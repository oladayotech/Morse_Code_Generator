import time

morse_code_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..',

    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 'f': '..-.', 
    'g': '--.', 'h': '....', 'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..', 
    'm': '--', 'n': '-.', 'o': '---', 'p': '.--.', 'q': '--.-', 'r': '.-.', 
    's': '...', 't': '-', 'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 
    'y': '-.--', 'z': '--..',
    
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', 
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.', '!': '-.-.--', 
    '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...', ':': '---...', 
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-', 
    '\"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
}

def type_text(text, delay=0.04):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def action_selection():
    type_text("""Type ETM to Covert English to Morse Code
Type MTE to Covert Morse Code to English
        """)
    
    while True:
        try:
            user_input_action_selection = input("").strip().lower()
            if user_input_action_selection == "mte":
                user_input_mte = input("Enter Something in Morse code to convert to English: ").split(" ")
                return user_input_action_selection, user_input_mte
            elif user_input_action_selection == "etm":
                user_input_etm = input("Enter Something in English to convert to Morse code: ")
                return user_input_action_selection, user_input_etm
            else:
                type_text("Please select one of the above")
        except Exception as e:
            print("e")
    
def input_validation(action, user_input):
    if action == "mte":
        generated_sentence = []
        for values_in_user_input in user_input:
            for key, value in morse_code_dict.items():
                if value == values_in_user_input:
                    generated_sentence.append(key)
                    break
        return generated_sentence
                        
    elif action == "etm":
        generated_morse_code = []
        for values in user_input:
            generated_morse_code.append(morse_code_dict[values])
        return generated_morse_code
            # print(morse_code_dict[values], end=" ")
    
def main():
    action, user_input = action_selection()
    generated_code = input_validation(action, user_input)
    for morse_code in generated_code:
        print(morse_code, end=" ")
    
if __name__ == "__main__":
    while True:
        main()

        play_again = input("\nDo you want to play again (yes/no): ")

        if play_again.lower() != "yes":
            type_text("Thanks for playing")
            break