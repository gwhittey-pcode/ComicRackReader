# -*- coding: utf-8 -*-
#
#
# Copyright © 2017 Easy
#

# LICENSE: MIT

"""

name:server_lists_screen

"""

from kivy.uix.screenmanager import Screen
from libs.utils.comic_server_conn import ComicServerConn
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import ILeftBodyTouch, ILeftBody
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.uix.image import Image
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivy.app import App
from kivymd.uix.dialog import MDDialog
from kivy.logger import Logger
from kivy.clock import Clock
from libs.utils.db_functions import ReadingList
from kivymd.uix.list import (
    ILeftBody,
    ILeftBodyTouch,
    IRightBodyTouch,
    OneLineIconListItem,
    OneLineAvatarIconListItem,
)
from kivymd.toast.kivytoast import toast


class MyTv(TreeView):
    def __init__(self, **kwargs):
        super(MyTv, self).__init__(**kwargs)

    def on_node_expand(self, node):
        node.icon = 'folder-open'


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class TreeViewFolder(OneLineIconListItem, TreeViewNode):
    text = StringProperty()
    color = ListProperty([1, 1, 0.4, 1])
    icon = StringProperty('folder')

    def __init__(self, **kwargs):
        super(TreeViewFolder, self).__init__(**kwargs)


class TreeViewItem(OneLineIconListItem, TreeViewNode):
    text = StringProperty()
    color = ListProperty([0.4, 0.4, 0.4, 1])
    icon = StringProperty('view-list')
    rl_slug = StringProperty()

    def __init__(self, **kwargs):
        super(TreeViewItem, self).__init__(**kwargs)


class ServerListsScreen(Screen):
    base_url = StringProperty()
    api_url = StringProperty()

    def __init__(self, **kwargs):
        super(ServerListsScreen, self).__init__(**kwargs)
        self.lists_loaded = BooleanProperty()
        self.lists_loaded = False
        self.app = App.get_running_app()
        self.fetch_data = None
        self.Data = ''
        self.fetch_data = ComicServerConn()
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url

    def on_pre_enter(self):
        self.app.show_action_bar()

    def on_enter(self, *args):
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        if self.lists_loaded is False:
            self.get_comicrack_list()
        self.app.set_screen('ComicRack Lists')

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def get_comicrack_list(self):
        if self.lists_loaded is False:
            url_send = f'{self.api_url}/lists/'
            self.fetch_data.get_server_data(url_send, self)

    def node_expand(self, instance, node):
        node.icon = 'folder-open'

    def node_collapse(self, instance, node):
        node.icon = 'folder'

    def do_expand(self, instance, node):
        self.my_tree.toggle_node(instance)

    def callback_for_menu_items(self, *args):
        toast(args[0])

    def open_readinglist(self, instance, node):

        server_readinglists_screen = self.app.manager.get_screen(
            'server_readinglists_screen')
        server_readinglists_screen.setup_screen()
        server_readinglists_screen.page_number = 1
        readinglist_Id = instance.id
        readinglist_name = (instance.text).split(' : ')[0]
        server_readinglists_screen.list_loaded = False
        query = ReadingList.select().where(ReadingList.slug == readinglist_Id)
        if query.exists():
            Logger.info(f'{readinglist_name} already in Database')
            set_mode = 'From DataBase'
        else:
            Logger.info(
                f'{readinglist_name} not in Database getting info from server')
            set_mode = 'From Server'
        # set_mode = 'From Server'

        server_readinglists_screen.collect_readinglist_data(
            readinglist_name, readinglist_Id, mode=set_mode)
        self.app.manager.current = 'server_readinglists_screen'

    def got_json(self, req, result):
        self.ids.mytv.clear_widgets()
        self.my_tree = self.ids.mytv
        self.my_tree.clear_widgets()
        self.my_tree.bind(minimum_height=self.my_tree.setter('height'))
        self.my_tree.bind(on_node_expand=self.node_expand)
        self.my_tree.bind(on_node_collapse=self.node_collapse)
        for item in result:
            if item['Name'] != 'Library':
                if item['Type'] == "ComicLibraryListItem" or\
                        item['Type'] == "ComicSmartListItem":
                    new_node = self.my_tree.add_node(TreeViewItem(
                        text=item['Name'], color=(
                            0.9568627450980393, 0.2627450980392157,
                            0.21176470588235294, 1), id=item['Id']))
                    new_node.bind(on_touch_down=self.open_readinglist)
                elif item['Type'] == "ComicListItemFolder":
                    parent = self.my_tree.add_node(
                        TreeViewFolder(text=item['Name'], color=(
                            0.9568627450980393, 0.2627450980392157,
                            0.21176470588235294, 1), id=item['Id']))
                    parent.bind(on_touch_down=self.do_expand)
                    self.set_files(parent, item['Lists'])
            self.lists_loaded = True

    def set_files(self, parent, child):
        for item in child:
            if item['Type'] == "ComicLibraryListItem" or\
                    item['Type'] == "ComicSmartListItem" or\
                    item['Type'] == "ComicIdListItem":
                new_node = self.my_tree.add_node(TreeViewItem(
                    text=item['Name'], color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']), parent)
                new_node.bind(on_touch_down=self.open_readinglist)
            elif item['Type'] == "ComicListItemFolder":
                sub_parent = self.my_tree.add_node(TreeViewFolder(
                    text=item['Name'], color=(
                        0.9568627450980393, 0.2627450980392157,
                        0.21176470588235294, 1), id=item['Id']), parent)
                sub_parent.bind(on_touch_down=self.do_expand)
                self.set_files(sub_parent, item['Lists'])
