from random import randint
from string import (
    ascii_uppercase as upper,
    ascii_lowercase as lower,
    digits
)

from settings import setup

length_theme = 10
length_msg = 10
count_letters = 15
symbols = list('{}{}{}'.format(upper, lower, digits))

def get_random_text(length):
    flag_digit, flag_char, txt = False, False, ''
    while True:
        for _ in range(length):
            char = symbols[randint(0, len(symbols)-1)]
            if char.isdecimal():
                flag_digit = True
            elif char.isalpha():
                flag_char = True
            txt += char
        if flag_digit and flag_char:
            return txt
        flag_digit, flag_char, txt = False, False, ''

def get_count_char_and_digit(txt):
    cnt_digits = cnt_chars = 0
    for symbol in txt:
        if symbol.isdecimal():
            cnt_digits += 1
        elif symbol.isalpha():
            cnt_chars += 1
    return cnt_digits, cnt_chars

def get_result_msg(letters):
    result_msg = ''
    fmt = '{i}. Received mail on theme {theme} with message: {msg}. It ' \
        'contains {cnt_chars} letters and {cnt_digits} numbers.\n'
    for i, letter in enumerate(letters.items(), 1):
        theme, msg = letter
        cnt_digits, cnt_chars = get_count_char_and_digit(msg)
        result_msg += fmt.format(
            theme=theme, msg=msg, i=i,
            cnt_chars=cnt_chars, cnt_digits=cnt_digits
        )
    return result_msg

def get_letters(count_letters):
    letters = {}
    for _ in range(count_letters):
        theme = get_random_text(length_theme)
        msg = get_random_text(length_msg)
        letters[theme] = msg
    return letters

def main():
    letters = get_letters(count_letters)
    print(get_result_msg(letters))

if __name__ == '__main__':
    main()
