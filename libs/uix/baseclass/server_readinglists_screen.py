# -*- coding: utf-8 -*-
#
#
# Copyright © 2017 Easy
#

# LICENSE: MIT

"""

name:server_readinglists_screen

"""

import os
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, DictProperty, NumericProperty,
                             ObjectProperty, OptionProperty, StringProperty)
from kivy.uix.button import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.utils import get_hex_from_color
from kivymd.toast.kivytoast.kivytoast import toast
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDIcon
from kivymd.uix.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import FixedHintTextInput, MDTextFieldRound
from kivymd.utils import asynckivy
from peewee import DataError, OperationalError, ProgrammingError

from libs.uix.baseclass.server_comicbook_screen import ServerComicBookScreen
from libs.uix.widgets.myimagelist import ComicTileLabel
from libs.utils.comic_functions import save_thumb
from libs.utils.comic_json_to_class import ComicBook, ComicReadingList
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.db_functions import Comic
from libs.utils.paginator import Paginator


class ReadingListComicImage(ComicTileLabel):
    my_clock = ObjectProperty()
    do_action = StringProperty()
    comic_slug = StringProperty()
    page_count = NumericProperty()
    leaf = NumericProperty()
    percent_read = NumericProperty()
    status = StringProperty()
    comic_obj = ObjectProperty(rebind=True)
    readinglist_obj = ObjectProperty(rebind=True)
    paginator_obj = ObjectProperty(rebind=True)
    pag_pagenum = NumericProperty()
    UserLastPageRead = NumericProperty()
    UserCurrentPage = NumericProperty()
    percent_read = NumericProperty()
    view_mode = StringProperty('Server')
    loading_done = BooleanProperty(False)

    def __init__(self, comic_obj=None, **kwargs):
        super(ReadingListComicImage, self).__init__(**kwargs)
        list_menu_items = ['Open This Comic',
                           'Mark as Read', 'Mark as UnRead', 'Download Comic']
        self.menu_items = []
        for item in list_menu_items:
            a_menu_item = {'viewclass': 'MDMenuItem',
                           'text': f'[color=#000000]{item}[/color]',
                           'callback': self.callback_for_menu_items}
            self.menu_items.append(a_menu_item)
        self.app = App.get_running_app()
        self.comic_obj = comic_obj
        self.img_color = (.89, .15, .21, 5)
        self.UserCurrentPage = comic_obj.UserCurrentPage
        self.UserLastPageRead = comic_obj.UserLastPageRead
        if self.comic_obj.local_file != '':
            self.has_localfile = True
        if self.comic_obj.UserLastPageRead == self.comic_obj.PageCount - 1:
            # self.img_color = (.89, .15, .21, 5)
            self.is_read = True
            # txt_color = get_hex_from_color((.89, .15, .21, 1))
            txt_color = get_hex_from_color((1, 1, 1, 1))
        else:
            txt_color = get_hex_from_color((1, 1, 1, 1))
            self.is_read = False
        strtxt = f"{self.comic_obj.Series} #{self.comic_obj.Number}"
        self.text = f'[color={txt_color}]{strtxt}[/color]'
        self._comic_object = self.comic_obj
        if comic_obj.UserLastPageRead == 0:
            self.percent_read = 0
        else:
            self.percent_read = round(
                comic_obj.UserLastPageRead / (comic_obj.PageCount - 1) * 100)
        self.page_count_text = f'{self.percent_read}%'

    def callback_for_menu_items(self, *args):
        def __updated_progress(results, state):
            Logger.info(results)
            if state == 'Unread':
                # self.img_color = (1, 1, 1, 1)
                self.is_read = False
                self.page_count_text = '0%'
                self.comic_obj.UserLastPage = 0
                self.comic_obj.UserCurrentPage = 0
                self.comic_obj.update()
            elif state == 'Read':
                # self.img_color = (.89, .15, .21, 5)
                self.is_read = True
                self.page_count_text = '100%'
                the_page = self.comic_obj.PageCount
                self.comic_obj.UserLastPage = the_page
                self.comic_obj.UserCurrentPage = the_page
        action = args[0].replace(
            '[color=#000000]', "").replace('[/color]', "")
        if action == "Open This Comic":
            self.open_comic()
        elif action == 'Mark as Read':
            try:
                db_comic = Comic.get(Comic.Id == self.comic_obj.Id)
                if db_comic:
                    db_comic.UserLastPageRead = self.comic_obj.PageCount - 1
                    db_comic.UserCurrentPage = self.comic_obj.PageCount - 1
                    db_comic.save()
                    self.comic_obj.UserLastPageRead = self.comic_obj.PageCount-1  # noqa
                    self.comic_obj.UserCurrentPage = self.comic_obj.PageCount - 1

            except (ProgrammingError, OperationalError, DataError) as e:
                Logger.error(f'Mar as unRead DB: {e}')
            server_con = ComicServerConn()
            update_url = '{}/Comics/{}/Progress'.format(
                self.app.api_url, self.comic_obj.Id)
            server_con.update_progress(
                update_url, self.comic_obj.PageCount - 1,
                callback=lambda req,
                results: __updated_progress(results, 'Read'))

        elif action == 'Mark as UnRead':
            try:
                db_comic = Comic.get(Comic.Id == self.comic_obj.Id)
                if db_comic:
                    db_comic.UserLastPageRead = 0
                    db_comic.UserCurrentPage = 0
                    db_comic.save()
                    self.comic_obj.UserLastPageRead = 0
                    self.comic_obj.UserCurrentPage = 0
            except (ProgrammingError, OperationalError, DataError) as e:
                Logger.error(f'Mar as unRead DB: {e}')
            server_con = ComicServerConn()
            update_url = '{}/Comics/{}/Mark_Unread'.format(
                self.app.api_url, self.comic_obj.Id)
            server_con.update_progress(
                update_url, 0,
                callback=lambda req, results:
                __updated_progress(results, 'Unread'))

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = 'read'
        Clock.schedule_once(callback, .25)
        self.my_clock = callback

    def menu(self, *args):
        self.do_action = 'menu'

    def on_release(self):
        Clock.unschedule(self.my_clock)
        self.do_action = 'menu'
        return super(ReadingListComicImage, self).on_press()

    def open_comic(self):
        new_screen_name = str(self.comic_obj.Id)
        if new_screen_name not in self.app.manager.screen_names:
            new_screen = ServerComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                comic_obj=self.comic_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=self.pag_pagenum,
                name=new_screen_name, last_load=0, view_mode=self.view_mode)
            self.app.manager.add_widget(new_screen)
            self.app.manager.current = new_screen_name
        else:
            self.app.manager.current = new_screen_name


class CustomMDFillRoundFlatIconButton(MDIconButton):
    pass


class Tooltip(Label):
    pass


class SyncButtonIcon(ButtonBehavior, MDIcon):
    icon_name = StringProperty()

    my_clock = ObjectProperty()
    do_action = StringProperty()
    tooltip_text = StringProperty()
    tooltip = Tooltip(text='No Tooltip')

    def __init__(self, **kwargs):
        #Window.bind(mouse_pos=self.on_mouse_pos)
        super(SyncButtonIcon, self).__init__(**kwargs)
        self.tooltip = Tooltip(text=self.tooltip_text)
        self.app = App.get_running_app()

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        self.tooltip.text = self.tooltip_text
        self.tooltip.pos = pos
        # cancel scheduled event since I moved the cursor
        Clock.unschedule(self.display_tooltip)
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, .5)

    def close_tooltip(self, *args):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        Window.add_widget(self.tooltip)

    def do_sync_rf(self, *args):
        self.app.manager.get_screen(
            'server_readinglists_screen').sync_readinglist()

    def do_options(self, *args):
        self.app.manager.get_screen(
            'server_readinglists_screen').open_sync_options()

    def do_data_refresh(self, *args):
        the_screen = self.app.manager.get_screen('server_readinglists_screen')
        the_screen.new_readinglist.do_db_refresh(screen=the_screen)


class SynLimitButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super(SynLimitButton, self).__init__(**kwargs)
        self.limit_menu_items = [{'viewclass': 'MDMenuItem',
                                  'text': '[color=#000000]Books[/color]',
                                  'callback': self.callback_for_menu_items},
                                 {'viewclass': 'MDMenuItem',
                                  'text': '[color=#000000]GB[/color]',
                                  'callback': self.callback_for_menu_items},
                                 {'viewclass': 'MDMenuItem',
                                  'text': '[color=#000000]MB[/color]',
                                  'callback': self.callback_for_menu_items},
                                 ]

    def callback_for_menu_items(self, *args):
        action = args[0].replace(
            '[color=#000000]', "").replace('[/color]', "")
        if action == "Books":
            self.text = "Books"
        elif action == "GB":
            self.text = "GB"
        elif action == "MB":
            self.text = "MB"

    def open_menu(self):
        MDDropdownMenu(items=self.limit_menu_items, width_mult=3).open(self)


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class AvatarSampleWidget(ILeftBody, MDIconButton):
    pass


class MyMDTextFieldRound(MDTextFieldRound, FixedHintTextInput):
    def __init__(self, **kwargs):
        super(MyMDTextFieldRound, self).__init__(**kwargs)
    helper_text = StringProperty("This field is required")
    helper_text_mode = OptionProperty(
        "none", options=["none", "on_error", "persistent", "on_focus"]
    )


class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):
    def __init__(self, **kwargs):
        super(IconRightSampleWidget, self).__init__(**kwargs)

    def statechange(self, instance):
        print('State Change')

    def on_touch_up(self, touch):
        return super().on_touch_up(touch)
        print('touch down')


class ServerReadingListsScreen(Screen):
    reading_list_title = StringProperty()
    page_number = NumericProperty()
    max_books_page = NumericProperty()
    dynamic_ids = DictProperty({})    # declare class attribute, dynamic_ids
    sync_bool = BooleanProperty(False)
    so = BooleanProperty()
    new_readinglist = ObjectProperty()

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
        self.please_wait_dialog = None

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

    def my_width_callback(self, obj, value):

        for key, val in self.ids.items():
            if key == 'main_grid':
                c = val
                c.cols = (Window.width - 10) // self.comic_thumb_width

    def collect_readinglist_data(
            self, readinglist_name='',
            readinglist_Id='',
            mode='From Server',
            *largs):
        async def collect_readinglist_data():
            self.readinglist_name = readinglist_name
            self.app.set_screen(self.readinglist_name + ' Page 1')
            self.reading_list_title = self.readinglist_name + ' Page 1'
            self.readinglist_Id = readinglist_Id
            self.mode = mode
            if self.mode == 'From Server':
                self.fetch_data = ComicServerConn()
                lsit_count_url = '{}/Lists/{}/Comics/'.format(
                    self.api_url, readinglist_Id)
                # self.fetch_data.get_list_count(lsit_count_url,self)
                self.fetch_data.get_server_data(lsit_count_url, self)
            elif self.mode == 'From DataBase':
                self.got_db_data()
        asynckivy.start(collect_readinglist_data())

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

    def build_page(self, object_lsit):
        async def build_page():
            grid = self.m_grid
            grid.clear_widgets()
            for comic in object_lsit:
                await asynckivy.sleep(0)
                c = ReadingListComicImage(comic_obj=comic)
                c.lines = 2
                c.readinglist_obj = self.new_readinglist
                c.paginator_obj = self.paginator_obj
                y = self.comic_thumb_height
                thumb_filename = f'{comic.Id}.jpg'
                id_folder = self.app.store_dir
                my_thumb_dir = os.path.join(
                    id_folder, 'comic_thumbs')
                t_file = os.path.join(my_thumb_dir, thumb_filename)
                if os.path.isfile(t_file):
                    c_image_source = t_file
                else:
                    part_url = f'/Comics/{comic.Id}/Pages/0?'
                    part_api = '&apiKey={}&height={}'.format(
                        self.api_key, round(dp(y)))
                    c_image_source = f"{self.api_url}{part_url}{part_api}"
                    asynckivy.start(save_thumb(comic.Id, c_image_source))
                c.source = c_image_source
                c.PageCount = comic.PageCount
                c.pag_pagenum = self.current_page.number
                grid.add_widget(c)
                grid.cols = (Window.width - 10) // self.comic_thumb_width
                self.dynamic_ids[id] = c
            self.ids.page_count.text = 'Page #\n{} of {}'.format(
                self.current_page.number, self.paginator_obj.num_pages())
            self.loading_done = True
        asynckivy.start(build_page())

    def refresh_callback(self, *args):
        '''A method that updates the state of reading list'''
        def refresh_callback(interval):
            self.ids.main_grid.clear_widgets()
            self.collect_readinglist_data(
                self.readinglist_name,
                self.readinglist_Id,
                mode='From DataBase')
#            self.build_page(page.object_list)
            self.ids.main_scroll.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)

    def got_db_data(self):
        """
        used if rl data is already stored in db.
        """
        async def _do_readinglist():
            self.new_readinglist = ComicReadingList(
                name=self.readinglist_name,
                data='db_data',
                slug=self.readinglist_Id)
            await asynckivy.sleep(0)
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
        asynckivy.start(_do_readinglist())

    def got_json(self, req, results):
        async def got_json():
            self.new_readinglist = ComicReadingList(
                name=self.readinglist_name,
                data=results,
                slug=self.readinglist_Id)
            for item in self.new_readinglist.comic_json:
                comic_index = self.new_readinglist.comic_json.index(item)
                new_comic = ComicBook(
                    item,
                    readlist_obj=self.new_readinglist,
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
        asynckivy.start(got_json())

    def show_please_wait_dialog(self):
        def __callback_for_please_wait_dialog(*args):
            pass
        self.please_wait_dialog = MDDialog(
            title="No ReadingList loaded.",
            size_hint=(0.8, 0.4),
            text_button_ok="Ok",
            text=f"No ReadingList loaded.",
            events_callback=__callback_for_please_wait_dialog,
        )
        self.please_wait_dialog.open()

    def setup_options(self):
        self.sync_options = SyncOptionsPopup(
            size_hint=(.76, .76),
            cb_limit_active=self.new_readinglist.cb_limit_active,
            limit_num_text=str(self.new_readinglist.limit_num),
            cb_only_read_active=self.new_readinglist.cb_only_read_active,
            cb_purge_active=self.new_readinglist.cb_purge_active,  # noqa
            cb_optimize_size_active=self.new_readinglist.cb_optimize_size_active,  # noqa
            sw_syn_this_active=bool(
                self.new_readinglist.sw_syn_this_active),
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


class SyncOptionsPopup(Popup):
    background = 'assets/cPop_bkg.png'
    text = StringProperty('')
    cb_limit_active = BooleanProperty(False)
    limit_num_text = BooleanProperty(False)
    cb_only_read_active = BooleanProperty(False)
    cb_purge_active = BooleanProperty(False)
    cb_optimize_size_active = BooleanProperty(False)
    sw_syn_this_active = BooleanProperty(False)
    ok_text = StringProperty('OK')
    cancel_text = StringProperty('Cancel')

    __events__ = ('on_ok', 'on_cancel')

    def __init__(self, **kwargs):
        super(SyncOptionsPopup, self).__init__(**kwargs)
        app = App.get_running_app()
        server_readinglists_screen = app.manager.get_screen(
            'server_readinglists_screen')
        self.current_screen = server_readinglists_screen

    def check_input(self, *args):
        text_field = args[0]
        if text_field.text.isnumeric():
            text_field.error = False
            return True
        else:
            text_field.error = True
            return False

    def on_open(self):
        # self.sw_syn_this.active=bool(self.current_screen.new_readinglist.sw_syn_this_active)
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=App.get_running_app().events_program)

    def on_dismiss(self):
        Window.bind(on_keyboard=App.get_running_app().events_program)

    def on_ok(self):
        chk_input = self.check_input(self.ids.limit_num)
        if chk_input is True:
            if self.ids.sw_syn_this.active:
                self.current_screen.sync_bool = True
            else:
                self.current_screen.sync_bool = False
            self.current_screen.new_readinglist.save_settings(
                cb_limit_active=self.ids.cb_limit.active,
                limit_num=int(self.ids.limit_num.text),
                cb_only_read_active=self.ids.cb_only_read.active,
                cb_purge_active=self.ids.cb_purge.active,
                cb_optimize_size_active=self.ids.cb_optimize_size.active,
                sw_syn_this_active=self.ids.sw_syn_this.active,
            )
            self.dismiss()
        else:
            self.ids.limit_num.focus = True
            return

    def on_cancel(self):
        self.ids.cb_limit.active = self.current_screen.new_readinglist.cb_limit_active # noqa
        self.ids.limit_num.text = str(
            self.current_screen.new_readinglist.limit_num)
        self.ids.cb_only_read.active = self.current_screen.new_readinglist.cb_only_read_active # noqa
        self.ids.cb_purge.active = self.current_screen.new_readinglist.cb_purge_active # noqa
        self.ids.cb_optimize_size.active = self.current_screen.new_readinglist.cb_optimize_size_active # noqa
        self.ids.sw_syn_this.active = bool(
            self.current_screen.new_readinglist.sw_syn_this_active)
        self.ids.limit_num.error = False
        self.dismiss()
