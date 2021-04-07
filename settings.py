# -*- coding: utf-8 -*-

from string import (
    ascii_uppercase as upper,
    ascii_lowercase as lower,
    digits
)

setup = {
    'email': '',
    'password': ''
}
length_theme = 10
length_msg = 10
count_letters = 5
lower = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
upper = lower.upper()
symbols = list(u'{}{}{}'.format(upper, lower, digits))
