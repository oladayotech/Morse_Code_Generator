from django.shortcuts import render
from django.http import JsonResponse

import json
from . import Morse_code_generator
# from Morse_code_generator import input_validation

# Create your views here.
def home(request):
    try:
        if request.method == 'POST':
            userinput = request.POST['userinput']
            action = 'etm'
            generated_morse_code = Morse_code_generator.input_validation(action, userinput)
        return render(request, 'index.html', {'contents':generated_morse_code})
    except Exception as e:
        return render(request, 'index.html', {'content':e})
        
def mte(request):
    try:
        if request.method == 'POST':
            userinput = request.POST['userinputmte']
            action = 'mte'
            generated_morse_code = Morse_code_generator.input_validation(action, userinput)
        return render(request, 'mte.html', {'contents':generated_morse_code, 'context':userinput})
    except Exception as e:
        return render(request, 'mte.html', {'content':e})