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
from libs.uix.baseclass.readinglistscreen import CustomeST
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
from libs.utils.paginator import Paginator


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
        # see if user has a api key stored from server

        if self.api_key == '':
            self.myLoginPop.ids.info.text = '[color=#FF0000]No API key sotred login to get one[/color]'
            self.open_popup()
            # self.fetch_data.get_api_key(req_url,self.username,self.password,self)
        else:
            tmp_readinglist_name = self.app.config.get(
                'Saved', 'last_reading_list_name')
            tmp_readinglist_Id = self.app.config.get(
                'Saved', 'last_reading_list_id')
            if tmp_readinglist_Id == '':
                return
            else:
                self.build_last_comic_section(
                    tmp_readinglist_name, tmp_readinglist_Id)
    # get api key from server and store it in settings.

    def got_api(self, req, result):
        api_key = result['ApiKey']
        self.app.config.set('Server', 'api_key', api_key)
        self.app.config.write()
        self.api_key = api_key
        self.myLoginPop.ids.info.text = "[color=#008000]\
        Login Sucessful API key saved[/color]"
        self.build_last_comic_section()

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

    def build_last_comic_section(self, readinglist_name, readinglist_Id):
        self.readinglist_name = readinglist_name
        # self.app.set_screen(self.readinglist_name + ' Page 1')
        self.reading_list_title = self.readinglist_name + ' Page 1'
        self.readinglist_Id = readinglist_Id
        self.fetch_data = ComicServerConn()
        lsit_count_url = f'{self.app.api_url}/Lists/{readinglist_Id}/Comics/'
        # self.fetch_data.get_list_count(lsit_count_url,self)

        self.fetch_data.get_server_data_callback(
            lsit_count_url, callback=lambda req, results: got_readlist_data(results))

        def got_readlist_data(results):
            tmp_last_comic_id = self.app.config.get(
                'Saved', 'last_comic_id')
            tmp_last_pag_pagnum = self.app.config.get(
                'Saved', 'last_pag_pagnum')
            if tmp_last_comic_id == '':
                return
            else:
                new_readinglist = ComicReadingList(
                    name=readinglist_name, data=results, slug=readinglist_Id)
                for item in new_readinglist.data["items"]:
                    new_comic = ComicBook(item)
                    new_readinglist.add_comic(new_comic)
                max_books_page = int(self.app.config.get(
                    'Server', 'max_books_page'))
                orphans = max_books_page - 1
                new_readinglist_reversed = new_readinglist.comics[::-1]
                paginator_obj = Paginator(
                    new_readinglist_reversed, max_books_page)
                readinglistscreen = self.app.manager.get_screen(
                    'readinglistscreen')
                readinglistscreen.list_loaded = False
                readinglistscreen.setup_screen()
                readinglistscreen.collect_readinglist_data(
                    readinglist_name, readinglist_Id)
                grid = self.ids["main_grid"]
                grid.cols = 1
                grid.clear_widgets()
                for comic in new_readinglist.comics:
                    if comic.slug == tmp_last_comic_id:
                        c = CustomeST()
                        c.comic_obj = comic
                        c.readinglist_obj = new_readinglist
                        c.paginator_obj = paginator_obj
                        x = self.app.comic_thumb_width
                        y = self.app.comic_thumb_height
                        thumb_size = f'height={y}&width={x}'
                        part_url = f'/Comics/{comic.Id}/Pages/0?'
                        part_api = f'&apiKey={self.api_key}'
                        c_image_source = f"{self.app.api_url}{part_url}{part_api}"
                        c.source = source = c_image_source
                        c.PageCount = comic.PageCount
                        c.pag_pagenum = tmp_last_pag_pagnum
                        strtxt = f"{comic.Series} #{comic.Number}"
                        c.text = strtxt
                        c.text_color = (0, 0, 0, 1)
                        grid.add_widget(c)
                        tmp_txt = f'Last Comic Load from {new_readinglist.name}'
                        self.ids.last_comic_label.text = tmp_txt

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
