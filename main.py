# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
# 
# LICENSE: MIT

# Entry point to the application. Runs the main program.py program code.
# In case of error, displays a window with its text.

import os
import sys
import traceback

NICK_NAME_AND_NAME_REPOSITORY = 'git@github.com:gwhittey-pcode/ComicRackReader.git'

directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(directory, 'libs/applibs'))

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
    Config.set('kivy', 'log_enable', 0)

    from kivymd.theming import ThemeManager
    from bugreporter import BugReporter
except Exception:
    traceback.print_exc(file=open(os.path.join(directory, 'error.log'), 'w'))
    print(traceback.print_exc())
    sys.exit(1)


__version__ = '.3'


def main():
    def create_error_monitor():
        class _App(App):
            theme_cls = ThemeManager()
            theme_cls.primary_palette = 'BlueGray'

            def build(self):
                box = BoxLayout()
                box.add_widget(report)
                return box
        app = _App()
        app.run()

    app = None

    try:
        from comicrackreader import ComicRackReader

        app = ComicRackReader()
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
            '''The function to send a bug report.'''

            try:
                txt = six.moves.urllib.parse.quote(
                    report.txt_traceback.text.encode('utf-8')
                )
                url = 'https://github.com/%s/issues/new?body=' % NICK_NAME_AND_NAME_REPOSITORY + txt
                webbrowser.open(url)
            except Exception:
                sys.exit(1)

        report = BugReporter(
            callback_report=callback_report, txt_report=text_error,
            icon_background=os.path.join('data', 'images', 'icon.png')
        )

        if app:
            try:
                app.screen.clear_widgets()
                app.screen.add_widget(report)
            except AttributeError:
            	create_error_monitor()
        else:
            create_error_monitor()


if __name__ in ('__main__', '__android__'):
    main()
