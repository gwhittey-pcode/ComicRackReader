# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

#
# LICENSE: MIT


import inspect

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import ConfigParserProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.utils import get_hex_from_color
from kivymd.utils import asynckivy

from libs.uix.baseclass.server_comicbook_screen import ServerComicBookScreen
from libs.uix.baseclass.server_readinglists_screen import ReadingListComicImage
from libs.utils.comic_json_to_class import ComicReadingList
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.db_functions import ReadingList
from libs.utils.paginator import Paginator


class LoginPopupContent(BoxLayout):
    info_text = StringProperty()


class LoginPopup(Popup):
    def on_open(self):
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=App.get_running_app().events_program)

    def on_dismiss(self):
        Window.bind(on_keyboard=App.get_running_app().events_program)


class BaseScreen(Screen):
    app = App.get_running_app()
    username = ConfigParserProperty(
        '', 'General', 'username', app.config)
    password = ConfigParserProperty(
        '', 'General', 'password', app.config)
    api_key = ConfigParserProperty(
        '', 'General', 'api_key', app.config)
    base_url = ConfigParserProperty(
        '', 'General', 'base_url', app.config)

    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''

        self.fetch_data = ComicServerConn()
        self.myLoginPop = LoginPopupContent()
        self.popup = LoginPopup(content=self.myLoginPop,
                                size_hint=(None, None), size=(500, 400))
        # self.update_settings()
        # self.bind(username=self.update_settings)
        # self.bind_settings()
        self.password = self.app.password
        self.api_key = self.app.api_key
        self.username = self.app.username
        self.base_url = self.app.base_url
        self.open_last_comic_startup = self.app.open_last_comic_startup

    def update_settings(self, *args):
        print(f'This is running : {self.username}')
        # self.username = self.app.username

    def on_pre_enter(self, *args):
        self.check_login()

    def check_login(self):
        # see if user has a api key stored from server
        if self.api_key == '':

            self.myLoginPop.ids.info.text = '[color=#FF0000]\
                No API key stored login to get one\
                    [/color]'
            # self.open_popup()
            # self.fetch_data.get_api_key(req_url,self.username,self.password,self)
        else:

            tmp_readinglist_name = self.app.config.get(
                'Saved', 'last_reading_list_name')
            tmp_readinglist_Id = self.app.config.get(
                'Saved', 'last_reading_list_id')
            if tmp_readinglist_Id == '':
                return
            else:
                pass
                Clock.schedule_once(lambda dt: self.build_last_comic_section(
                    tmp_readinglist_name, tmp_readinglist_Id))

    # get api key from server and store it in settings.
    def open_comic(
        self,
        tmp_last_comic_id='',
        tmp_last_comic_type='',
        paginator_obj=None, comic=None,
        tmp_last_pag_pagnum=None
    ):
        new_screen_name = str(tmp_last_comic_id)
        if new_screen_name not in self.app.manager.screen_names:
            if tmp_last_comic_type == 'local_file':
                view_mode = 'Sync'
            else:
                view_mode = 'Server'
            new_screen = ServerComicBookScreen(
                readinglist_obj=self.new_readinglist,
                comic_obj=comic,
                paginator_obj=paginator_obj,
                pag_pagenum=tmp_last_pag_pagnum,
                name=new_screen_name, last_load=0, view_mode=view_mode)
            self.app.manager.add_widget(new_screen)
            self.app.manager.current = new_screen_name
            self.app.app_started = True
        else:
            self.app.manager.current = new_screen_name
            self.app.app_started = True

    def validate_user(self):
        def got_api(result):
            api_key = result['ApiKey']
            self.app.config.set('General', 'api_key', api_key)
            self.app.config.write()
            self.api_key = api_key
            self.myLoginPop.ids.info.text = "[color=#008000]\
                                            Login Sucessful API key saved\
                                                [/color]"
            self.popup.dismiss()
            tmp_readinglist_name = self.app.config.get(
                'Saved', 'last_reading_list_name')
            tmp_readinglist_Id = self.app.config.get(
                'Saved', 'last_reading_list_id')
            if tmp_readinglist_Id == '':
                return
            else:
                Clock.schedule_once(lambda dt: self.build_last_comic_section(
                    tmp_readinglist_name, tmp_readinglist_Id))

        user = self.myLoginPop.ids.username_field.text
        pwd = self.myLoginPop.ids.pwd_field.text
        url = self.myLoginPop.ids.url_field.text
        self.base_url = url.strip()
        self.username = user
        self.password = pwd
        req_url = f"{self.app.base_url}/auth"
        self.fetch_data.get_api_key(req_url, user, pwd, callback=lambda req,
                                    results: got_api(results))

    def build_last_comic_section(self, readinglist_name, readinglist_Id):

        def __got_readlist_data(results):
            async def __load_readinglist_scree(paginator_obj=None):
                if tmp_last_comic_type == 'local_file':
                    x_readinglists_screen = self.app.manager.get_screen(
                        'local_readinglists_screen')
                else:
                    x_readinglists_screen = self.app.manager.get_screen(
                        'server_readinglists_screen')
                x_readinglists_screen.list_loaded = False
                x_readinglists_screen.setup_screen()
                x_readinglists_screen.page_number = tmp_last_pag_pagnum
                x_readinglists_screen.collect_readinglist_data(
                    readinglist_name, readinglist_Id, mode=set_mode)
            tmp_last_comic_id = self.app.config.get(
                'Saved', 'last_comic_id')
            tmp_last_comic_type = self.app.config.get(
                'Saved', 'last_comic_type')
            tmp_last_pag_pagnum = int(self.app.config.get(
                'Saved', 'last_pag_pagnum'))
            if tmp_last_comic_id == '':
                return
            else:
                query = ReadingList.select().where(
                    ReadingList.slug == readinglist_Id)
                if query.exists():
                    Logger.info(f'{readinglist_name} already in Database')
                    set_mode = 'From DataBase'
                    mode = ''
                    if tmp_last_comic_type == 'local_file':
                        mode = 'local_file'
                    self.new_readinglist = ComicReadingList(
                        name=self.readinglist_name, data='db_data',
                        slug=self.readinglist_Id, mode=mode)

                    # self.new_readinglist.comics_write()
                    max_books_page = int(self.app.config.get(
                        'General', 'max_books_page'))
                    new_readinglist_reversed = self.new_readinglist.comics
                    paginator_obj = Paginator(
                        new_readinglist_reversed, max_books_page)
                    for x in range(1, paginator_obj.num_pages()):
                        this_page = paginator_obj.page(x)
                        for comic in this_page.object_list:
                            if tmp_last_comic_id == comic.Id:
                                tmp_last_pag_pagnum = this_page.number
                    asynckivy.start(__load_readinglist_scree(
                        paginator_obj=paginator_obj))
                    if self.open_last_comic_startup == 1\
                            and not self.app.app_started:
                        for comic in self.new_readinglist.comics:
                            if comic.slug == tmp_last_comic_id:

                                self.open_comic(
                                    tmp_last_comic_id=tmp_last_comic_id,
                                    tmp_last_comic_type=tmp_last_comic_type,
                                    paginator_obj=paginator_obj,
                                    comic=comic,
                                    tmp_last_pag_pagnum=tmp_last_pag_pagnum)
                    else:
                        grid = self.ids["main_grid"]
                        grid.cols = 1
                        grid.clear_widgets()
                        for comic in self.new_readinglist.comics:
                            if comic.slug == tmp_last_comic_id:
                                c = ReadingListComicImage(comic_obj=comic)
                                c.readinglist_obj = self.new_readinglist
                                c.paginator_obj = paginator_obj
                                x = self.app.comic_thumb_width
                                y = self.app.comic_thumb_height
                                if tmp_last_comic_type == 'local_file':
                                    if comic.local_file == "":
                                        return
                                    import os
                                    id_folder = os.path.join(
                                        self.app.sync_folder,
                                        self.new_readinglist.slug)
                                    my_thumb_dir = os.path.join(
                                        id_folder, 'thumb')
                                    thumb_name = f'{comic.Id}.jpg'
                                    t_file = os.path.join(
                                        my_thumb_dir, thumb_name)
                                    c_image_source = t_file
                                else:
                                    round_y = round(dp(y))
                                    part_url = f'/Comics/{comic.Id}/Pages/0?'
                                    part_api = '&apiKey={}&height={}'.format(
                                        self.api_key, round_y)
                                    c_image_source = '{}{}{}'.format(
                                        self.app.api_url, part_url, part_api)
                                c.source = c_image_source
                                c.PageCount = comic.PageCount
                                c.pag_pagenum = tmp_last_pag_pagnum
                                if tmp_last_comic_type == 'local_file':
                                    c.view_mode = 'Sync'
                                strtxt = f"{comic.Series} #{comic.Number}"
                                tmp_color = get_hex_from_color((1, 1, 1, 1))
                                c.text = f'[color={tmp_color}]{strtxt}[/color]'
                                grid.add_widget(c)
                                tmp_txt = f'Last Comic Load from \
                                        {self.new_readinglist.name}'
                                self.ids.last_comic_label.text = tmp_txt
                else:
                    Logger.info(
                        f'{readinglist_name} \
                            not in Database This could be a problems')

                    set_mode = 'From Server'
                # set_mode = 'From Server'
        self.readinglist_name = readinglist_name
        # self.app.set_screen(self.readinglist_name + ' Page 1')
        self.reading_list_title = self.readinglist_name + ' Page 1'
        self.readinglist_Id = readinglist_Id

        # self.fetch_data.get_list_count(lsit_count_url,self)
        tmp_last_comic_type = self.app.config.get(
            'Saved', 'last_comic_type')
        if tmp_last_comic_type == 'local_file':
            Clock.schedule_once(
                lambda dt: __got_readlist_data('none'), 0.15)
        else:
            self.fetch_data = ComicServerConn()
            lsit_count_url = f'{self.app.api_url}/Lists/{readinglist_Id}/Comics/'  # noqa
            self.fetch_data.get_server_data_callback(
                lsit_count_url, callback=lambda req,
                results: __got_readlist_data(results))

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

    def callback_for_menu_items(self, *args):
        pass
