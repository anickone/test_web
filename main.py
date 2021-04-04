from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
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

class BaseMail(object):
    def __init__(self, timeout=4):
        self.timeout = timeout
        self.start()

    def start(self):
        self.browser = webdriver.Chrome()

    def open(self, url):
        self.browser.get(url)

    def stop(self):
        self.browser.quit()

    def is_element_present(self, how, what, timeout=4):
        try:
            WebDriverWait(self.browser, timeout
                ).until(EC.presence_of_element_located(
                    (how, what)
                )
            )
        except TimeoutException:
            return False
        return True

    def is_element_interactable(self, how, what, timeout=4):
        try:
            WebDriverWait(self.browser, timeout
                ).until(EC.element_to_be_clickable(
                    (how, what)
                )
            )
        except TimeoutException:
            return False
        return True

    def check_element(self, how, what, timeout=4):
        return self.is_element_present(how, what, timeout) and \
                self.is_element_interactable(how, what, timeout)

    def get_element(self, how, what, timeout=4):
        if self.check_element(how, what, timeout):
            return self.browser.find_element(how, what)
        print('Element "{}" is not available.'.format(what))
        # self.stop()

    def click(self, what, how=By.XPATH):
        el = self.get_element(how, what)
        el.click()

    def send_text(self, text, what, how=By.XPATH):
        el = self.get_element(how, what)
        el.send_keys(text)

    def get_text(self, what, how=By.XPATH):
        el = self.get_element(how, what)
        return el.text

class YahooMail(BaseMail):
    def __init__(self, timeout=4):
        super(YahooMail, self).__init__(timeout)
        # login selectors
        self.login_url = 'https://login.yahoo.com/'
        self.email_input = '//input[@name="username"]'
        self.email_btn = '//input[@type="submit"]'
        self.password_input = '//input[@type="password"]'
        self.password_btn = '//button[@type="submit"]'
        self.mail_box_url = 'https://mail.yahoo.com/'
        # logout selectors
        self.logout_url = 'https://login.yahoo.com/account/logout'
        self.logout_btn = '//input[@data-logout="yes"]'
        # send letter selectors
        self.new_letter = '//a[@data-test-id="compose-button"]'
        self.msg_to = '//input[@id="message-to-field"]'
        self.field_theme = '//input[@data-test-id="compose-subject"]'
        self.field_msg = '//div[@data-test-id="rte"]/div'
        self.send_btn = '//button[@data-test-id="compose-send-button"]/span'
        # check letter selectors
        self.letter_theme = '//span[@data-test-id="message-group-subject-text"]'
        self.letter_msg = '//div[@dir="ltr"]'
        self.back_to_list = '//button[@data-test-id="toolbar-back-to-list"]'
        self.letter_selector = '(//a[@role="row"])[{}]'.format
        self.letter_delete = '//button[@data-test-id="toolbar-delete"]'
        # check inbox
        self.inbox_link = '//a[@data-test-folder-name="Inbox"]'
        self.unread_letters = 'data-test-unread-count'

    def login(self):
        # open mail login url
        self.open(self.login_url)
        # input email and click btn
        self.send_text(setup['email'], self.email_input)
        self.click(self.email_btn)
        # input password and click btn
        self.send_text(setup['password'], self.password_input)
        self.click(self.password_btn)
        # redirect from index page to mail box
        self.open(self.mail_box_url)

    def logout(self):
        self.open(self.logout_url)
        self.click(self.logout_btn)

    def read_letter(self, this_letter):
        # open letter
        self.click(this_letter)
        # read theme
        theme = self.get_text(self.letter_theme)
        # read msg
        msg = self.get_text(self.letter_msg)
        # back to list letters
        self.click(self.back_to_list)
        return theme, msg

    def send_letter(self, to_email, theme, msg):
        # open compose letter app
        self.click(self.new_letter)
        # field msg to email
        self.send_text(to_email, self.msg_to)
        # field theme
        self.send_text(theme, self.field_theme)
        # field msg
        self.send_text(msg, self.field_msg)
        # send letter
        self.click(self.send_btn)

    def delete_letter(self, this_letter):
        # open letter
        self.click(this_letter)
        # delete
        self.click(self.letter_delete)

    def check_new_letters_inbox(self):
        # check new letter
        self.click(self.inbox_link)
        a = self.get_element(By.XPATH, self.inbox_link, timeout=4)
        try:
            unread_cnt_letters = int(a.get_attribute(self.unread_letters))
        except ValueError:
            unread_cnt_letters = 0
            err = 'Change behavior attribute inbox "{}".'
            print(err.format(self.unread_letters))
        return unread_cnt_letters

def isdecimal(char):
    return char in '0123456789'

def get_random_text(length):
    flag_digit, flag_char, txt = False, False, ''
    while True:
        for _ in range(length):
            char = symbols[randint(0, len(symbols)-1)]
            if isdecimal(char):
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
        if isdecimal(symbol):
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

def generate_letters(count_letters):
    letters = {}
    for _ in range(count_letters):
        theme = get_random_text(length_theme)
        msg = get_random_text(length_msg)
        letters[theme] = msg
    return letters

def send_letters(service, letters):
    for theme, msg in letters.items():
        service.send_letter(setup['email'], theme, msg)

def check_letters(service, letters):
    check = set(letters)
    read_letters = {}
    i = 0
    while check:
        i += 1
        selector = service.letter_selector(i)
        if service.check_element(By.XPATH, selector):
            theme, msg = service.read_letter(selector)
            if theme in check:
                check.remove(theme)
                read_letters[theme] = msg
        else:
            print('not found letters:', check)
            break
    else:
        print('all letters found')
    return read_letters

def delete_letters(service, letters, delete_all=False, save_letters=[]):
    """
    If delete_all=True all letters are deleted, except save_letters.
    If delete_all=False all that were sent are deleted.
    """
    check = set(letters)
    i = 1
    while check or delete_all:
        selector = service.letter_selector(i)
        if service.check_element(By.XPATH, selector):
            theme, _ = service.read_letter(selector)
            if theme in save_letters:
                i += 1
                continue
            elif theme in check:
                check.remove(theme)
                service.delete_letter(selector)
            elif delete_all:
                service.delete_letter(selector)
            else:
                i += 1
        else:
            if delete_all:
                print('all not save letters deleted')
            else:
                print('not deleted letters because not found:', check)
            break
    else:
        print('all sent letters deleted')

def main():
    # enter to mail box
    service = YahooMail()
    service.login()

    unread_letters = service.check_new_letters_inbox()
    # send letters
    letters = generate_letters(count_letters)
    send_letters(service, letters)

    # wait for letters ~ 2-3 minutes
    for _ in range(60):
        time.sleep(15)
        new = service.check_new_letters_inbox() - unread_letters
        print('Received {}.'.format(new))
        if new >= count_letters:
            break

    # check letters
    read_letters = check_letters(service, letters)

    # send result msg
    result_msg = get_result_msg(read_letters)
    service.send_letter(setup['email'], 'result', result_msg)

    # delete letters past result msg
    delete_letters(service, letters)

    # delete all not saved letters
    # delete_letters(service, [], delete_all=True, save_letters=['result'])

    service.logout()
    service.stop()

if __name__ == '__main__':
    main()
