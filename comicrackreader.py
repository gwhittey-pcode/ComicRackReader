# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
###
# LICENSE: MIT

import os
import sys
from ast import literal_eval
from kivy.config import Config

from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ListProperty

from main import __version__
from libs.translation import Translation
from libs.uix.baseclass.startscreen import StartScreen
from libs.uix.lists import Lists
from kivy.logger import Logger
from kivymd.theming import ThemeManager
from kivymd.label import MDLabel
from kivymd.toast import toast

# from dialogs import card
# End KivyMD imports
from settings.settingsjson import settings_json_server, settings_json_dispaly,\
    settings_json_screen_tap_control, settings_json_hotkeys
from kivy.properties import ObjectProperty, StringProperty
from settings.custom_settings import MySettings

SCREEN_LIST = ['base', 'license', 'about', 'readinglistscreen',
                        'comicracklistscreen', 'open_comicscreen']
class ComicRackReader(App):
    title = 'ComicRackReader Home Screen'
    icon = 'icon.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Amber'
    lang = StringProperty('en')
    open_comics_list = ListProperty()
    full_screen = False
    LIST_SCREENS = ListProperty()
    def __init__(self, **kvargs):
        super(ComicRackReader, self).__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = 'below_target'
        
        self.LIST_SCREENS = ['base', 'license', 'about', 'readinglistscreen',
        'comicracklistscreen', 'open_comicscreen']
        self.list_previous_screens = ['base']
        self.window = Window
        self.config = ConfigParser()
        self.manager = None
        self.window_language = None
        self.exit_interval = False
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
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
        self.settings_cls = MySettings

    # def get_application_config(self):
    #     return super(ComicRackReader, self).get_application_config(
    #         '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        '''Creates an application settings file ComicRackReader.ini.'''

        config.adddefaultsection('General')
        config.adddefaultsection('Saved')
        config.setdefault('General', 'language', 'en')
        config.setdefault('Saved', 'last_comic_id', '')
        config.setdefault('Saved', 'last_reading_list_id', '')
        config.setdefault('Saved', 'last_reading_list_name', '')
        config.setdefault('Saved', 'last_pag_pagnum', '')
        config.setdefaults('Server', {
            'url':          'http://',
            'storagedir':       self.user_data_dir,
            'max_height':       1500,
            'use_api_key':      0,
            'api_key':          '',
            'username':         '',
            'password':         '',
            # 'use_pagination':   '1',
            'max_books_page':   25
        })

        config.setdefaults('Display', {
            'mag_glass_size':   200,
            'right2left':       0,
            'dblpagesplit':     '0',
            'stretch_image':    '0',
            'keep_ratio':       '0',
            # 'comic_thumb_width': 200,
            # 'comic_thumb_height': 300,
            'reading_list_icon_size': 'Small',
            'max_comic_pages_limit':   50,
            'window_height'          : 800,
            'window_width'          : 600,
            
        })

        config.setdefaults('Screen Tap Control', {
            'bottom_right':     'Next Page',
            'bottom_left':      'Prev Page',
            'bottom_center':    'Open Page Nav',
            'top_right':        'Return to Home Screen',
            'top_left':         'Precodv Page',
            'top_center':       'Open Collection Browser',
            'middle_right':     'None',
            'middle_left':      'None',
            'middle_center':    'Open NavBar',
            'dbl_tap_time':      250,
        })

        config.setdefaults('Hotkeys', {
            'hk_next_page':           '.',
            'hk_prev_page':           ',',
            'hk_open_page_nav':       'p',
            'hk_open_collection':     'j',
            'hk_return_comic_list':   'c',
            'hk_return_base_screen': 'r',
            'hk_toggle_navbar':        'n',
            'hk_open_comicscreen':     'o',
            'hk_toggle_fullscreen':    'f',

        })

    def set_value_from_config(self):
        '''Sets the values of variables from the settings
        file ComicRackReader.ini.'''

        self.config.read(os.path.join(self.directory, 'comicrackreader.ini'))
        self.lang = self.config.get('General', 'language')

    def set_window_size(self):
        app = App.get_running_app()

        window_height = app.config.get('Display', 'window_height')
        window_width = app.config.get('Display', 'window_width')
        Window.size = (int(window_width),int(window_height))
        Window.top = dp(30)
        Window.left = dp(30)
        # Config.set('graphics', 'position', 'custom')
        # Config.set('graphics', 'left', 25)
        # Config.set('graphics', 'top',  25)
        # Config.set('graphics', 'height', window_height)
        # Config.set('graphics', 'width',  window_width)
        # Config.write()
        
    def build(self):
        self.base_url = self.config.get('Server', 'url')
        self.api_url = self.base_url + "/BCR"
        self.api_key = self.config.get('Server', 'api_key')
        self.set_value_from_config()
        self.load_all_kv_files(os.path.join(
            self.directory, 'libs', 'uix', 'kv'))
        self.screen = StartScreen()  # program main screen
        self.manager = self.screen.ids.manager
        #self.nav_drawer = self.screen.ids.nav_drawer
        #self.set_window_size()
        return self.screen

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            kv_file = os.path.join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                with open(kv_file, encoding='utf-8') as kv:
                    Builder.load_string(kv.read())

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        c = Keyboard()

        '''Called when you press a Key'''
        app = App.get_running_app()
        current_screen = app.manager.current_screen
        hk_next_page = app.config.get('Hotkeys', 'hk_next_page')
        hk_prev_page = app.config.get('Hotkeys', 'hk_prev_page')
        hk_open_page_nav = app.config.get('Hotkeys', 'hk_open_page_nav')
        hk_open_collection = app.config.get(
            'Hotkeys', 'hk_open_collection')
        hk_return_comic_list = app.config.get(
            'Hotkeys', 'hk_return_comic_list')
        hk_return_base_screen = app.config.get(
            'Hotkeys', 'hk_return_base_screen')
        hk_toggle_navbar = app.config.get('Hotkeys', 'hk_toggle_navbar')
        hk_open_comicscreen = app.config.get('Hotkeys', 'hk_open_comicscreen')
        hk_toggle_fullscreen = app.config.get('Hotkeys', 'hk_toggle_fullscreen')
        Logger.debug(f'keyboard:{keyboard}')
        if not current_screen.name in SCREEN_LIST:
            if keyboard in (c.string_to_keycode(hk_next_page), 275):
                current_screen.load_next_slide()
            elif keyboard in (c.string_to_keycode(hk_prev_page), 276):
                current_screen.load_prev_slide()
            elif keyboard == c.string_to_keycode(hk_open_page_nav):
                current_screen.page_nav_popup_open()
            elif keyboard == c.string_to_keycode(hk_open_collection):
                current_screen.comicscreen_open_collection_popup()
            elif keyboard == c.string_to_keycode(hk_toggle_navbar):
                current_screen.toggle_option_bar()
            elif keyboard == c.string_to_keycode(hk_open_comicscreen):
                app.switch_open_comics_screen()
            elif keyboard == c.string_to_keycode(hk_return_comic_list):
                app.switch_readinglists_screen()
            elif keyboard == c.string_to_keycode(hk_return_base_screen):
                app.show_action_bar()
                app.manager.current='base'
            # elif keyboard in (1001, 27):
            #     if self.nav_drawer.state == 'open':
            #         self.nav_drawer.toggle_nav_drawer()
            #     self.back_screen(event=keyboard)
            elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
                self.toggle_full_screen()
        else:
            if keyboard in (282, 319):
                pass
            elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
                self.toggle_full_screen()
            elif keyboard == c.string_to_keycode(hk_open_comicscreen):
                app.manager.current='open_comicscreen'
            elif keyboard == c.string_to_keycode(hk_return_comic_list):
                app.manager.current='readinglistscreen'
            elif keyboard == c.string_to_keycode(hk_return_base_screen):
                app.show_action_bar()
                app.switch_base_screen()
            # elif keyboard in (1001, 27):
            #     if self.nav_drawer.state == 'open':
            #         self.nav_drawer.toggle_nav_drawer()
            #     self.back_screen(event=keyboard)
        return True

    def toggle_full_screen(self):
        if App.get_running_app().full_screen == False:
            Window.fullscreen='auto'
            App.get_running_app().full_screen=True
        else:
            App.get_running_app().full_screen=False
            Window.fullscreen=False
        
    def back_screen(self, event=None):
        '''Screen manager Called when the Back Key is pressed.'''
        # BackKey pressed.
        if event in (1001, 27):
            if self.manager.current == 'base':
                self.dialog_exit()
                return
            try:
                self.manager.current=self.list_previous_screens.pop()
            except:
                self.manager.current='base'
            # self.screen.ids.action_bar.title = self.title

    def show_about(self, *args):
        self.nav_drawer.toggle_nav_drawer()
        self.screen.ids.about.ids.label.text=_(
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
        self.manager.current='about'
        self.screen.ids.action_bar.left_action_items=[
            ['chevron-left', lambda x: self.back_screen(27)]]

    def show_license(self, *args):
        self.screen.ids.license.ids.text_license.text=('%s') % open(
                os.path.join(self.directory, 'LICENSE'),
                encoding='utf-8').read()

        self.nav_drawer._toggle()
        self.manager.current='license'
        self.screen.ids.action_bar.left_action_items=[
            ['chevron-left', lambda x: self.back_screen(27)]]
        self.screen.ids.action_bar.title='MIT LICENSE'

    def select_locale(self, *args):
        '''Displays a window with a list of available language localizations'''

        def select_locale(name_locale):
            '''Sets the selected location..'''

            for locale in self.dict_language.keys():
                if name_locale == self.dict_language[locale]:
                    self.lang=locale
                    self.config.set('General', 'language', self.lang)
                    self.config.write()

        dict_info_locales={}
        for locale in self.dict_language.keys():
            dict_info_locales[self.dict_language[locale]]=[
                'locale', locale == self.lang]

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
                self.exit_interval=False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)

        Clock.schedule_interval(check_interval_press, 1)
        toast('Press Back to Exit')

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def build_settings(self, settings):
        settings.add_json_panel('Server Settings',
                                self.config,
                                data=settings_json_server)
        settings.add_json_panel('Display Settings',
                                self.config,
                                data=settings_json_dispaly)
        settings.add_json_panel('Screen Tap Control',
                                self.config,
                                data=settings_json_screen_tap_control)
        settings.add_json_panel('Hotkeys',
                                self.config,
                                data=settings_json_hotkeys)

    def on_config_change(self, config, section,
                         key, value):
        if key == 'url':
            self.base_url=self.config.get('Server', 'url')
        if key == 'api_key':
            self.api_key=self.config.get('Server', 'api_key')
        if key == 'dbl_tap_time':
            self.Config.set('postproc', 'double_tap_time', value)

    def switch_lists_screen(self):
        self.set_screen("List of Reading Lists Screen")
        self.manager.current='comicracklistscreen'
        comicracklistscreen=self.manager.get_screen('comicracklistscreen')

    def switch_open_comics_screen(self):
        self.set_screen("Open Comics Screen")
        self.manager.current='open_comicscreen'

    def switch_readinglists_screen(self):
        self.set_screen(self.manager.get_screen('readinglistscreen').reading_list_title)
        self.manager.current='readinglistscreen'

    def switch_base_screen(self):
        self.set_screen("ComicRackReader Home Screen")
        self.manager.current='base'

    def set_screen(self, title):
        self.screen.ids.action_bar.title=title

    def hide_action_bar(self):
        self.screen.ids.action_bar.opacity=0
        self.screen.ids.action_bar.disabled=True
        self.screen.ids.action_bar.size_hint_y=None
        self.screen.ids.action_bar.size=(0, 0)

    def show_action_bar(self):
        self.screen.ids.action_bar.opacity=1
        self.screen.ids.action_bar.disabled=False
        self.screen.ids.action_bar.size=(
            Window.width, self.theme_cls.standard_increment)

