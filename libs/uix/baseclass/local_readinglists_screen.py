# -*- coding: utf-8 -*-
#
#
# Copyright © 2017 Easy
#

# LICENSE: MIT

"""

name:local_readinglists_screen

"""

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, DictProperty,
                             NumericProperty, ObjectProperty, StringProperty)
from kivy.uix.screenmanager import Screen
from kivymd.toast.kivytoast.kivytoast import toast
from libs.uix.baseclass.server_readinglists_screen import (
    ReadingListComicImage, SyncOptionsPopup)
from libs.utils.comic_json_to_class import ComicBook, ComicReadingList
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.paginator import Paginator

# from libs.utils.server_sync import  SyncReadingListObject


class LocalReadingListsScreen(Screen):
    reading_list_title = StringProperty()
    page_number = NumericProperty()
    max_books_page = NumericProperty()
    dynamic_ids = DictProperty({})    # declare class attribute, dynamic_ids
    sync_bool = BooleanProperty(False)
    so = BooleanProperty()
    new_readinglist = ObjectProperty()

    def __init__(self, **kwargs):
        super(LocalReadingListsScreen, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.fetch_data = None
        self.readinglist_Id = StringProperty()
        self.readinglist_name = ''
        # self.bind_to_resize()
        self.bind(width=self.my_width_callback)
        self.m_grid = ''
        self.main_stack = ''
        self.prev_button = ''
        self.next_button = ''
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.api_key = self.app.config.get('General', 'api_key')
        self.list_count = ''
        self.paginator_obj = ObjectProperty()
        self.current_page = ObjectProperty()
        self.list_loaded = BooleanProperty()
        self.page_number = 1
        self.list_loaded = False
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
        self.file_download = True
        self.num_file_done = 0
        self.max_books_page = self.app.max_books_page

    def callback_for_menu_items(self, *args):
        pass

    def setup_screen(self):
        self.api_key = self.app.config.get('General', 'api_key')
        self.api_url = self.app.api_url
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]

    def on_pre_enter(self, *args):
        self.app.show_action_bar()

        return super().on_pre_enter(*args)

    def on_leave(self, *args):
        self.app.list_previous_screens.append(self.name)
        return super().on_leave(*args)

    def on_enter(self, *args):
        self.app.set_screen(f'{self.readinglist_name}-(Local) Page 1')

    def my_width_callback(self, obj, value):
        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width-10)//self.comic_thumb_width

    def collect_readinglist_data(self, readinglist_name, readinglist_Id,
                                 mode='From DataBase'):
        self.readinglist_name = readinglist_name

        self.reading_list_title = self.readinglist_name + ' Page 1'
        self.readinglist_Id = readinglist_Id
        self.mode = mode
        if self.mode == 'From Server':
            self.fetch_data = ComicServerConn()
            lsit_count_url = f'{self.api_url}/Lists/{readinglist_Id}/Comics/'
            # self.fetch_data.get_list_count(lsit_count_url,self)
            self.fetch_data.get_server_data(lsit_count_url, self)
        elif self.mode == 'From DataBase':
            self.got_db_data()

    def get_page(self, instance):
        page_num = instance.page_num
        self.app.set_screen(self.readinglist_name + f' Page {page_num}')
        self.reading_list_title = self.readinglist_name + f' Page {page_num}'
        page = self.paginator_obj.page(page_num)
        self.current_page = page
        if page.has_next():
            self.next_button.opacity = 1
            self.next_button.disabled = False
            self.next_button.page_num = page.next_page_number()
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            self.next_button.page_num = ''
        if page.has_previous():
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            self.prev_button.page_num = page.previous_page_number()
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            self.prev_button.page_num = ''
        self.build_page(page.object_list)

        self.ids.main_scroll.scroll_to(
            self.ids.main_grid.children[0], padding=10, animate=True)

    def build_page(self, object_lsit):
        grid = self.m_grid
        grid.clear_widgets()
        for comic in object_lsit:
            if comic.is_sync:
                c = ReadingListComicImage(comic_obj=comic)
                c.lines = 2
                c.readinglist_obj = self.new_readinglist
                c.paginator_obj = self.paginator_obj
                y = self.comic_thumb_height
                if self.mode == 'From Server':
                    part_url = f'/Comics/{comic.Id}/Pages/0?'
                    part_api = f'&apiKey={self.api_key}&height={round(dp(y))}'
                    c_image_source = f"{self.api_url}{part_url}{part_api}"
                else:
                    import os
                    id_folder = os.path.join(
                        self.app.sync_folder, self.new_readinglist.slug)
                    my_thumb_dir = os.path.join(id_folder, 'thumb')
                    thumb_name = f'{comic.Id}.jpg'
                    t_file = os.path.join(my_thumb_dir, thumb_name)
                    c_image_source = t_file
                c.source = c_image_source
                c.PageCount = comic.PageCount
                c.pag_pagenum = self.current_page.number
                c.view_mode = 'Sync'
                grid.add_widget(c)
                grid.cols = (Window.width-10)//self.comic_thumb_width
                self.dynamic_ids[id] = c
            else:
                pass
        self.ids.page_count.text = f'Page #\n{self.current_page.number} of \
            {self.paginator_obj.num_pages()}'

    def got_db_data(self):
        """
        used if rl data is already stored in db.
        """

        def _do_readinglist():
            self.new_readinglist = ComicReadingList(
                name=self.readinglist_name, data='db_data',
                slug=self.readinglist_Id, mode='local_file')
            self.so = self.new_readinglist.sw_syn_this_active
            self.setup_options()
            new_readinglist_reversed = self.new_readinglist.comics
            self.paginator_obj = Paginator(
                new_readinglist_reversed, self.max_books_page)
            page = self.paginator_obj.page(self.page_number)
            self.current_page = page
            if page.has_next():
                self.next_button.opacity = 1
                self.next_button.disabled = False
                self.next_button.page_num = page.next_page_number()
            else:
                self.next_button.opacity = 0
                self.next_button.disabled = True
                self.next_button.page_num = ''
            if page.has_previous():
                self.prev_button.opacity = 1
                self.prev_button.disabled = False
                self.prev_button.page_num = page.previous_page_number()
            else:
                self.prev_button.opacity = 0
                self.prev_button.disabled = True
                self.prev_button.page_num = ''
            self.build_page(page.object_list)
            self.list_loaded = True
        Clock.schedule_once(lambda dt: _do_readinglist(), 0)

        # self.bind(new_readinglist=self.setter('sync_bool'))
        # self.max_books_page = int(self.app.config.get(
        #    'General', 'max_books_page'))

    def got_json(self, req, results):
        self.new_readinglist = ComicReadingList(
            name=self.readinglist_name, data=results, slug=self.readinglist_Id)
        for item in self.new_readinglist.comic_json:
            comic_index = self.new_readinglist.comic_json.index(item)
            new_comic = ComicBook(
                item, readlist_obj=self.new_readinglist,
                comic_index=comic_index)
            self.new_readinglist.add_comic(new_comic)
        self.setup_options()
        new_readinglist_reversed = self.new_readinglist.comics[::-1]
        self.paginator_obj = Paginator(
            new_readinglist_reversed, self.max_books_page)
        page = self.paginator_obj.page(self.page_number)
        self.current_page = page
        if page.has_next():
            self.next_button.opacity = 1
            self.next_button.disabled = False
            self.next_button.page_num = page.next_page_number()
        else:
            self.next_button.opacity = 0
            self.next_button.disabled = True
            self.next_button.page_num = ''
        if page.has_previous():
            self.prev_button.opacity = 1
            self.prev_button.disabled = False
            self.prev_button.page_num = page.previous_page_number()
        else:
            self.prev_button.opacity = 0
            self.prev_button.disabled = True
            self.prev_button.page_num = ''
        self.build_page(page.object_list)
        self.list_loaded = True

    def setup_options(self):
        s_r_l = self.new_readinglist
        self.sync_options = SyncOptionsPopup(
            size_hint=(.76, .76),
            cb_limit_active=s_r_l.cb_limit_active,
            limit_num_text=str(s_r_l.limit_num),
            cb_only_read_active=s_r_l.cb_only_read_active,
            cb_purge_active=s_r_l.cb_purge_active,
            cb_optimize_size_active=s_r_l.cb_optimize_size_active,
            sw_syn_this_active=bool(s_r_l.sw_syn_this_active),
        )
        self.sync_options.ids.limit_num.bind(
            on_text_validate=self.sync_options.check_input,
            focus=self.sync_options.check_input,
        )

        self.sync_options.title = self.new_readinglist.name

    def open_sync_options(self):
        if self.sync_options.ids.sw_syn_this.active is True:
            self.sync_options.ids.syn_on_off_label.text = f''
            self.sync_options.ids.syn_on_off_label.theme_text_color = 'Primary'
        self.sync_options.open()

    def sync_readinglist(self):
        if self.sync_options.ids.sw_syn_this.active is False:
            self.sync_options.ids.syn_on_off_label.text = f'Sync Not Turned On'
            self.open_sync_options()
        elif self.sync_options.ids.sw_syn_this.active is True:
            toast(f'Starting sync of {self.new_readinglist.name}')
            self.new_readinglist.do_sync()
