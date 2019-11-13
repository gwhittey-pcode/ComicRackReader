# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

#
# LICENSE: MIT

# Entry point to the application. Runs the main program.py program code.
# In case of error, displays a window with its text.

import os
import sys
import traceback

NICK_NAME_AND_NAME_REPOSITORY = (
    "git@github.com:gwhittey-pcode/ComicRackReader.git"
)

directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(directory, "libs/applibs"))

try:
    import webbrowser
    import kivy

    kivy.require("1.11.1")

    from kivy.config import Config

    # Config.set('kivy', 'keyboard_mode', 'system')
    Config.set("kivy", "log_enable", 0)

    from kivymd.theming import ThemeManager
    from kivymd.app import MDApp
    from libs.applibs.bugreporter import BugReporter
except Exception:
    traceback.print_exc(file=open(os.path.join(directory, "error.log"), "w"))
    print(traceback.print_exc())
    sys.exit(1)


__version__ = "1.0RC1"


def main():
    def create_error_monitor():
        class _App(MDApp):
            def build(self):
                box = BoxLayout()
                box.add_widget(report)
                return box

        app = _App()
        app.run()

    app = None
    from comicrackreader import ComicRackReader

    app = ComicRackReader()
    app.run()


if __name__ in ("__main__", "__android__"):
    main()
