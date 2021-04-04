import time

from services import YahooMail
from settings import setup, count_letters
from functions import (
    generate_letters,
    send_letters,
    check_letters,
    get_result_msg,
    delete_letters
)

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
