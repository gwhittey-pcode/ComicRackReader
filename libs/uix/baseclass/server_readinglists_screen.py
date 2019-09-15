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
    BooleanProperty, OptionProperty
from kivy.uix.image import AsyncImage
from kivy.uix.modalview import ModalView
from kivymd.uix.imagelist import SmartTileWithLabel
from kivymd.uix.list import (
    ILeftBody,
    ILeftBodyTouch,
    IRightBodyTouch,
    OneLineIconListItem,
    OneLineAvatarIconListItem,
)

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextFieldRound, FixedHintTextInput
from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
#from libs.utils.server_sync import  SyncReadingListObject

from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.toast.kivytoast.kivytoast import toast
from kivymd.theming import ThemableBehavior
from kivymd.icon_definitions import md_icons
from libs.utils.paginator import Paginator
from kivymd.uix.menu import MDDropdownMenu, MDMenuItem
from libs.uix.baseclass.server_comicbook_screen import ServerComicBookScreen
from kivy.clock import Clock
from functools import partial
from kivy.utils import get_hex_from_color
from kivy.metrics import dp
from libs.utils.comicapi.comicarchive import ComicArchive
from kivy.graphics import BorderImage
from kivy.uix.button import ButtonBehavior
from kivy.uix.popup import Popup
import ntpath
import re


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
        def updated_progress(results, state):
            tmp_txt = self.text
            if state == 'Unread':
                self.img_color = (1, 1, 1, 1)
            elif state == 'Read':
                self.img_color = (.89, .15, .21, 5)

        action = args[0].replace(
            '[color=#000000]', "").replace('[/color]', "")
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
            server_con = ComicServerConn()
            update_url = f'{self.app.api_url}/Comics/{self.comic_obj.Id}/Progress'
            server_con.update_progress(update_url, self.comic_obj.PageCount-1,
                                       callback=lambda req, results:
                                       updated_progress(results, 'Read'))

        elif action == 'Mark as UnRead':
            server_con = ComicServerConn()
            update_url = f'{self.app.api_url}/Comics/{self.comic_obj.Id}/Progress'
            server_con.update_progress(update_url, 0,
                                       callback=lambda req, results:
                                       updated_progress(results, 'Unread'))

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


class CustomMDFillRoundFlatIconButton(MDIconButton):
    def __init__(self, **kwargs):
        _url = ObjectProperty()
        page_num = NumericProperty()
        super(CustomMDFillRoundFlatIconButton, self).__init__(**kwargs)


class SyncButtonIcon(ButtonBehavior, MDIcon):
    icon_name = StringProperty()

    my_clock = ObjectProperty()
    do_action = StringProperty()

    def __init__(self, **kwargs):
        super(SyncButtonIcon, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.menu_items = []
        self.menu_items.append(
            {'viewclass': 'MDMenuItem',
            'text': '[color=#000000]Sync Options[/color]',
            'callback': self.callback_for_menu_items
            }
        )
       


    def callback_for_menu_items(self, *args):
        action = args[0].replace(
            '[color=#000000]', "").replace('[/color]', "")
        if action == "Sync Options":
            # self.app.switch_sync_control()
            self.app.manager.current_screen.open_sync_options()
        elif action == "Start Sync":
            self.do_sync_rf()

    def on_press(self):
        callback = partial(self.menu)
        self.do_action = 'menu'
        Clock.schedule_once(callback, .05)
        self.my_clock = callback

    def menu(self, *args):
        self.do_action = 'menu'

    def on_release(self):
        Clock.unschedule(self.my_clock)
        self.do_action = 'menu'
        return super(SyncButtonIcon, self).on_press()

    def do_sync_rf(self):
        self.app.manager.current_screen.sync_readinglist()


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
        self.sync_options = SyncOptionsPopup(
                        size_hint = (.76,.76),
                        cb_limit_state = self.new_readinglist.cb_limit_state,
                        limit_num_text = str(self.new_readinglist.limit_num),
                        cb_only_read_state = self.new_readinglist.cb_only_read_state,
                        cb_keep_last_read_state = self.new_readinglist.cb_keep_last_read_state,
                        cb_optimize_size_state = self.new_readinglist.cb_optimize_size_state,
                        sw_syn_this_active=bool(self.new_readinglist.sw_syn_this_active),
                        )
        self.sync_options.ids.limit_num.bind(
            on_text_validate=self.sync_options.check_input,
            focus=self.sync_options.check_input,
        )
        
        if self.new_readinglist.sw_syn_this_active == True:
            self.sync_btn_menu_items('add')
        return super().on_enter(*args)
        
        self.sync_options.title = self.new_readinglist.name
    def sync_btn_menu_items(self, action):
        sb = self.ids.sync_button
        if action == 'add':
            
            sb.menu_items.append(
                    {'viewclass': 'MDMenuItem',
                    'text': '[color=#000000]Start Sync[/color]',
                    'callback': self.callback_for_menu_items
                    }
                )
        elif action == 'del':
            sb.menu_items.pop()
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
            self.ids.main_grid.children[-1], padding=10, animate=True)

    def build_page(self, object_lsit):
        grid = self.m_grid
        main_stack = self.main_stack
        grid.clear_widgets()
        for comic in object_lsit:
            c = CustomeST(id=comic.Id)
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
            
            strtxt = f"{comic.Series} #{comic.Number}"
            if comic.UserLastPageRead == comic.PageCount-1:
                c.img_color = (.89, .15, .21, 5)
                #txt_color = get_hex_from_color((.89, .15, .21, 1))
                txt_color = get_hex_from_color((1, 1, 1, 1))
            else:
                txt_color = get_hex_from_color((1, 1, 1, 1))
            c.text = f'[color={txt_color}]{strtxt}[/color]'
            grid.add_widget(c)
            grid.cols = (Window.width-10)//self.comic_thumb_width
            self.ids.page_count.text = f'Page #\n{self.current_page.number} of {self.paginator_obj.num_pages()}'
            
            
    def got_json(self, req, results):
        
        self.new_readinglist = ComicReadingList(
            name=self.readinglist_name, data=results, slug=self.readinglist_Id)
        for item in self.new_readinglist.comic_json:
            comic_index = self.new_readinglist.comic_json.index(item)
            new_comic = ComicBook(item,readlist_obj=self.new_readinglist,comic_index=comic_index)
            self.new_readinglist.add_comic(new_comic)
            
     
        self.max_books_page = int(self.app.config.get(
            'General', 'max_books_page'))
        #self.sync_object = SyncReadingListObject(reading_list=self.new_readinglist)
        orphans = self.max_books_page - 1
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

    def open_sync_options(self):
        self.sync_options.open()

    def sync_readinglist(self):
        self.sync_object.sync_readinglist()


class SyncOptionsPopup(Popup):
    background = 'assets/cPop_bkg.png'
    text = StringProperty('')
    cb_limit_state = StringProperty()
    limit_num_text = StringProperty()
    cb_only_read_state = StringProperty()
    cb_keep_last_read_state = StringProperty()
    cb_optimize_size_state = StringProperty()
    sw_syn_this_active = BooleanProperty(False)
    ok_text = StringProperty('OK')
    cancel_text = StringProperty('Cancel')
    
    __events__ = ('on_ok', 'on_cancel')
    def __init__(self, **kwargs):
        super(SyncOptionsPopup, self).__init__(**kwargs)
        app = App.get_running_app()
        self.current_screen = app.manager.current_screen
       
    def check_input(self,*args):
        text_field = args[0]
        if text_field.text.isnumeric():
            text_field.error = False
            return True
        else:
            text_field.error = True
            return False
    
    
    def on_open(self):
        #self.sw_syn_this.active=bool(self.current_screen.new_readinglist.sw_syn_this_active)
        """ disable hotkeys while we do this"""
        Window.unbind(on_keyboard=App.get_running_app().events_program)
    def on_dismiss(self):
        Window.bind(on_keyboard=App.get_running_app().events_program)

    def on_ok(self):
        chk_input = self.check_input(self.ids.limit_num)
        if chk_input is True:
            self.current_screen.new_readinglist.save_settings(
                cb_limit_state = self.ids.cb_limit.state,
                limit_num = int(self.ids.limit_num.text),
                cb_only_read_state = self.ids.cb_only_read.state,
                cb_keep_last_read_state = self.ids.cb_keep_last_read.state,
                cb_optimize_size_state = self.ids.cb_optimize_size.state,
                sw_syn_this_active = self.ids.sw_syn_this.active,
            )
            if self.ids.sw_syn_this.active is False:
                self.current_screen.sync_btn_menu_items('del')
            elif self.ids.sw_syn_this.active is True:
                self.current_screen.sync_btn_menu_items('add')
            self.dismiss()
            
                
        else:
            self.ids.limit_num.focus = True
            return
    def on_cancel(self):
        self.ids.cb_limit.state = self.current_screen.new_readinglist.cb_limit_state
        self.ids.limit_num.text = str(self.current_screen.new_readinglist.limit_num)
        self.ids.cb_only_read.state = self.current_screen.new_readinglist.cb_only_read_state
        self.ids.cb_keep_last_read.state = self.current_screen.new_readinglist.cb_keep_last_read_state
        self.ids.cb_optimize_size.state = self.current_screen.new_readinglist.cb_optimize_size_state
        self.ids.sw_syn_this.active=bool(self.current_screen.new_readinglist.sw_syn_this_active)
        self.ids.limit_num.error = False
        self.dismiss()
