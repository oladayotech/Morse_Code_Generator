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
        return render(request, 'index.html', {'contents':generated_morse_code, 'contest':userinput})
    except Exception as e:
        return render(request, 'index.html', {'content':e})
        
# def mte(request):
#     try:
#         if request.method == 'POST':
#             userinput = request.POST['userinputmte']
#             action = 'mte'
#             generated_morse_code = Morse_code_generator.input_validation(action, userinput)
#         return render(request, 'mte.html', {'contents':generated_morse_code, 'context':userinput})
#     except Exception as e:
#         return render(request, 'mte.html', {'content':e})

def mte(request):
    try:
        # Check if the request method is POST
        if request.method == 'POST':
            userinput = request.POST['userinputmte']
            print(userinput)
            action = 'mte'
            # Call the function to convert Morse code to English
            generated_morse_code = Morse_code_generator.input_validation(action, userinput)
            print(f"Generated English Output: {generated_morse_code}")
            # Render the result with the generated Morse code and original input
        return render(request, 'mte.html', {'contents': generated_morse_code, 'context': userinput})
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        # Handle exceptions and return the error message
        return render(request, 'mte.html', {'content': str(e)})