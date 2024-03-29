# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

#
# LICENSE: MIT

from kivy.properties import ObjectProperty

from kivymd.uix.navigationdrawer import MDNavigationLayout


class NavDrawer(MDNavigationLayout):
    _app = ObjectProperty()

    def _toggle(self):
        self.toggle_nav_drawer()

    def add_name_previous_screen(self):
        name_current_screen = self._app.manager.current
        if self.state == 'open':
            try:
                if self._app.list_previous_screens[-1] == name_current_screen:
                    return
            except IndexError:
                pass
            self._app.list_previous_screens.append(name_current_screen)
