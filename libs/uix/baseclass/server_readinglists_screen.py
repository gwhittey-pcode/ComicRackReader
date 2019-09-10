# -*- coding: utf-8 -*-
#
# This file created with KivyCreatorProject
# <https://github.com/HeaTTheatR/KivyCreatorProgect
#
# Copyright © 2017 Easy
#
# For suggestions and questions:
# <kivydevelopment@gmail.com>
# LICENSE: MIT
from kivy.core.window import Window

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, NumericProperty,\
    BooleanProperty
from kivy.uix.image import AsyncImage
from kivymd.uix.imagelist import SmartTileWithLabel
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
from libs.utils.server_sync import SyncServer
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.toast.kivytoast.kivytoast import toast
from libs.utils.paginator import Paginator
from libs.uix.baseclass.server_comicbook_screen import ServerComicBookScreen
from kivy.clock import Clock
from functools import partial
from kivy.utils import get_hex_from_color
from kivy.metrics import dp
from libs.utils.comicapi.comicarchive import ComicArchive

import ntpath


class CustomeST(SmartTileWithLabel):
    my_clock = ObjectProperty()
    do_action = StringProperty()

    def __init__(self, **kwargs):
        super(CustomeST, self).__init__(**kwargs)
        self.menu_items = [{'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Open This Comic[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Mark as Read[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Mark as UnRead[/color]',
                            'callback': self.callback_for_menu_items},
                           {'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Download Readlist[/color]',
                            'callback': self.callback_for_menu_items}
                           ]
        self.app = App.get_running_app()
        self.comic_slug = StringProperty()
        self.page_count = NumericProperty()
        self.leaf = NumericProperty()
        self.percent_read = NumericProperty()
        self.status = StringProperty()
        self.comic_obj = ObjectProperty()
        self.readinglist_obj = ObjectProperty()
        self.paginator_obj = ObjectProperty()
        self.pag_pagenum = NumericProperty()

    def callback_for_menu_items(self, *args):
        def updated_progress(results):
            print('update')
            tmp_txt = self.text
            new_txt = tmp_txt.replace('Read', 'Unread')
            print(new_txt)
            self.text = new_txt
            self.img_color = (1, 1, 1, 1)
        action = args[0].replace('[color=#000000]', '')
        action = action.replace('[/color]', '')
        print(f'action:{action}')
        if action == "Open This Comic":
            new_screen_name = str(self.comic_obj.Id)
            if new_screen_name not in self.app.manager.screen_names:
                new_screen = ServerComicBookScreen(
                    readinglist_obj=self.readinglist_obj,
                    comic_obj=self.comic_obj,
                    paginator_obj=self.paginator_obj,
                    pag_pagenum=self.pag_pagenum,
                    name=new_screen_name)
                self.app.manager.add_widget(new_screen)
                self.app.manager.current = new_screen_name
        elif action == 'Mark as Read':
            print(f'self.color:{self.img_color}')
        elif action == 'Mark as UnRead':
            server_con = ComicServerConn()
            update_url = f'{self.app.api_url}/Comics/{self.comic_obj.Id}/Progress'
            server_con.update_progress(update_url, 0,
                                       callback=lambda req, results:
                                       updated_progress(results))

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = 'read'
        Clock.schedule_once(callback, 1.5)
        self.my_clock = callback

    def menu(self, *args):
        self.do_action = 'menu'

    def on_release(self):
        Clock.unschedule(self.my_clock)
        self.do_action = 'menu'
        return super(CustomeST, self).on_press()

    def open_comic(self):
        new_screen_name = str(self.comic_obj.Id)
        if new_screen_name not in self.app.manager.screen_names:
            new_screen = ServerComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                comic_obj=self.comic_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=self.pag_pagenum,
                name=new_screen_name, last_load=0)
            self.app.manager.add_widget(new_screen)
            self.app.manager.current = new_screen_name
        else:
            self.app.manager.current = new_screen_name


class CustomMDFillRoundFlatIconButton(MDFillRoundFlatIconButton):
    def __init__(self, **kwargs):
        _url = ObjectProperty()
        page_num = NumericProperty()
        super(CustomMDFillRoundFlatIconButton, self).__init__(**kwargs)


class SyncButton(MDFillRoundFlatIconButton):
    my_clock = ObjectProperty()
    do_action = StringProperty()

    def __init__(self, **kwargs):
        super(SyncButton, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.menu_items = [{'viewclass': 'MDMenuItem',
                            'text': '[color=#000000]Reduce File Size[/color]',
                            'callback': self.callback_for_menu_items},
                           #    {'viewclass': 'MDMenuItem',
                           #     'text': '[color=#000000]Orginal File[/color]',
                           #     'callback': self.callback_for_menu_items},

                           ]

    def callback_for_menu_items(self, *args):
        if args[0] == "[color=#000000]Reduce File Size[/color]":
            self.app.manager.current_screen.sync_readinglist_button()
            print('Sync - Reduce File Size')
        elif args[0] == "[color=#000000]Orginal File[/color]":
            print('Sync - Orginal File')

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = 'read'
        Clock.schedule_once(callback, 1.5)
        self.my_clock = callback

    def menu(self, *args):
        self.do_action = 'menu'

    def on_release(self):
        Clock.unschedule(self.my_clock)
        self.do_action = 'menu'
        return super(SyncButton, self).on_press()

    def do_sync_rf(self):
        self.app.manager.current_screen.sync_readinglist_button()


class ServerReadingListsScreen(Screen):
    reading_list_title = StringProperty()
    page_number = NumericProperty()

    def __init__(self, **kwargs):
        super(ServerReadingListsScreen, self).__init__(**kwargs)
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
        self.new_readinglist = None
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.api_key = self.app.config.get('Server', 'api_key')
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

    def setup_screen(self):
        self.api_key = self.app.config.get('Server', 'api_key')
        self.api_url = self.app.api_url
        self.main_stack = self.ids['main_stack']
        self.m_grid = self.ids["main_grid"]
        self.prev_button = self.ids["prev_button"]
        self.next_button = self.ids["next_button"]

    def on_pre_enter(self, *args):

        self.app.show_action_bar()

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def my_width_callback(self, obj, value):
        win_x = (Window.width-30)//self.comic_thumb_width
        win_div = (Window.width-30) % self.comic_thumb_width
        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width-10)//self.comic_thumb_width

    def collect_readinglist_data(self, readinglist_name, readinglist_Id):
        self.readinglist_name = readinglist_name
        self.app.set_screen(self.readinglist_name + ' Page 1')
        self.reading_list_title = self.readinglist_name + ' Page 1'
        self.readinglist_Id = readinglist_Id
        self.fetch_data = ComicServerConn()
        lsit_count_url = f'{self.api_url}/Lists/{readinglist_Id}/Comics/'
        # self.fetch_data.get_list_count(lsit_count_url,self)
        self.fetch_data.get_server_data(lsit_count_url, self)

    def get_page(self, instance):
        print(instance.id)
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

    def build_page(self, object_lsit):
        grid = self.m_grid
        main_stack = self.main_stack
        grid.clear_widgets()
        for comic in object_lsit:
            c = CustomeST()
            c.comic_obj = comic
            c.lines = 2
            c.readinglist_obj = self.new_readinglist
            c.paginator_obj = self.paginator_obj
            x = self.comic_thumb_width
            y = self.comic_thumb_height
            thumb_size = f'height={y}&width={x}'
            part_url = f'/Comics/{comic.Id}/Pages/0?'
            part_api = f'&apiKey={self.api_key}&height={round(dp(y))}'
            c_image_source = f"{self.api_url}{part_url}{part_api}"
            c.source = source = c_image_source
            c.PageCount = comic.PageCount
            c.pag_pagenum = self.current_page.number
            if comic.Id in self.app.current_files:
                is_sync = ' \n[File Synced]'
            else:
                is_sync = ''
            strtxt = f"{comic.Series} #{comic.Number}{is_sync}"
            if comic.UserLastPageRead == comic.PageCount-1:
                strtxt = f'{strtxt} \n[Read]'
                c.img_color = (.89, .15, .21, 5)
                #txt_color = get_hex_from_color((.89, .15, .21, 1))
                txt_color = get_hex_from_color((1, 1, 1, 1))
            else:
                strtxt = f'{strtxt} [UnRead]'
                txt_color = get_hex_from_color((1, 1, 1, 1))
            c.text = f'[color={txt_color}]{strtxt}[/color]'
            grid.add_widget(c)
            grid.cols = (Window.width-10)//self.comic_thumb_width
            self.ids.page_count.text = f'{self.current_page.number} of {self.paginator_obj.num_pages()}'

    def got_json(self, req, result):
        self.comic_collection = result
        self.new_readinglist = ComicReadingList(
            name=self.readinglist_name, data=result, slug=self.readinglist_Id)
        for item in self.new_readinglist.data["items"]:
            new_comic = ComicBook(item)
            self.new_readinglist.add_comic(new_comic)
        max_books_page = int(self.app.config.get(
            'Server', 'max_books_page'))

        orphans = max_books_page - 1
        new_readinglist_reversed = self.new_readinglist.comics[::-1]
        self.paginator_obj = Paginator(
            new_readinglist_reversed, max_books_page)
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

    def sync_delayed_work(self, func, items, delay=0):
        '''Apply the func() on each item contained in items
        '''
        if not items:
            return

        def _sync_delayed_work(*l):
            item = items.pop(0)
            if func(item) is False or not len(items):
                return False
            Clock.schedule_once(_sync_delayed_work, delay)
        Clock.schedule_once(_sync_delayed_work, delay)

    def download_file(self, comic):
        def got_file(results):
            self.num_file_done += 1
            toast(f'{file_name} Synced')
            self.file_download = True
        self.file_download = False
        file_name = ntpath.basename(comic.file_path)
        new_readinglist_reversed = self.new_readinglist.comics[::-1]
        comic_index = new_readinglist_reversed.index(comic)
        self.app.current_files.put(comic.Id,
                                   file=file_name,
                                   Id=comic.Id,
                                   slug=comic.slug,
                                   data_type='ComicBook',
                                   Series=comic.Series,
                                   Number=comic.Number,
                                   Month=comic.month,
                                   Year=comic.year,
                                   UserCurrentPage=comic.UserCurrentPage,
                                   UserLastPageRead=comic.UserLastPageRead,
                                   PageCount=comic.PageCount,
                                   Summary=comic.Summary,
                                   Index=comic_index,
                                   FilePath=comic.file_path,
                                   ReadlistID=self.new_readinglist.slug
                                   )
        lsit_count_url = f'{self.api_url}/Comics/{comic.Id}/Sync/'
        self.fetch_data.get_server_file_download(
            lsit_count_url, callback=lambda req,
            results: got_file(results),
            file_path=f'{self.app.sync_dir}/comics/{file_name}'
        )

    def _finish_sync(self, dt):
        def _finish_toast(dt):
            toast('Reading List has been Synceddd')
        page = self.paginator_obj.page(self.current_page.number)
        list_comics = page.object_list
        num_comic = len(list_comics)
        if self.num_file_done == num_comic:
            Clock.schedule_once(_finish_toast, 3)
            self.event.cancel()

    def sync_readinglist_button(self):
        page = self.paginator_obj.page(self.current_page.number)
        list_comics = page.object_list
        self.sync_delayed_work(self.download_file, list_comics, delay=.15)
        self.event = Clock.schedule_interval(self._finish_sync, 0.5)

        # sync_screen = self.app.manager.get_screen('syncscreen')
        # sync_screen.obj_readinglist = page.object_list
        # self.app.manager.current = 'syncscreen'
    def test_it(self):
        print('start')
        res = self.app.current_files.find(data_type='ComicBook')
        rl = ComicReadingList('Test', 'test')
        for item in res:
            new_comic = ComicBook(item[1])
            rl.add_comic(new_comic)
        for comic in rl.comics:
            print(comic.name)
