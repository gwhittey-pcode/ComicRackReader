BugReporter
-----------

Экран для визуализации текста ошибки выполнения программы.

<img src="https://raw.githubusercontent.com/HeaTTheatR/KivyBugReporter/master/Screenshot.png" 
align="center"/>

Приложение написанно с использованием фреймворка для  кроссплатформенной разработки <Kivy>.
Информация о фреймворке <Kivy> доступна по ссылке http://kivy.org

ЯЗЫК ПРОГРАММИРОВАНИЯ
---------------------
Python 2.7 +

ЗАВИСИМОСТИ
-----------
Фреймворк [Kivy](http://kivy.org/docs/installation/installation.html)

Библиотека [KivyMD](https://gitlab.com/kivymd/KivyMD)

ПРИМЕР ИСПОЛЬЗОВАНИЯ
--------------------

Чтобы вы не гадали, почему ваше приложение написанное с использованием фреймворка Kivy, вдруг молча закрылось,
в процессе использования, или при старте, используйте нижеследующий код в своём файле main.py:

```python
# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2017 Easy

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

# Точка входа в приложение. Запускает основной программный код program.py.
# В случае ошибки, выводит на экран окно с её текстом.

import os
import sys
import traceback

# Никнейм и имя репозитория на github,
# куда будет отправлен отчёт баг репорта.
NICK_NAME_AND_NAME_REPOSITORY = 'NameAutos/NameRepository'

directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.dont_write_bytecode = True

try:
    import webbrowser
    try:
        import six.moves.urllib
    except ImportError:
        pass

    import kivy
    kivy.require('1.9.2')

    from kivy.config import Config
    Config.set('kivy', 'keyboard_mode', 'system')

    # Activity баг репорта.
    from bugreporter import BugReporter
except Exception:
    traceback.print_exc(file=open(os.path.join(directory, 'error.log'), 'w'))
    sys.exit(1)


__version__ = '0.0.1'


def main():
    app = None

    try:
        from program import Program  # основной класс программы

        # Запуск приложения.
        app = Program()
        app.run()
    except Exception:
    	from kivy.app import App
    	from kivy.uix.boxlayout import BoxLayout


        text_error = traceback.format_exc()
        traceback.print_exc(file=open(os.path.join(directory, 'error.log'), 'w'))

        if app:
            try:
                app.stop()
            except AttributeError:
                app = None

        def callback_report(*args):
            '''Функция отправки баг-репорта.'''

            try:
                txt = six.moves.urllib.parse.quote(
                    report.txt_traceback.text.encode('utf-8')
                )
                url = 'https://github.com/%s/issues/new?body=' + txt % NICK_NAME_AND_NAME_REPOSITORY
                webbrowser.open(url)
            except Exception:
                sys.exit(1)

        report = BugReporter(
            callback_report=callback_report, txt_report=text_error,
            icon_background='icon.png'
        )

        if app:
            app.screen.clear_widgets()
            app.screen.add_widget(report)
        else:
            class _App(App):
         	       def build(self):
         	           box = BoxLayout()
         	           box.add_widget(report)
         	           return box
         	   app = _App()
        app.run()


if __name__ in ('__main__', '__android__'):
    main()
```

ЛИЦЕНЗИЯ
--------
MIT

