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

from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.logger import Logger
import json

from base64 import b64encode
from kivy.uix.button import Button
from kivy.properties import StringProperty
import urllib.parse
from libs.utils.comic_server_conn import ComicServerConn
from kivymd.list import OneLineListItem
from kivymd.accordionlistitem import MDAccordionListItem
from kivymd.list import OneLineIconListItem, OneLineAvatarListItem
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBodyTouch
from kivymd.list import ILeftBody
from kivy.uix.image import Image
from kivymd.toast import toast
from kivy.uix.popup import Popup


class LoginPopup(BoxLayout):
    info_text = StringProperty()


class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.api_key = ''
        self.fetch_data = ComicServerConn()
        self.myLoginPop = LoginPopup()
        self.popup = Popup(content=self.myLoginPop,
                           size_hint=(None, None), size=(500, 400))
        self.username = self.app.config.get('Server', 'username')
        self.password = self.app.config.get('Server', 'password')
        self.api_key = self.app.config.get('Server', 'api_key')
        self.myLoginPop.ids.username_field.text = self.username
        self.myLoginPop.ids.pwd_field.text = self.password
        self.myLoginPop.ids.url_field.text = self.app.config.get(
            'Server', 'url')

    def on_pre_enter(self, *args):
        self.check_login()

    def check_login(self):
        for widget in self.walk():
            print("{} -> {}".format(widget, widget.id))

        # see if user has a api key stored from server

        if self.api_key == '':
            self.myLoginPop.ids.info.text = '[color=#FF0000]No API key sotred login to get one[/color]'
            self.open_popup()
            # self.fetch_data.get_api_key(req_url,self.username,self.password,self)

    # get api key from server and store it in settings.
    def got_api(self, req, result):
        api_key = result['ApiKey']
        self.app.config.set('Server', 'api_key', api_key)
        self.app.config.write()
        self.api_key = api_key
        self.myLoginPop.ids.info.text = "[color=#008000]\
        Login Sucessful API key saved[/color]"

    def validate_user(self):
        user = self.myLoginPop.ids.username_field.text
        pwd = self.myLoginPop.ids.pwd_field.text
        url = self.myLoginPop.ids.url_field.text
        self.app.get_running_app().config.set('Server', 'username', user)
        self.app.get_running_app().config.set('Server', 'password', pwd)
        self.app.get_running_app().config.set('Server', 'url', url)
        self.app.get_running_app().config.write()
        self.app.base_url = url.strip()
        self.app.api_url = self.app.base_url + "/BCR"
        req_url = f"{self.app.base_url}/auth"
        self.fetch_data.get_api_key(req_url, user, pwd, self)

    def update_leaf(self):
        Window.fullscreen = 'auto'

    def open_popup(self):

        self.popup.open()

    def close_popup(self):
        self.popup.dismiss()

    def got_error(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_time_out(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_failure(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))

    def got_redirect(self, req, results):
        Logger.critical('ERROR in %s %s' % (inspect.stack()[0][3], results))
