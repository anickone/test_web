1. Залогиниться в почту (любую).
2. Отправить самому себе на эту же почту 15 писем, в которых сообщение - рандомная строка, содержащая 10 символов (буквы и цифры), тема - рандомная строка, содержащая 10 символов (буквы и цифры).
3. Проверить что все 15 писем доставлены.
4. Собрать текст сообщений с главной страницы почтового ящика, сохранить их в дикт, где ключ - тема письма, значение - текст сообщения.
5. Полученную информацию отправить себе же в одном сообщении в таком виде: "Received mail on theme {тема письма} with message: {текст письма}. It contains {кол-во букв в письме} letters and {кол-во цифр в письме} numbers". Важно - значение должно вычисляться исходя из данных в дикте, не браться из памяти. В таком формате должны быть перечислены все полученные сообщения.
6. Удалить все полученные письма, кроме последнего.

В работе использовать Python 2.7 + Selenium.

## Description
It work on Python 2.7 or 3.

## Requirements
Python 2.7 or 3
Selenium

## Install
for Python 2.7
virtualenv -p /usr/bin/python2.7 virtualenv_name
source virtualenv_name/bin/activate

or for Python 3
virtualenv -p /usr/bin/python3 virtualenv_name
source virtualenv_name/bin/activate

pip install selenium

git clone https://github.com/anickone/test_web.git
add your email and password in settings.py
cd test_web
python main.py
