# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

#
# LICENSE: MIT

import webbrowser

from kivy.uix.screenmanager import Screen


class About(Screen):
    def open_url(self, instance, url):
        webbrowser.open(url)
