# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

###
# LICENSE: MIT
"""
FIXME: add in settings change update all app settings

"""
import sys
import os
from pathlib import Path
from ast import literal_eval
from shutil import copyfile
from kivymd.uix.dialog import MDDialog

# from kivymd.app import MDApp
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.config import ConfigParser
from kivy.clock import Clock
from kivy.utils import get_hex_from_color

from kivy.properties import (
    ObjectProperty,
    StringProperty,
    ListProperty,
    NumericProperty,
    BooleanProperty,
)
from libs.uix.baseclass.startscreen import StartScreen
from kivy.logger import Logger
from kivymd.theming import ThemeManager
from kivymd.toast.kivytoast import toast
from kivymd.uix.filemanager import MDFileManager
from libs.utils.db_functions import start_db

# from dialogs import card
# End KivyMD imports
from settings.settingsjson import (
    settings_json_server,
    settings_json_dispaly,
    settings_json_screen_tap_control,
    settings_json_hotkeys,
    settings_json_sync,
)
from settings.custom_settings import MySettings

from libs.utils.comic_functions import convert_comicapi_to_json
from libs.utils.paginator import Paginator
from libs.utils.comic_json_to_class import ComicReadingList, ComicBook
from libs.uix.widgets.mytoolbar import MDToolbarTooltips
from kivy.factory import Factory


class ComicRackReader(MDApp):
    nav_drawer = ObjectProperty()
    lang = StringProperty("en")
    open_comics_list = ListProperty()
    sync_folder = StringProperty()
    full_screen = False
    LIST_SCREENS = ListProperty()
    store_dir = StringProperty()
    comic_db = ObjectProperty()
    username = StringProperty()
    password = StringProperty()
    api_key = StringProperty()
    max_books_page = NumericProperty()
    open_last_comic_startup = NumericProperty()
    how_to_open_comic = StringProperty()
    app_started = BooleanProperty(False)
    open_comic_screen = StringProperty()
    sync_is_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = "below_target"
        self.LIST_SCREENS = [
            "base",
            "license",
            "about",
            "server_lists_screen",
            "syncscreen",
            "server_readinglists_screen",
            "single_file_screen",
            "open_file_screen",
        ]

        self.list_previous_screens = ["base"]
        self.window = Window
        self.config = ConfigParser()
        self.manager = None
        self.window_language = None
        self.exit_interval = False
        self.comic_thumb_height = 240
        self.comic_thumb_width = 156
        self.dict_language = literal_eval(
            open(
                os.path.join(self.directory, "data", "locales", "locales.txt")
            ).read()
        )
        # self.translation = Translation(
        #     self.lang, 'Ttest', os.path.join(self.directory,
        # data', 'locales')
        # )
        self.base_url = ""
        self.settings_cls = MySettings
        self.md_manager = None
        self.open_comic_screen = ""

    # def get_application_config(self):
    #     return super(ComicRackReader, self).get_application_config(
    #         '{}/%(appname)s.ini'.format(self.directory))

    def build_config(self, config):
        """Creates an application settings file ComicRackReader.ini."""

        config.adddefaultsection("Language")
        config.adddefaultsection("Saved")
        config.setdefault("Language", "language", "en")

        config.setdefault("Saved", "last_comic_id", "")
        config.setdefault("Saved", "last_comic_type", "")
        config.setdefault("Saved", "last_reading_list_id", "")
        config.setdefault("Saved", "last_reading_list_name", "")
        config.setdefault("Saved", "last_pag_pagnum", "")

        config.setdefaults(
            "General",
            {
                "base_url": "http://",
                "storagedir": self.user_data_dir,
                "use_api_key": 0,
                "api_key": "",
                "username": "",
                "password": "",
                "open_last_comic_startup": 0,
                "how_to_open_comic": "Open Local Copy",
                # 'use_pagination':   '1',
                "max_books_page": 25,
            },
        )
        config.setdefaults(
            "Sync", {"sync_folder": self.user_data_dir, "max_num_sync": 50}
        )
        config.setdefaults(
            "Display",
            {
                "mag_glass_size": 200,
                "right2left": 0,
                "dblpagesplit": "0",
                "stretch_image": "0",
                "keep_ratio": "0",
                "reading_list_icon_size": "Small",
                "max_comic_pages_limit": 50,
                "max_height": 1500,
            },
        )

        config.setdefaults(
            "Screen Tap Control",
            {
                "bottom_right": "Next Page",
                "bottom_left": "Prev Page",
                "bottom_center": "Open Page Nav",
                "top_right": "Return to Home Screen",
                "top_left": "Precodv Page",
                "top_center": "Open Collection Browser",
                "middle_right": "None",
                "middle_left": "None",
                "middle_center": "Open NavBar",
                "dbl_tap_time": 250,
            },
        )

        config.setdefaults(
            "Hotkeys",
            {
                "hk_next_page": ".",
                "hk_prev_page": ",",
                "hk_open_page_nav": "p",
                "hk_open_collection": "j",
                "hk_return_comic_list": "c",
                "hk_return_base_screen": "r",
                "hk_toggle_navbar": "n",
                "hk_toggle_fullscreen": "f",
            },
        )

    def set_value_from_config(self, *args):
        """Sets the values of variables from the settings
        file ComicRackReader.ini."""
        self.config.read(os.path.join(self.directory, "comicrackreader.ini"))
        self.lang = self.config.get("Language", "language")
        self.sync_folder = self.config.get("Sync", "sync_folder")
        self.store_dir = os.path.join(
            self.config.get("General", "storagedir"), "store_dir"
        )
        if not Path(self.store_dir).is_dir():
            os.makedirs(self.store_dir)
        self.base_url = self.config.get("General", "base_url").rstrip("\\")
        print(f"self.base_url:{self.base_url}")
        self.api_key = self.config.get("General", "api_key")
        self.username = self.config.get("General", "username")
        self.password = self.config.get("General", "password")

        self.api_url = self.base_url + "/API"
        self.my_data_dir = os.path.join(self.store_dir, "comics_db")

        if not os.path.isdir(self.my_data_dir):
            os.makedirs(self.my_data_dir)

        self.max_books_page = int(self.config.get("General", "max_books_page"))
        self.open_last_comic_startup = self.config.get(
            "General", "open_last_comic_startup"
        )
        self.how_to_open_comic = self.config.get(
            "General", "how_to_open_comic"
        )

    def config_callback(self, section, key, value):
        if key == "storagedir":

            def __callback_for_please_wait_dialog(*args):
                if args[0] == "Delete Database":
                    self.stop()
                elif args[0] == "Move Database":
                    print("move")
                    db_folder = self.my_data_dir
                    old_dbfile = os.path.join(db_folder, "ComicRackReader.db")
                    store_dir = os.path.join(value, "store_dir")
                    new_data_dir = os.path.join(store_dir, "comics_db")
                    new_dbfile = os.path.join(
                        new_data_dir, "ComicRackReader.db"
                    )
                    if not os.path.isdir(store_dir):
                        os.makedirs(store_dir)
                    if not os.path.isdir(new_data_dir):
                        os.makedirs(new_data_dir)
                    copyfile(old_dbfile, new_dbfile)
                    self.stop()

            self.please_wait_dialog = MDDialog(
                title="Please Restart ComicRackReader",
                size_hint=(0.8, 0.4),
                text_button_ok="Delete Database",
                text_button_cancel="Move Database",
                text=f"Storage/Databse dir changed Delete Data or Move it to new dir \nApp will Close please restart it for new setting to take effect?",
                events_callback=__callback_for_please_wait_dialog,
            )
            self.please_wait_dialog.open()
        else:
            config_items = {
                "base_url": "base_url",
                "api_key": "api_key",
                "sync_folder": "sync_folder",
                "password": "password",
                "username": "username",
                "max_books_page": "max_books_page",
                "sync_folder": "sync_folder",
            }
            item_list = list(config_items.keys())
            if key in item_list:
                item = config_items[key]
                setattr(self, item, value)
            self.api_url = self.base_url + "/API"
            # self.my_data_dir = os.path.join(self.store_dir, 'comics_db')

    def build(self):
        r = Factory.register
        r("MDToolbarTooltips", module="libs.uix.widgets.mytoolbar")
        self.set_value_from_config()
        from libs.uix.baseclass.basescreen import BaseScreen
        from libs.uix.baseclass.about import About
        from libs.uix.baseclass.local_lists_screen import LocalListsScreen
        from libs.uix.baseclass.local_readinglists_screen import (
            LocalReadingListsScreen,
        )
       # from libs.uix.baseclass.navdrawer import NavDrawer
        from libs.uix.baseclass.server_comicbook_screen import (
            ServerComicBookScreen,
        )
        from libs.uix.baseclass.server_lists_screen import ServerListsScreen
        from libs.uix.baseclass.server_readinglists_screen import (
            ServerReadingListsScreen,
        )
        from libs.uix.baseclass.license import License
        from libs.uix.lists import SingleIconItem

        start_db()
        path = os.path.dirname(__file__)
        icon_path = os.path.join(path, f"data{os.sep}")
        self.icon = os.path.join(icon_path, f"icon.png")
        self.title = "ComicRackReader 1.2.4"
        self.theme_cls.primary_palette = "Amber"
        self.load_all_kv_files(
            os.path.join(self.directory, "libs", "uix", "kv")
        )
        self.screen = StartScreen()  # program main screen
        self.manager = self.screen.ids.manager
        action_bar = self.screen.ids.action_bar
        # Left side Action bar Icons
        action_bar.left_action_items = [
            ["home", "Home", lambda x: self.switch_base_screen()],
            ["settings", "Settings", lambda x: self.open_settings()],
            ["fullscreen", "Full Screen", lambda x: self.toggle_full_screen()],
        ]
        # right side Action bar Icons
        action_bar.right_action_items = [
            ["file-cabinet", "Open File", lambda x: self.file_manager_open()],
            [
                "server",
                "ComicRack Reading Lists",
                lambda x: self.switch_server_lists_screen(),
            ],
            [
                "view-list",
                "Current Server Reading List",
                lambda x: self.switch_readinglists_screen(),
            ],
            [
                "folder-sync",
                "Local Reading Lists",
                lambda x: self.switch_local_lists_screen(),
            ],
            [
                "playlist-check",
                "Current Local Reading List",
                lambda x: self.switch_local_readinglists_screen(),
            ],
            [
                "book-open-page-variant",
                "Open Comic Book",
                lambda x: self.switch_comic_reader(),
            ],
            ["close-box-outline", "Exit App", lambda x: self.stop()],
        ]
        self.config.add_callback(self.config_callback)
        return self.screen

    def load_all_kv_files(self, directory_kv_files):
        for kv_file in os.listdir(directory_kv_files):
            kv_file = os.path.join(directory_kv_files, kv_file)
            if os.path.isfile(kv_file):
                with open(kv_file, encoding="utf-8") as kv:
                    Builder.load_string(kv.read())

    def on_config_change(self, config, section, key, value):
        pass

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        c = Keyboard()
        """Called when you press a Key"""
        app = App.get_running_app()
        current_screen = app.manager.current_screen
        hk_next_page = app.config.get("Hotkeys", "hk_next_page")
        hk_prev_page = app.config.get("Hotkeys", "hk_prev_page")
        hk_open_page_nav = app.config.get("Hotkeys", "hk_open_page_nav")
        hk_open_collection = app.config.get("Hotkeys", "hk_open_collection")
        hk_return_comic_list = app.config.get(
            "Hotkeys", "hk_return_comic_list"
        )
        hk_return_base_screen = app.config.get(
            "Hotkeys", "hk_return_base_screen"
        )
        hk_toggle_navbar = app.config.get("Hotkeys", "hk_toggle_navbar")

        hk_toggle_fullscreen = app.config.get(
            "Hotkeys", "hk_toggle_fullscreen"
        )
        Logger.debug(f"keyboard:{keyboard}")
        if current_screen.name not in self.LIST_SCREENS:
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
            elif keyboard == c.string_to_keycode(hk_return_comic_list):
                app.switch_readinglists_screen()
            elif keyboard == c.string_to_keycode(hk_return_base_screen):
                app.show_action_bar()
                app.manager.current = "base"
            elif keyboard in (1001, 27):
                if self.nav_drawer.state == "open":
                    self.nav_drawer.toggle_nav_drawer()
                self.back_screen(event=keyboard)
            elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
                self.toggle_full_screen()
        else:
            if keyboard in (282, 319):
                pass
            elif keyboard == c.string_to_keycode(hk_toggle_fullscreen):
                self.toggle_full_screen()
            elif keyboard == c.string_to_keycode(hk_return_comic_list):
                app.manager.current = "server_readinglists_screen"
            elif keyboard == c.string_to_keycode(hk_return_base_screen):
                app.show_action_bar()
                app.switch_base_screen()
            elif keyboard in (1001, 27):
                if self.nav_drawer.state == "open":
                    self.nav_drawer.toggle_nav_drawer()
                self.back_screen(event=keyboard)
        return True

    def toggle_full_screen(self):
        if App.get_running_app().full_screen is False:
            Window.fullscreen = "auto"
            App.get_running_app().full_screen = True
        else:
            App.get_running_app().full_screen = False
            Window.fullscreen = False

    def back_screen(self, event=None):
        """Screen manager Called when the Back Key is pressed."""
        # BackKey pressed.
        if event in (1001, 27):
            if self.manager.current == "base":
                self.dialog_exit()
                return
            try:
                self.manager.current = self.list_previous_screens.pop()
            except:  # noqa
                self.manager.current = "base"
            # self.screen.ids.action_bar.title = self.title

    def show_license(self, *args):
        self.screen.ids.license.ids.text_license.text = ("%s") % open(
            os.path.join(self.directory, "LICENSE"), encoding="utf-8"
        ).read()

        self.nav_drawer._toggle()
        self.manager.current = "license"
        self.screen.ids.action_bar.left_action_items = [
            ["chevron-left", lambda x: self.back_screen(27)]
        ]
        self.screen.ids.action_bar.title = "MIT LICENSE"

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)

        Clock.schedule_interval(check_interval_press, 1)
        toast("Press Back to Exit")

    def on_lang(self, instance, lang):
        self.translation.switch_lang(lang)

    def build_settings(self, settings):
        settings.add_json_panel(
            "Sync Settings", self.config, data=settings_json_sync
        )
        settings.add_json_panel(
            "General Settings", self.config, data=settings_json_server
        )

        settings.add_json_panel(
            "Display Settings", self.config, data=settings_json_dispaly
        )
        settings.add_json_panel(
            "Screen Tap Control",
            self.config,
            data=settings_json_screen_tap_control,
        )
        settings.add_json_panel(
            "Hotkeys", self.config, data=settings_json_hotkeys
        )

    def switch_server_lists_screen(self):
        self.set_screen("List of Reading Lists Screen")
        self.manager.current = "server_lists_screen"

    def switch_readinglists_screen(self):
        screen = self.manager.get_screen("server_readinglists_screen")
        self.set_screen(screen.reading_list_title)
        self.manager.current = "server_readinglists_screen"

    def switch_local_readinglists_screen(self):
        screen = self.manager.get_screen("local_readinglists_screen")
        self.set_screen(screen.reading_list_title)
        self.manager.current = "local_readinglists_screen"

    def switch_comic_reader(self):
        if self.open_comic_screen:
            self.manager.current = "comic_book_screen"
        else:
            toast("No ComicBook Open")

    def switch_base_screen(self):
        self.set_screen("ComicRackReader Home Screen")
        self.manager.current = "base"

    def switch_local_lists_screen(self):
        self.set_screen("Local Sync Comics")
        self.manager.current = "local_lists_screen"

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
            Window.width,
            self.theme_cls.standard_increment,
        )

    # FileManger
    def file_manager_open(self):
        previous = False
        if not self.md_manager:
            self.md_manager = ModalView(size_hint=(1, 1), auto_dismiss=False)
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.select_path,
                previous=previous,
            )
            self.md_manager.add_widget(self.file_manager)

            self.file_manager.show(self.sync_folder)
        self.manager_open = True
        self.md_manager.open()

    def select_path(self, path):
        """It will be called when you click on the file name
        or the catalog selection button.
        :type path: str;
        :param path: path to the selected directory or file;
        """
        has_cb_files = False
        self.exit_manager()
        if os.path.isfile(path):
            ext = os.path.splitext(path)[-1].lower()
            if ext in (".cbz", ".cbr", ".cb7", ".cbp"):
                has_cb_files = True
                data = {"items": []}
                comic_data = convert_comicapi_to_json(path)
                data["items"].append(comic_data)
                new_rl = ComicReadingList(
                    name="Single_FileLoad",
                    data=data,
                    slug="FileOpen",
                    mode="FileOpen",
                )
                new_comic = ComicBook(data["items"][0], mode="FileOpen")
                new_rl.add_comic(new_comic)
            else:
                pass
        elif os.path.isdir(path):
            if os.path.isdir(path):
                onlyfiles = [
                    f
                    for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))
                ]
            data = {"items": []}
            for file in onlyfiles:
                ext = os.path.splitext(file)[-1].lower()
                if ext in (".cbz", ".cbr", ".cb7", ".cbp"):
                    file_path = os.path.join(path, file)
                    comic_data = convert_comicapi_to_json(file_path)
                    data["items"].append(comic_data)
                    has_cb_files = True
                else:
                    pass
            if has_cb_files is True:
                new_rl = ComicReadingList(
                    name=path, data=data, slug="path", mode="FileOpen"
                )
                for item in new_rl.comic_json:
                    comic_index = new_rl.comic_json
                    new_comic = ComicBook(
                        item,
                        readinglist_ob=new_rl,
                        comic_index=comic_index,
                        mode="FileOpen",
                    )
                    new_rl.add_comic(new_comic)
        if has_cb_files is True:
            max_books_page = int(self.config.get("General", "max_books_page"))
            paginator_obj = Paginator(new_rl.comics, max_books_page)
            screen = self.manager.get_screen("comic_book_screen")
            screen.setup_screen(
                readinglist_obj=new_rl,
                comic_obj=new_rl.comics[0],
                paginator_obj=paginator_obj,
                pag_pagenum=1,
                view_mode="FileOpen",
            )
            self.manager.current = "comic_book_screen"
            toast(f"Opening {new_rl.comics[0].__str__}")
        else:
            toast("A vaild ComicBook File was not found")
        self.md_manager = None

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""

        self.md_manager.dismiss()
        self.manager_open = False

    def delayed_work(self, func, items, delay=0):
        """Apply the func() on each item contained in items
        """
        if not items:
            return

        def _sync_delayed_work(*l):
            item = items.pop(0)
            if func(item) is False or not len(items):
                return False
            Clock.schedule_once(_sync_delayed_work, delay)

        Clock.schedule_once(_sync_delayed_work, delay)


c = ComicRackReader()
c.run()
