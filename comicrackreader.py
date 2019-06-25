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

import os
import sys
from ast import literal_eval

from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ListProperty

from main import __version__
from libs.translation import Translation
from libs.uix.baseclass.startscreen import StartScreen
from libs.uix.lists import Lists

from kivymd.theming import ThemeManager
from kivymd.label import MDLabel
from kivymd.toast import toast

# from dialogs import card
# End KivyMD imports
from settings.settingsjson import settings_json_server, settings_json_dispaly,\
    settings_json_screen_tap_control
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.settings import SettingsWithSidebar


class ComicRackReader(App):
    title = 'ComicRackReader'
    icon = 'icon.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Amber'
    lang = StringProperty('en')
    open_comics_list = ListProperty()

    def __init__(self, **kvargs):
        super(ComicRackReader, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = 'below_target'

        self.list_previous_screens = ['base']
        self.window = Window
        self.config = ConfigParser()
        self.manager = None
        self.window_language = None
        self.exit_interval = False
        self.dict_language = literal_eval(
            open(
                os.path.join(self.directory, 'data', 'locales',
                             'locales.txt')).read()
        )
        # self.translation = Translation(
        #     self.lang, 'Ttest', os.path.join(self.directory,
        # data', 'locales')
        # )
        self.base_url = ''
        self.settings_cls = SettingsWithSidebar

    def get_application_config(self):
        return super(ComicRackReader, self).get_application_config(
            '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        '''Creates an application settings file ComicRackReader.ini.'''

        config.adddefaultsection('General')
        config.setdefault('General', 'language', 'en')
        config.setdefaults('Server', {
            'url':          'http://',
            'storagedir':       self.user_data_dir,
            'max_height':       0,
            'use_api_key':      0,
            'api_key':          '',
            'username':         '',
            'password':         '',
            # 'use_pagination':   '1',
            'max_books_page':   50
        })

        config.setdefaults('Display', {
            'mag_glass_size':   200,
            'right2left':       0,
            'dblpagesplit':     '0',
            'stretch_image':    '0',
            'keep_ratio':       '0',
            'reading_list_icon_size': 'Medium',
            'max_comic_pages_limit':   50,
        })

        config.setdefaults('Screen Tap Control', {
            'bottom_right':     'Next Page',
            'bottom_left':      'Prev Page',
            'bottom_center':    'Open Page Nav',
            'top_right':        'Return to Home Screen',
            'top_left':         'Precodv Page',
            'top_center':       'Open Collection Browser',
            'middle_right':     '',
            'middle_left':      '',
            'middle_center':    'Open Options Popup',
            'dbl_tap_time':      250,
        })

    def set_value_from_config(self):
        '''Sets the values of variables from the settings
        file ComicRackReader.ini.'''

        self.config.read(os.path.join(self.directory, 'comicrackreader.ini'))
        self.lang = self.config.get('General', 'language')

    def build(self):
        self.base_url = self.config.get('Server', 'url')
        self.api_url = self.base_url + "/BCR"
        self.api_key = self.config.get('Server', 'api_key')
        self.set_value_from_config()
        self.load_all_kv_files(os.path.join(
            self.directory, 'libs', 'uix', 'kv'))
        self.screen = StartScreen()  # program main screen
        self.manager = self.screen.ids.manager
        self.nav_drawer = self.screen.ids.nav_drawer

        return self.screen

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            kv_file = os.path.join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                with open(kv_file, encoding='utf-8') as kv:
                    Builder.load_string(kv.read())

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        '''Called when you press the Menu button or Back Key'''
        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.toggle_nav_drawer()
            self.back_screen(event=keyboard)
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self, event=None):
        '''Screen manager Called when the Back Key is pressed.'''
        # BackKey pressed.
        if event in (1001, 27):
            if self.manager.current == 'base':
                self.dialog_exit()
                return
            try:
                self.manager.current = self.list_previous_screens.pop()
            except:
                self.manager.current = 'base'
            # self.screen.ids.action_bar.title = self.title
            self.screen.ids.action_bar.left_action_items = \
                [['menu', lambda x: self.nav_drawer._toggle()]]

    def show_about(self, *args):
        self.nav_drawer.toggle_nav_drawer()
        self.screen.ids.about.ids.label.text = \
            _(
                u'[size=20][b]ComicRackReader[/b][/size]\n\n'
                u'[b]Version:[/b] {version}\n'
                u'[b]License:[/b] MIT\n\n'
                u'[size=20][b]Developer[/b][/size]\n\n'
                u'[ref=SITE_PROJECT]'
                u'[color={link_color}]Gerard Whittey[/color][/ref]\n\n'
                u'[b]Source code:[/b] '
                u'[ref=git@github-pcode:gwhittey-pcode/ComicRackReader.git]'
                u'[color={link_color}]GitHub[/color][/ref]').format(
                version=__version__,
                link_color=get_hex_from_color(self.theme_cls.primary_color)
            )
        self.manager.current = 'about'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]

    def show_license(self, *args):
        self.screen.ids.license.ids.text_license.text = \
            ('%s') % open(
                os.path.join(self.directory, 'LICENSE'),
                encoding='utf-8').read()

        self.nav_drawer._toggle()
        self.manager.current = 'license'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen(27)]]
        self.screen.ids.action_bar.title = 'MIT LICENSE'

    def select_locale(self, *args):
        '''Displays a window with a list of available language localizations'''

        def select_locale(name_locale):
            '''Sets the selected location..'''

            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang = locale
                    self.config.set('General', 'language', self.lang)
                    self.config.write()

        dict_info_locales = {}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]] = \
                ['locale', locale == self.lang]

        # if not self.window_language:
        #     self.window_language = card(
        #         Lists(
        #             dict_items=dict_info_locales,
        #             events_callback=select_locale, flag='one_select_check'
        #         ),
        #         size=(.85, .55)
        #     )
        # self.window_language.open()

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)

        Clock.schedule_interval(check_interval_press, 1)
        toast('Press Back to Exit')

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def build_settings(self, settings):
        settings.add_json_panel('General Settings',
                                self.config,
                                data=settings_json_server)
        settings.add_json_panel('Display Settings',
                                self.config,
                                data=settings_json_dispaly)
        settings.add_json_panel('Screen Tap Control',
                                self.config,
                                data=settings_json_screen_tap_control)

    def on_config_change(self, config, section,
                         key, value):
        if key == 'url':
            self.base_url = self.config.get('Server', 'url')
        if key == 'api_key':
            self.api_key = self.config.get('Server', 'api_key')
        if key == 'dbl_tap_time':
            self.Config.set('postproc', 'double_tap_time', value)

    def switch_lists_screen(self):
        self.manager.current = 'comicracklistscreen'
        comicracklistscreen = self.manager.get_screen('comicracklistscreen')

    def switch_open_comics_screen(self):
        self.manager.current = 'open_comicscreen'

    def switch_readinglists_screen_switch(self):
        self.manager.current = 'readinglistscreen'

    def switch_base_screen_switch(self):
        self.set_screen("Home Screen")
        self.manager.current = 'base'

    def set_screen(self, title):
        self.screen.ids.action_bar.title = title

    def hide_action_bar(self):
        self.screen.ids.action_bar.opacity = 0
        self.screen.ids.action_bar.disabled = True
        self.screen.ids.action_bar.size_hint_y = None
        self.screen.ids.action_bar.size = (0, 0)

    def show_action_bar(self):
        self.screen.ids.action_bar.opacity = 1
        self.screen.ids.action_bar.disabled = False
        self.screen.ids.action_bar.size = (
            Window.width, self.theme_cls.standard_increment)
