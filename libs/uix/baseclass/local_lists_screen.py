# -*- coding: utf-8 -*-
#
#
# Copyright © 2017 Easy
#

# LICENSE: MIT

"""

name:local_lists_screen

"""

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    ObjectProperty,
    StringProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.treeview import TreeView, TreeViewLabel, TreeViewNode
from kivymd.toast.kivytoast import toast
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (ILeftBody, ILeftBodyTouch, IRightBodyTouch,
                             OneLineAvatarIconListItem, OneLineIconListItem)
from kivymd.uix.selectioncontrol import MDCheckbox

from libs.utils.comic_server_conn import ComicServerConn
from libs.utils.db_functions import ReadingList


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

    def __init__(self, **kwargs):
        super(TreeViewItem, self).__init__(**kwargs)


class LocalListsScreen(Screen):
    base_url = StringProperty()
    api_url = StringProperty()
    node_list = ListProperty()
    my_tree = ObjectProperty()

    def __init__(self, **kwargs):
        super(LocalListsScreen, self).__init__(**kwargs)
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
        self.my_tree = self.ids.mytv
        if self.node_list:
            for node in self.node_list:
                self.my_tree.remove_node(node)
        self.get_comicrack_list()
        self.app.set_screen('ComicRack Lists')

    def on_leave(self):
        self.app.list_previous_screens.append(self.name)

    def get_comicrack_list(self):
        query = ReadingList.select().where(ReadingList.sw_syn_this_active == True)  # noqa
        self.my_tree.root_options = {'text': 'Synced ReadingLists',
                                     'color': (0, 0, 0, 1), 'font_size': dp(18)
                                     }
        self.my_tree.bind(minimum_height=self.my_tree.setter('height'))
        self.my_tree.bind(on_node_expand=self.node_expand)
        self.my_tree.bind(on_node_collapse=self.node_collapse)
        for item in query:
            new_node = self.my_tree.add_node(TreeViewItem(
                text=item.name, color=(
                    0.9568627450980393, 0.2627450980392157,
                    0.21176470588235294, 1)))
            new_node.rl_slug = item.slug
            new_node.bind(on_touch_down=self.open_readinglist)
            self.node_list.append(new_node)
        self.lists_loaded = False

    def node_expand(self, instance, node):
        node.icon = 'folder-open'

    def node_collapse(self, instance, node):
        node.icon = 'folder'

    def do_expand(self, instance, node):
        self.my_tree.toggle_node(instance)

    def callback_for_menu_items(self, *args):
        toast(args[0])

    def open_readinglist(self, instance, node):
        self.app.manager.current = 'local_readinglists_screen'
        local_readinglists_screen = self.app.manager.get_screen(
            'local_readinglists_screen')
        local_readinglists_screen.setup_screen()
        local_readinglists_screen.page_number = 1
        readinglist_Id = instance.rl_slug
        readinglist_name = (instance.text).split(' : ')[0]
        local_readinglists_screen.list_loaded = False
        query = ReadingList.select().where(ReadingList.slug == readinglist_Id)
        if query.exists():
            Logger.info(f'{readinglist_name} already in Database')
            set_mode = 'From DataBase'
        else:
            Logger.info(
                f'{readinglist_name} not in Database getting info from server')
            set_mode = 'From Server'
        # set_mode = 'From Server'
        local_readinglists_screen.collect_readinglist_data(
            readinglist_name, readinglist_Id, mode=set_mode)
