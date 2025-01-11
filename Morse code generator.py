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
    '\"': '.-..-.', '$': '...-..-', ' ': ' ' #' ': '/', '@': '.--.-.'
}

def type_text(text, delay=0.04):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

while True:
    def action_selection():
        type_text("""Type ETM to Covert English to Morse Code""")
    
        while True:
            try:
                user_input = input("\n").strip().lower()
                if user_input == "etm":
                    return user_input
                else:
                    print("Please select one of the above")
            except Exception as e:
                print("e")
    
    def input_validation():
        action = action_selection()
        if action == "etm":
            user_input = input("Enter Something in English to convert to Morse code")
            # user_input = user_input.split(" ")
            print(user_input)
            for values in user_input:
                print(morse_code_dict[values], end=" ")
    
    def main():
        # action_selection()
        input_validation()
    
    if __name__ == "__main__":
        main()

    play_again = input("Do you want to play again (yes/no): ")

    if play_again.lower() != "yes":
        print("Thanks for playing")
        break