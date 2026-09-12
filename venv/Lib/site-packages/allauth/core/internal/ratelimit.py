"""
from __future__ import annotations

Rate limiting in this implementation relies on a cache and uses non-atomic
operations, making it vulnerable to race conditions. As a result, users may
occasionally bypass the intended rate limit due to concurrent access. However,
such race conditions are rare in practice. For example, if the limit is set to
10 requests per minute and a large number of parallel processes attempt to test
that limit, you may occasionally observe slight overruns—such as 11 or 12
requests slipping through. Nevertheless, exceeding the limit by a large margin
is highly unlikely due to the low probability of many processes entering the
critical non-atomic code section simultaneously.
"""

import hashlib
import ipaddress
import time
from collections import namedtuple
from dataclasses import dataclass
from http import HTTPStatus

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist

from allauth.core.exceptions import RateLimited


Rate = namedtuple("Rate", "amount duration per")


@dataclass
class SingleRateLimitUsage:
    cache_key: str
    cache_duration: float | int
    timestamp: float

    def rollback(self) -> None:
        history = cache.get(self.cache_key, [])
        history = [ts for ts in history if ts != self.timestamp]
        cache.set(self.cache_key, history, self.cache_duration)


@dataclass
class RateLimitUsage:
    usage: list[SingleRateLimitUsage]

    def rollback(self) -> None:
        for usage in self.usage:
            usage.rollback()


def parse_duration(duration) -> int | float:
    if len(duration) == 0:
        raise ValueError(duration)
    unit = duration[-1]
    value = duration[0:-1]
    unit_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in unit_map:
        raise ValueError(f"Invalid duration unit: {unit}")
    if len(value) == 0:
        value = 1
    else:
        value = float(value)
    return value * unit_map[unit]


def parse_rate(rate: str) -> Rate:
    parts = rate.split("/")
    if len(parts) == 2:
        amount, duration = parts
        per = "ip"
    elif len(parts) == 3:
        amount, duration, per = parts
    else:
        raise ValueError(rate)
    amount_v = int(amount)
    duration_v = parse_duration(duration)
    return Rate(amount_v, duration_v, per)


def parse_rates(rates: str | None) -> list[Rate]:
    ret = []
    if rates:
        rates = rates.strip()
        if rates:
            parts = rates.split(",")
            for part in parts:
                ret.append(parse_rate(part.strip()))
    return ret


def truncate_ip(ip: str) -> str:
    from allauth import app_settings as allauth_settings

    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip

    if isinstance(addr, ipaddress.IPv6Address):
        prefix = allauth_settings.RATE_LIMIT_IPV6_PREFIX
        network = ipaddress.IPv6Network(f"{addr}/{prefix}", strict=False)
        return str(network.network_address)
    return ip


def get_ip(request: HttpRequest) -> str:
    from allauth.account.adapter import get_adapter

    ip = get_adapter().get_client_ip(request)
    return truncate_ip(ip)


def get_cache_key(
    request: HttpRequest, *, action: str, rate: Rate, key=None, user=None
) -> str:
    source: tuple[str, ...]
    if rate.per == "ip":
        source = ("ip", get_ip(request))
    elif rate.per == "user":
        if user is None:
            if not request.user.is_authenticated:
                raise ImproperlyConfigured(
                    "ratelimit configured per user but used anonymously"
                )
            user = request.user
        source = ("user", str(user.pk))
    elif rate.per == "key":
        if key is None:
            raise ImproperlyConfigured(
                "ratelimit configured per key but no key specified"
            )
        key_hash = hashlib.sha256(key.encode("utf8")).hexdigest()
        source = (key_hash,)
    else:
        raise ValueError(rate.per)
    keys = ["allauth", "rl", action, *source]
    return ":".join(keys)


def apply_rate(
    history: list[float], now: float, rate: Rate, *, dry_run: bool = False
) -> tuple[bool, list[float]]:
    """Apply ``rate`` to the hit timestamps at ``now``, returning
    ``(allowed, history)``: expired timestamps are dropped and, unless
    ``dry_run``, an allowed hit is recorded. I/O-free, so needs no cache.
    """
    while history and history[-1] <= now - rate.duration:
        history.pop()
    allowed = len(history) < rate.amount
    if allowed and not dry_run:
        history.insert(0, now)
    return allowed, history


def _consume_single_rate(
    request: HttpRequest,
    *,
    action: str,
    rate: Rate,
    key=None,
    user=None,
    dry_run: bool = False,
    raise_exception: bool = False,
) -> SingleRateLimitUsage | None:
    cache_key = get_cache_key(request, action=action, rate=rate, key=key, user=user)
    history = cache.get(cache_key, [])
    now = time.time()
    allowed, history = apply_rate(history, now, rate, dry_run=dry_run)
    if allowed:
        usage = SingleRateLimitUsage(
            cache_key=cache_key, timestamp=now, cache_duration=rate.duration
        )
        if not dry_run:
            cache.set(cache_key, history, rate.duration)
    else:
        usage = None
        if raise_exception:
            raise RateLimited
    return usage


def consume(
    request: HttpRequest,
    *,
    action: str,
    config: dict[str, str],
    key=None,
    user=None,
    dry_run: bool = False,
    limit_get: bool = False,
    raise_exception: bool = False,
) -> RateLimitUsage | None:
    usage = RateLimitUsage(usage=[])
    if (not limit_get) and request.method == "GET":
        return usage
    rates = parse_rates(config.get(action))
    if not rates:
        return usage
    allowed = True
    for rate in rates:
        single_usage = _consume_single_rate(
            request,
            action=action,
            rate=rate,
            key=key,
            user=user,
            dry_run=dry_run,
            raise_exception=raise_exception,
        )
        if not single_usage:
            allowed = False
            break
        usage.usage.append(single_usage)
    return usage if allowed else None


def handler429(request: HttpRequest) -> HttpResponse:
    from allauth.account import app_settings

    try:
        return render(
            request,
            f"429.{app_settings.TEMPLATE_EXTENSION}",
            status=HTTPStatus.TOO_MANY_REQUESTS,
        )
    except TemplateDoesNotExist:
        content = """<html>
    <head><title>Too Many Requests</title></head>
    <body>
        <h1>429 Too Many Requests</h1>
        <p>You have sent too many requests. Please try again later.</p>
    </body>
</html>"""
        return HttpResponse(
            content=content,
            content_type="text/html",
            status=HTTPStatus.TOO_MANY_REQUESTS,
        )


def clear(
    request: HttpRequest, *, config: dict, action: str, key=None, user=None
) -> None:
    rates = parse_rates(config.get(action))
    for rate in rates:
        cache_key = get_cache_key(request, action=action, rate=rate, key=key, user=user)
        cache.delete(cache_key)
