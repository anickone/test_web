import time

from services import YahooMail, GMail
from settings import setup, count_letters
from functions import generate_letters, get_result_msg

def main():
    # enter to mail box
    # service = YahooMail()
    service = GMail(timeout=15)
    service.login()
    service.open_mail_box()
    # '''
    unread_letters = service.check_new_letters_inbox()
    # send letters
    letters = generate_letters(count_letters)
    service.send_letters(setup['email'], letters)

    service.wait_for_letters(
        5,
        count_letters=count_letters,
        unread_letters=unread_letters
    )

    # check letters
    read_letters = service.check_letters(letters)

    # send result msg
    result_msg = get_result_msg(read_letters)
    service.send_letter(setup['email'], 'result', result_msg)

    # delete letters past result msg
    service.delete_letters(letters)

    # delete all not saved letters
    # service.delete_letters([], delete_all=True, save_letters=['result'])

    service.logout()
    service.stop()

if __name__ == '__main__':
    main()
