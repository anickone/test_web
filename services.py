from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
import time

from settings import setup

class BaseMail(object):
    def __init__(self, timeout=4, attempts=5):
        self.timeout = timeout
        self.attempts = attempts
        self.start()

    def start(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(self.timeout)

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
        for attempt in range(self.attempts):
            if self.check_element(how, what, timeout):
                return self.browser.find_element(how, what)
            print('Attempt: {}. Element "{}" is not available.'.format(attempt, what))
            time.sleep(timeout)
        print('Critical error.')
        self.logout()
        self.stop()

    def click(self, what, how=By.XPATH):
        el = self.get_element(how, what)
        el.click()

    def send_text(self, text, what, how=By.XPATH):
        el = self.get_element(how, what)
        el.send_keys(text)

    def get_text(self, what, how=By.XPATH):
        el = self.get_element(how, what)
        return el.text

    def login(self):
        # open mail login url
        self.open(self.login_url)
        # input email and click btn
        self.send_text(setup['email'], self.email_input)
        self.click(self.email_btn)
        # input password and click btn
        self.send_text(setup['password'], self.password_input)
        self.click(self.password_btn)

    def open_mail_box(self):
        # redirect from index page to mail box
        self.open(self.mail_box_url)

    def logout(self):
        self.open(self.logout_url)

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

    def send_letters(self, to_email, letters):
        for theme, msg in letters.items():
            self.send_letter(to_email, theme, msg)

    def check_letters(self, letters):
        check = set(letters)
        read_letters = {}
        i = 0
        while check:
            i += 1
            selector = self.letter_selector(i)
            if self.check_element(By.XPATH, selector):
                theme, msg = self.read_letter(selector)
                if theme in check:
                    check.remove(theme)
                    read_letters[theme] = msg
            else:
                print('not found letters:', check)
                break
        else:
            print('all letters found')
        return read_letters

    def delete_letters(self, letters, delete_all=False, save_letters=[]):
        """
        If delete_all=True all letters are deleted, except save_letters.
        If delete_all=False all that were sent are deleted.
        """
        check = set(letters)
        i = 1
        while check or delete_all:
            selector = self.letter_selector(i)
            if self.check_element(By.XPATH, selector):
                theme, _ = self.read_letter(selector)
                if theme in save_letters:
                    i += 1
                elif theme in check:
                    check.remove(theme)
                    self.delete_letter(selector)
                elif delete_all:
                    self.delete_letter(selector)
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

    def wait_for_letters(self, sec, **kwargs):
        time.sleep(sec)

class GMail(BaseMail):
    def __init__(self, timeout=4):
        super(GMail, self).__init__(timeout)
        # login selectors
        self.login_url = 'https://accounts.google.com/'
        self.email_input = '//input[@type="email"]'
        self.email_btn = '//button[@jsaction]'
        self.password_input = '//input[@type="password"]'
        self.password_btn = '//div[@id="passwordNext"]//button'
        self.mail_box_url = 'https://mail.google.com/'
        # logout selectors
        self.logout_url = 'https://accounts.google.com/Logout'
        # send letter selectors
        self.new_letter = '//div[@gh="cm"]'
        self.msg_to = '//textarea[@role="combobox"]'
        self.field_theme = '//input[@name="subjectbox"]'
        self.field_msg = '//div[@role="textbox"]'
        self.send_btn = '//div[@data-tooltip-delay and @jslog]'
        self.close_msg = '//div[@aria-live="assertive"]//div[@role="button"]'
        # check letter selectors
        self.letter_theme = '//div/h2[@data-thread-perm-id]'
        self.letter_msg = '//div[@data-message-id]//div[@dir="ltr"]'
        self.back_to_list = '//div[@act="19"]/div'
        self.letter_selector = '//tr[@role="row"][{}]'.format
        self.letter_delete = '//div[@act="10" and @jslog]/div'
        # check inbox
        self.inbox_link = '//a[@href="https://mail.google.com/mail/u/0/#inbox"]'
        self.unread_letters = 'aria-label'

    def check_new_letters_inbox(self):
        # check new letter
        self.click(self.inbox_link)
        a = self.get_element(By.XPATH, self.inbox_link, timeout=4)
        txt = a.get_attribute(self.unread_letters)
        r = re.findall(r'\d+', txt)
        if r:
            unread_cnt_letters = int(r[0])
        else:
            unread_cnt_letters = 0
        return unread_cnt_letters

    def send_letter(self, to_email, theme, msg):
        super(GMail, self).send_letter(to_email, theme, msg)
        # close assertive msg
        time.sleep(5)
        # not work
        # self.click(self.close_msg)

    def open_mail_box(self):
        time.sleep(self.timeout)
        super(GMail, self).open_mail_box()

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

    def logout(self):
        super(YahooMail, self).logout()
        self.click(self.logout_btn)

    def wait_for_letters(self, sec, **kwargs):
        super(YahooMail, self).wait_for_letters(sec, **kwargs)
        if 'unread_letters' not in kwargs or 'count_letters' not in kwargs:
            return
        # wait for letters ~ 2-3 minutes
        for _ in range(60):
            time.sleep(15)
            new = self.check_new_letters_inbox() - kwargs['unread_letters']
            print('Received {}.'.format(new))
            if new >= kwargs['count_letters']:
                break
