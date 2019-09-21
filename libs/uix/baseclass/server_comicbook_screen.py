# -*- coding: utf-8 -*-
#

#
# Copyright © 2017 Easy
#

# LICENSE: MIT

"""

name:server_comicbook_screen

"""
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty,\
    NumericProperty, BooleanProperty, DictProperty
from libs.utils.comic_server_conn import ComicServerConn
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.modalview import ModalView
from settings.settingsjson import settings_json_screen_tap_control
from libs.uix.widgets.comicbook_screen_widgets import ComicBookPageImage,\
    ComicBookPageThumb, ComicBookPageScatter, ComicCarousel,\
    ComicBookPageControlButton, ThumbPopPageInnerGrid,\
    ThumbPopPagebntlbl, CommonComicsScroll, CommonComicsOuterGrid,\
    CommonComicsCoverInnerGrid, CommonComicsCoverImage, \
    CommonComicsCoverLabel
from kivymd.toast.kivytoast import toast
from kivymd.uix.dialog import MDDialog
from kivy.loader import Loader
import json
from kivymd.uix.toolbar import MDToolbar
from kivy.core.window import Window
from libs.utils.comic_functions import get_comic_page, get_file_page_size
from kivy.clock import Clock
from libs.utils.db_functions import ReadingList,Comic
class ServerComicBookScreen(Screen):
    scroller = ObjectProperty()
    top_pop = ObjectProperty()
    section = StringProperty()
    sort_by = StringProperty()
    last_load = NumericProperty()
    str_page_count = StringProperty()
    full_screen = BooleanProperty()
    next_nav_comic_thumb = ObjectProperty()
    prev_nav_comic_thumb = ObjectProperty()
    pag_pagenum = NumericProperty()
    view_mode = StringProperty()
    dynamic_ids = DictProperty({})    # declare class attribute, dynamic_ids

    def __init__(self, readinglist_obj=None, comic_obj=None, view_mode='Server',
                 paginator_obj=None, pag_pagenum=1, last_load=0, ** kwargs):
        super(ServerComicBookScreen, self).__init__(**kwargs)
        self.fetch_data = None
        self.app = App.get_running_app()
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.current_page = None
        self.comic_obj = ObjectProperty()
        self.comic_obj = None
        self.paginator_obj = ObjectProperty()
        self.paginator_obj = None
        self.fetch_data = ComicServerConn()
        self.api_key = self.app.config.get('General', 'api_key')
        self.popup_bkcolor = (.5, .5, .5, .87)
        self.last_load = last_load
        self.full_screen = False
        self.option_isopen = False
        self.next_dialog_open = False
        self.prev_dialog_open = False
        config_app = App.get_running_app()
        settings_data = json.loads(settings_json_screen_tap_control)
       # Window.bind(on_keyboard=self.events_program)
        for setting in settings_data:
            if setting['type'] == 'options':
                tap_config = config_app.config.get(setting[u'section'],
                                                   setting[u'key'])
                if tap_config == 'Disabled':
                    self.ids[setting[u'key']].disabled = True

        self.readinglist_obj = readinglist_obj
        self.comic_obj = comic_obj
        self.paginator_obj = paginator_obj
        self.view_mode = view_mode
        self.app.config.write()
        self.pag_pagenum = pag_pagenum
        if self.view_mode == 'FileOpen':
            self.app.config.set('Saved', 'last_file_comic_id',
                                self.comic_obj.FilePath)
            self.app.config.set(
                'Saved', 'last_file_reading_list_id', self.readinglist_obj.slug)
            self.app.config.set(
                'Saved', 'last_file_reading_list_name', self.readinglist_obj.name)
            if int(self.pag_pagenum):
                self.app.config.set(
                    'Saved', 'last_file_pag_pagnum', self.pag_pagenum)
        else:
            self.app.config.set(
                'Saved', 'last_server_comic_id', self.comic_obj.Id)

            self.app.config.set(
                'Saved', 'last_server_reading_list_id', self.readinglist_obj.slug)
            self.app.config.set(
                'Saved', 'last_server_reading_list_name', self.readinglist_obj.name)
            if int(self.pag_pagenum):
                self.app.config.set(
                    'Saved', 'last_server_pag_pagnum', self.pag_pagenum)
        self.app.config.write()
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:
            self.scroller.clear_widgets()
        if self.top_pop:
            self.top_pop.clear_widgets()
        number_pages = int(comic_obj.PageCount)
        max_comic_pages_limit = int(App.get_running_app().config.get(
            'Display', 'max_comic_pages_limit'))
        if number_pages <= max_comic_pages_limit:
            x_title = 'Pages 1 to %s of %s ' % (number_pages, number_pages)
        else:
            if self.last_load == 0:
                x_title = 'Pages 1 to %s of %s ' % (
                    max_comic_pages_limit, number_pages)
            else:
                x_title = 'Pages %s to %s of %s ' % (
                    max_comic_pages_limit, (self.last_load +
                                            max_comic_pages_limit),
                    number_pages)
        self.str_page_count = x_title
        x_title = f'{self.comic_obj.__str__} {x_title}'
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True,
                            do_scroll_y=False, id='page_thumb_scroll',
                            scroll_type=['bars', 'content']
                            )
        self.dynamic_ids['page_thumb_scroll'] = scroll
        t_y = round(dp(320))
        self.page_nav_popup = Popup(id='page_nav_popup', title=x_title,
                                    pos_hint={'y': 0},
                                    size_hint=(1, None),
                                    height=round(dp(320))
                                    )
        self.dynamic_ids['page_nav_popup'] = self.page_nav_popup
        self.page_nav_popup.add_widget(scroll)
        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None, None), spacing=(5, 0),
                                padding=(5, 1), id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        i = 0
        self.use_sections = False
        if number_pages <= max_comic_pages_limit:
            self.use_sections = False
            for i in range(0, number_pages):
                self.add_pages(comic_book_carousel, outer_grid, comic_obj, i)
                if i == comic_obj.UserCurrentPage:
                    m_UserCurrentPage = 'comic_scatter'+str(i)
        else:
            self.use_sections = True
            if self.last_load == 0:
                z = max_comic_pages_limit
                for i in range(0, number_pages)[0:z]:
                    self.add_pages(comic_book_carousel,
                                   outer_grid, comic_obj, i)
                self.last_load = max_comic_pages_limit
                self.last_section = 0
                if i == comic_obj.UserCurrentPage:
                    m_UserCurrentPage = 'comic_scatter'+str(i)
            else:
                z = self.last_load + max_comic_pages_limit
                for i in range(0, number_pages)[self.last_load:z]:
                    self.add_pages(comic_book_carousel,
                                   outer_grid, comic_obj, i)
                    if i == comic_obj.UserCurrentPage:
                        m_UserCurrentPage = 'comic_scatter'+str(i)
                if (self.last_load - max_comic_pages_limit) >= 0:
                    self.last_section = (
                        self.last_load - max_comic_pages_limit)
                self.last_load = self.last_load + max_comic_pages_limit

            if self.use_sections:
                if i+1 >= number_pages:
                    self.use_sections = False
                    self.section = 'Last'
                elif i+1 == max_comic_pages_limit:
                    self.section = 'First'
                else:
                    self.section = 'Section'

        scroll.add_widget(outer_grid)
        self.build_top_nav()
        self.next_comic = self.get_next_comic()
        self.prev_comic = self.get_prev_comic()
        self.build_next_comic_dialog()
        self.build_prev_comic_dialog()

    def toggle_full_screen(self):
        if self.full_screen == False:
            Window.fullscreen = True
            self.full_screen == True
        else:
            Window.fullscreen = False

    def open_mag_glass(self):
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        current_slide.open_mag_glass()

    def on_pre_enter(self):
        self.app.hide_action_bar()
        self.build_option_pop()

    def on_pre_leave(self, *args):
        self.top_pop.dismiss()
        self.page_nav_popup.dismiss()
        self.option_pop.dismiss()

    def on_leave(self, *args):

        self.app.manager.remove_widget(self)
        self = None

    def load_UserCurrentPage(self):
        for slide in self.ids.comic_book_carousel.slides:
            if slide.comic_page == self.comic_obj.UserCurrentPage:
                self.ids.comic_book_carousel.load_slide(slide)

    def slide_changed(self, index):
        if self.view_mode == 'FileOpen' or self.comic_obj.is_sync:
            if index is not None:
                def __update_page(key_val=None):
                    db_item = Comic.get(Comic.Id == self.comic_obj.Id)
                    for key, value in key_val.items():
                        setattr(db_item,key,value)
                        setattr(self.comic_obj,key,value)
                    db_item.save()
                comic_book_carousel = self.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                current_page = comic_book_carousel.current_slide.comic_page
                comic_obj = self.comic_obj
                comic_Id = comic_obj.Id
                if self.comic_obj.is_sync:
                    if current_page > self.comic_obj.UserLastPageRead:
                        key_val = {
                        'UserLastPageRead' :current_page,
                        'UserCurrentPage':current_page
                        }
                    else:
                        key_val = {'UserCurrentPage':current_page}
                    Clock.schedule_once(lambda dt, key_value={}:__update_page(key_val=key_val), 0.15)
                prev_id = f'comic_scatter{current_page-1}'
                next_id = f'comic_scatter{current_page+1}'
                p_slide = comic_book_carousel.previous_slide
                for slide in comic_book_carousel.slides:
                    for child in slide.walk():
                        if child.id is not None:
                            if "comic_scatter" in child.id:
                                if child.zoom_state == 'zoomed':
                                    child.do_zoom(False)
        else:
            def updated_progress(results):
                pass
            if index is not None:
                comic_book_carousel = self.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                current_page = comic_book_carousel.current_slide.comic_page
                comic_obj = self.comic_obj
                comic_Id = comic_obj.Id
                prev_id = f'comic_scatter{current_page-1}'
                next_id = f'comic_scatter{current_page+1}'
                update_url = f'{self.api_url}/Comics/{comic_Id}/Progress'
                self.fetch_data.update_progress(update_url, current_page,
                                                callback=lambda req, results:
                                                updated_progress(results))
                # if current_slide == comic_book_carousel.slides[-1]:
                #     app = App.get_running_app()
                #     comic_book_screen = app.manager.current_screen
                #     comic_book_screen.open_next_dialog()
                # elif current_slide == comic_book_carousel.slides[0]:
                #     app = App.get_running_app()
                #     comic_book_screen = app.manager.current_screen
                #     comic_book_screen.open_prev_dialog()
                p_slide = comic_book_carousel.previous_slide
                for slide in comic_book_carousel.slides:
                    for child in slide.walk():
                        if child.id is not None:
                            if "comic_scatter" in child.id:
                                if child.zoom_state == 'zoomed':
                                    child.do_zoom(False)

    def add_pages(self, comic_book_carousel, outer_grid, comic_obj, i):
        # fire off dblpage split if server replies size of image is
        # width>height
        def got_page_size(results):
            if results['width'] > results['height']:
                proxyImage = Loader.image(comic_page_source)
                proxyImage.bind(on_load=partial(
                    comic_page_image._new_image_downloaded,
                    comic_page_scatter, outer_grid, comic_obj, i,
                    comic_page_source))

        strech_image = App.get_running_app().config.get('Display',
                                                        'stretch_image')

        max_height = App.get_running_app().config.get('General', 'max_height')
        comic_page_scatter = ComicBookPageScatter(id='comic_scatter'+str(i),
                                                  comic_page=i,
                                                  do_rotation=False,
                                                  do_translation=False,
                                                  size_hint=(1, 1),
                                                  auto_bring_to_front=True,
                                                  scale_min=1)
        if strech_image == '1':
            s_allow_stretch = True
            s_keep_ratio = False
        else:
            s_allow_stretch = False
            s_keep_ratio = True
        s_max_height = round(dp(max_height))

        s_url_part = f"/Comics/{comic_obj.Id}/Pages/{i}?height={s_max_height}"
        s_url_api = f"&apiKey={self.api_key}"
        if self.view_mode == 'FileOpen' or self.comic_obj.is_sync:
            comic_page_source = get_comic_page(comic_obj, i)
        else:
            comic_page_source = f"{self.api_url}{s_url_part}{s_url_api}"
        comic_page_image = ComicBookPageImage(comic_slug=comic_obj.slug,
                                              id='pi_'+str(i),
                                              allow_stretch=s_allow_stretch,
                                              keep_ratio=s_keep_ratio,
                                              comic_page=i,
                                              source=comic_page_source

                                              )
        comic_page_scatter.add_widget(comic_page_image)
        comic_book_carousel.add_widget(comic_page_scatter)
        # Let's make the thumbs for popup
        s_height = round(dp(240))
        s_url_part = f"/Comics/{comic_obj.Id}/Pages/{i}?height={s_height}"
        s_url_api = f"&apiKey={self.api_key}"
        if self.view_mode == 'FileOpen':
            src_img = get_comic_page(comic_obj, i)
        else:
            src_img = f"{self.api_url}{s_url_part}{s_url_api}"
        inner_grid = ThumbPopPageInnerGrid(
            id='inner_grid'+str(i), spacing=(0, 0))
        page_thumb = ComicBookPageThumb(comic_slug=comic_obj.slug,
                                        id='page_thumb' + str(i), comic_page=i,
                                        source=src_img,
                                        allow_stretch=True)

        page_thumb.size_hint_y = None
        page_thumb.height = dp(240)
        inner_grid.add_widget(page_thumb)
        page_thumb.bind(on_release=page_thumb.click)
        smbutton = ThumbPopPagebntlbl(text='P%s' % str(i+1),
                                      elevation_normal=2, padding=(1, 1),
                                      id=f'page_thumb_lbl{i}',
                                      comic_slug=comic_obj.slug,
                                      comic_page=i,
                                      text_color=(0, 0, 0, 1)
                                      )
        inner_grid.add_widget(smbutton)
        smbutton.bind(on_release=smbutton.click)
        outer_grid.add_widget(inner_grid)
        if comic_obj.PageCount-1 == i:
            self.load_UserCurrentPage()
        s_url_part = f"/Comics/{comic_obj.Id}/Pages/{i}/size"
        get_size_url = f"{self.api_url}{s_url_part}"
        if self.view_mode == 'FileOpen':
            width, height = get_file_page_size(comic_page_source)
            data = {"width": width, "height": height}
            got_page_size(data)
        else:
            self.fetch_data.get_page_size_data(
                get_size_url, callback=lambda req, results: got_page_size(results))
        # proxyImage = Loader.image(comic_page_source,nocache=True)
        # proxyImage.bind(on_load=partial(
        #                                comic_page_image._new_image_downloaded,
        #                                 comic_page_scatter,outer_grid,comic_obj,
        #                                 i,comic_page_source
        #                                 )
        #                 )
        if comic_obj.PageCount-1 == i:
            self.last_page_done = True
            self.load_UserCurrentPage()

    def page_nav_popup_open(self):
        self.page_nav_popup.open()
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        for child in self.walk():
            if child.id == current_slide.id:
                current_page = child
                comic_page = current_page.comic_page
        # scroller = self.dynamic_ids['page_thumb_scroll']
        # for grandchild in scroller.walk():
        #             c_page_thumb = f'page_thumb{comic_page}'
        #             c_page_lbl = f'page_thumb_lbl{comic_page}'
        #             if grandchild.id == c_page_thumb:
        #                 target_thumb = grandchild
        #                 self.scroller.scroll_to(
        #                     target_thumb, padd7ing=10, animate=True)
        for child in self.page_nav_popup.walk():
            if child.id == 'page_thumb_scroll':
                scroller = child
                for grandchild in scroller.walk():
                    c_page_thumb = f'page_thumb{comic_page}'
                    c_page_lbl = f'page_thumb_lbl{comic_page}'
                    if grandchild.id == c_page_thumb:
                        target_thumb = grandchild
                        self.scroller.scroll_to(
                            target_thumb, padding=10, animate=True)

    def build_top_nav(self):
        """
        Build the top popup that contains the readnglist comics and links via cover image to open
        them
        """
        scroll = CommonComicsScroll(id='page_thumb_scroll', size_hint=(
            1, 1), do_scroll_x=True, do_scroll_y=False)
        self.top_pop = Popup(
            id='page_pop',
            title='Comics in List',
            title_align='center',
            content=scroll,
            pos_hint={'top': 1},
            size_hint=(1, None),
            height=round(dp(325))

        )
        self.top_pop
        grid = CommonComicsOuterGrid(id='outtergrd', size_hint=(
            None, None), spacing=5, padding=(5, 5, 5, 5))
        grid.bind(minimum_width=grid.setter('width'))
        if self.current_page is None:
            if self.pag_pagenum == 0:
                page = self.paginator_obj.page(1)
                c_pag_pagenum = page.number
            else:
                page = self.paginator_obj.page(self.pag_pagenum)
            comics_list = page.object_list
            self.current_page = page
            c_pag_pagenum = page.number
            page_num = self.paginator_obj.num_pages()
            c_readinglist_name = self.readinglist_obj.name
            group_str = f' - Page# {page.number} of {page_num}'
            c_title = f'{c_readinglist_name}{group_str}'
            self.top_pop.title = c_title
        else:
            page = self.current_page
            c_pag_pagenum = page.number
            page_num = self.paginator_obj.num_pages()
            c_readinglist_name = self.readinglist_obj.name
            group_str = f" - Page# {page.number} of {page_num}"
            c_title = f'{c_readinglist_name}{group_str}'
            self.top_pop.title = c_title
            comics_list = page.object_list
        if page.has_previous():
            comic_name = 'Prev Page'
            src_thumb = 'assets/prev_page.jpg'
            inner_grid = CommonComicsCoverInnerGrid(
                id='inner_grid'+str('prev'), padding=(1, 1, 1, 1))
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str('prev'))
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.paginator_obj = self.paginator_obj
            comic_thumb.new_page_num = page.previous_page_number()
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=self.load_new_page)
            # smbutton = CommonComicsCoverLabel(text=comic_name)
            smbutton = ThumbPopPagebntlbl(text=comic_name,
                                          elevation_normal=2,
                                          padding=(1, 1),
                                          id=f'comic_lbl_prev',
                                          comic_slug="Prev Comic",

                                          font_size=10.5,
                                          text_color=(0, 0, 0, 1)
                                          )
            inner_grid.add_widget(smbutton)
            smbutton.bind(on_release=self.top_pop.dismiss)
            smbutton.bind(on_release=self.load_new_page)
            grid.add_widget(inner_grid)

        for comic in comics_list:
            comic_name = str(comic.__str__)
            s_url_part = f"/Comics/{comic.Id}/Pages/0?height={round(dp(240))}"
            s_url_api = f"&apiKey={self.api_key}"
            if self.view_mode == 'FileOpen':
                src_thumb = get_comic_page(comic, 0)
            else:
                src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"
            inner_grid = CommonComicsCoverInnerGrid(
                id='inner_grid'+str(comic.Id),
                padding=(0, 0, 0, 0)
            )
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str(comic.Id), comic_obj=comic)
            if self.view_mode == 'FileOpen':
                comic_thumb.mode = 'FileOpen'
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.paginator_obj = self.paginator_obj
            comic_thumb.new_page_num = c_pag_pagenum
            comic_thumb.comic_obj = comic
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=comic_thumb.open_collection)
            # smbutton = CommonComicsCoverLabel(text=comic_name)
            smbutton = ThumbPopPagebntlbl(text=comic_name,
                                          elevation_normal=2,
                                          padding=(1, 1),
                                          id=f'comic_lbl{comic.Id}',
                                          comic_slug=comic.slug,

                                          font_size=10.5,
                                          text_color=(0, 0, 0, 1)
                                          )
            inner_grid.add_widget(smbutton)
            smbutton.bind(on_release=self.top_pop.dismiss)
            smbutton.bind(on_release=comic_thumb.open_collection)
            grid.add_widget(inner_grid)

        if page.has_next():
            comic_name = 'Next Page'
            src_thumb = 'assets/next_page.jpg'
            inner_grid = CommonComicsCoverInnerGrid(
                id='inner_grid'+str('next'))
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str('next'),)
            comic_thumb.readinglist_obj = self.readinglist_obj
            comic_thumb.new_page_num = page.next_page_number()
            comic_thumb.paginator_obj = self.paginator_obj
            inner_grid.add_widget(comic_thumb)
            comic_thumb.bind(on_release=self.top_pop.dismiss)
            comic_thumb.bind(on_release=self.load_new_page)
            # smbutton = CommonComicsCoverLabel(text=comic_name)
            smbutton = ThumbPopPagebntlbl(text=comic_name,
                                          elevation_normal=2,
                                          padding=(1, 1),
                                          id=f'comic_lbl_next',
                                          comic_slug='Next Comic',

                                          font_size=10.5,
                                          text_color=(0, 0, 0, 1)
                                          )
            inner_grid.add_widget(smbutton)
            smbutton.bind(on_release=self.top_pop.dismiss)
            smbutton.bind(on_release=self.load_new_page)
            grid.add_widget(inner_grid)
        scroll.add_widget(grid)

    def comicscreen_open_collection_popup(self):
        self.top_pop.open()

    def load_new_page(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page

        self.build_top_nav()
        self.top_pop.open()

    def load_next_page_comic(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page
        n_paginator = self.paginator_obj
        page = self.current_page
        c_pag_pagenum = new_page.number
        comics_list = page.object_list
        new_screen_name = str(self.next_comic.Id)
        if new_screen_name not in self.app.manager.screen_names:
            new_screen = ServerComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=c_pag_pagenum,
                comic_obj=self.next_comic,
                name=new_screen_name, view_mode=self.view_mode)
            if self.view_mode == 'FileOpen':
                new_screen.view_mode = 'FileOpen'
            self.app.manager.add_widget(new_screen)
        self.app.manager.current = new_screen_name

    def load_prev_page_comic(self, instance):
        new_page = self.paginator_obj.page(instance.new_page_num)
        self.current_page = new_page
        n_paginator = self.paginator_obj
        page = self.current_page
        c_pag_pagenum = new_page.number
        comics_list = page.object_list
        new_screen_name = str(self.prev_comic.Id)
        if new_screen_name not in self.app.manager.screen_names:
            new_screen = ServerComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=c_pag_pagenum,
                comic_obj=self.prev_comic,
                name=new_screen_name, view_mode=self.view_mode)
            self.app.manager.add_widget(new_screen)
        self.app.manager.current = new_screen_name

    def get_next_comic(self):
        n_paginator = self.paginator_obj
        page = self.current_page
        comic_obj = self.comic_obj
        comics_list = page.object_list
        index = comics_list.index(comic_obj)

        if comic_obj.Id == comics_list[-1].Id and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_comic = comics_list[0]
        else:
            if index >= len(comics_list)-1:
                if len(comics_list) <= 1 or self.use_sections is True:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index]
            else:
                if len(comics_list) <= 1 or self.use_sections is True:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index+1]
        return next_comic

    # TODO Fix when 1 comic is loaded there should not be a
    # next and prev comic.
    def get_prev_comic(self):
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj)  # first index where x appears
        if comic_obj.Id == comics_list[0].Id and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_comic = comics_list[-1]
        else:
            if index < len(comics_list):
                if index == 0:
                    if self.section == 'Section' or self.section == 'Last':
                        prev_comic = self.comic_obj

                    else:
                        prev_comic = comics_list[index]
                else:
                    if self.section == 'Section' or self.section == 'Last':
                        prev_comic = self.comic_obj
                    else:
                        prev_comic = comics_list[index-1]
        return prev_comic

    def build_next_comic_dialog(self):
        ''' Make popup showing cover for next comic'''
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic = self.next_comic
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj)  # first index where x appears
        if index+1 == len(comics_list) and page.has_next():
            n_page = n_paginator.page(page.next_page_number())
            comics_list = n_page.object_list
            next_page_number = page.next_page_number()
            c_new_page_num = next_page_number
        else:
            c_new_page_num = page.number
        comic_name = str(comic.__str__)
        s_url_part = f"/Comics/{comic.Id}/Pages/0?height={round(dp(240))}"
        s_url_api = f"&apiKey={self.api_key}"
        if self.view_mode == 'FileOpen':
            src_thumb = get_comic_page(comic, 0)
        else:
            src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"

        inner_grid = CommonComicsCoverInnerGrid(
            id='inner_grid'+str(comic.Id),
            pos_hint={'top': 0.99, 'right': .1}
        )

        comic_thumb = CommonComicsCoverImage(source=src_thumb, id=str(
            comic.Id), comic_obj=comic)
        if self.view_mode == 'FileOpen':
            comic_thumb.mode = 'FileOpen'
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        comic_thumb.last_load = self.last_load
        if self.use_sections:
            comic_thumb.last_section = self.last_section
        comic_thumb.paginator_obj = self.paginator_obj
        comic_thumb.new_page_num = c_new_page_num
        inner_grid.add_widget(comic_thumb)

        smbutton = ThumbPopPagebntlbl(text=comic_name,
                                      font_size=12,
                                      text_color=(0, 0, 0, 1))
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if self.use_sections:
                dialog_title = 'Load Next Section'
            else:
                if index+1 == page.end_index():
                    dialog_title = 'Load Next Page'
                else:
                    dialog_title = 'On Last Comic'
        else:
            if self.use_sections:
                dialog_title = 'Load Next Section'
            else:
                if index+1 == page.end_index():
                    dialog_title = 'Load Next Page'
                else:
                    dialog_title = 'Load Next Comic'

        self.next_dialog = Popup(id='next_pop',
                                 title=dialog_title,
                                 content=content,
                                 pos_hint={.5: .724},
                                 size_hint=(None, None),
                                 size=(dp(280), dp(340))
                                 )
        self.next_dialog.bind(on_dismiss=self.next_dialog_closed)
        c_padding = (self.next_dialog.width/4)
        CommonComicsCoverInnerGrid.padding = (c_padding, 0, 0, 0)
        comic_thumb.bind(on_release=self.close_next_dialog)
        self.next_nav_comic_thumb = comic_thumb
        # if index >= len(comics_list)-1:
        #     if self.use_sections:
        #         comic_thumb.bind(on_release=comic_thumb.open_next_section)
        #     else:
        #         if len(comics_list) >= 1:
        #             comic_thumb.bind(on_release=self.load_next_page_comic)
        #         else:
        #             return
        # else:
        #     if self.use_sections:
        #         comic_thumb.bind(on_release=comic_thumb.open_next_section)
        #     else:
        #         if len(comics_list) >= 1:
        #             comic_thumb.bind(on_release=self.load_next_page_comic)
        #         else:
        #             comic_thumb.bind(on_release=comic_thumb.open_collection)

        if index >= len(comics_list)-1:
            if self.use_sections:
                comic_thumb.action_do = 'open_next_section'
                comic_thumb.bind(on_release=comic_thumb.do_action)
            else:
                if len(comics_list) >= 1:
                    comic_thumb.action_do = 'load_next_page_comic'
                    comic_thumb.bind(on_release=self.load_next_page_comic)
                else:
                    return
        else:
            if self.use_sections:
                comic_thumb.action_do = 'open_next_section'
                comic_thumb.bind(on_release=comic_thumb.do_action)
            else:
                if len(comics_list) >= 1:
                    comic_thumb.action_do = 'load_next_page_comic'
                    comic_thumb.bind(on_release=self.load_next_page_comic)
                else:
                    comic_thumb.action_do = 'open_collection'
                    comic_thumb.bind(on_release=comic_thumb.do_action)

    def build_prev_comic_dialog(self):
        n_paginator = self.paginator_obj
        page = self.current_page
        comics_list = page.object_list
        comic = self.prev_comic
        comic_obj = self.comic_obj
        index = comics_list.index(comic_obj)  # first index where x appears
        prev_page_number = 1
        if index == 0 and page.has_previous():
            n_page = n_paginator.page(page.previous_page_number())
            comics_list = n_page.object_list
            prev_page_number = page.previous_page_number()
        comic_name = str(comic.__str__)
        s_url_part = f"/Comics/{comic.Id}/Pages/0?height={round(dp(240))}"
        s_url_api = f"&apiKey={self.api_key}"
        if self.view_mode == 'FileOpen':
            src_thumb = get_comic_page(comic, 0)
        else:
            src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"
        inner_grid = CommonComicsCoverInnerGrid(
            id='inner_grid'+str(comic.Id), pos_hint={'top': 0.99, 'right': .1}
        )
        comic_thumb = CommonComicsCoverImage(source=src_thumb, id=str(
            comic.Id), pos_hint={.5: .5}, comic_obj=comic)
        if self.view_mode == 'FileOpen':
            comic_thumb.mode = 'FileOpen'
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        if self.use_sections:
            comic_thumb.last_section = self.last_section
        if index == 0 and page.has_previous():
            comic_thumb.new_page_num = prev_page_number
        else:
            comic_thumb.new_page_num = page.number
        comic_thumb.readinglist_obj = self.readinglist_obj
        inner_grid.add_widget(comic_thumb)

        smbutton = ThumbPopPagebntlbl(text=comic_name,
                                      font_size=12,
                                      text_color=(0, 0, 0, 1))
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if len(comics_list) >= 1:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'On First Comic'
        else:
            if index != 0:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'On First Comic'
        self.prev_dialog = Popup(id='prev_pop',
                                 title=dialog_title,
                                 content=content,
                                 pos_hint={.5: .724},
                                 size_hint=(.4, .34)
                                 )
        self.prev_dialog.bind(on_dismiss=self.prev_dialog_closed)
        c_padding = (self.prev_dialog.width/4)
        CommonComicsCoverInnerGrid.padding = (c_padding, 0, 0, 0)
        comic_thumb.bind(on_release=self.prev_dialog.dismiss)
        self.prev_nav_comic_thumb = comic_thumb
        if index < len(comics_list):
            if index == 0:
                if self.use_sections and self.section != 'First':
                    comic_thumb.action_do = 'open_prev_section'
                    comic_thumb.bind(on_release=comic_thumb.do_action)
                else:
                    if len(comics_list) > 1:
                        comic_thumb.action_do = 'load_prev_page_comic'
                        comic_thumb.bind(on_release=self.load_prev_page_comic)
                    else:
                        return
            else:
                if self.use_sections and self.section != 'First':
                    comic_thumb.action_do = 'open_prev_section'
                    comic_thumb.bind(on_release=comic_thumb.do_action)
                else:
                    if len(comics_list) > 1:
                        comic_thumb.action_do = 'load_prev_page_comic'
                        comic_thumb.bind(on_release=self.load_prev_page_comic)
                    else:
                        comic_thumb.action_do = 'open_collection'
                        comic_thumb.bind(on_release=comic_thumb.do_action)

    def open_next_dialog(self):
        toast('At last page open next comic')
        self.next_dialog.open()

    def next_dialog_closed(self, *args):
        self.next_dialog_open = False

    def close_next_dialog(self, *args):
        self.next_dialog.dismiss()
        self.next_dialog_open = False

    def open_prev_dialog(self):
        toast('At first page open prev comic')
        self.prev_dialog.open()

    def prev_dialog_closed(self, *args):
        self.next_dialog_open = False

    def close_prev_dialog(self, *args):
        self.prev_dialog.dismiss()
        self.prev_dialog_open = False

    def load_random_comic(self):
        next_screen_name = self.app.manager.next()
        self.app.manager.current = next_screen_name

    def load_next_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.use_sections:
            if comic_book_carousel.next_slide is None:
                if self.next_dialog_open == False:
                    self.open_next_dialog()
                    self.next_dialog_open = True
                else:
                    if self.next_nav_comic_thumb.action_do == 'load_next_page_comic':
                        self.load_next_page_comic(self.next_nav_comic_thumb)
                    else:
                        self.next_nav_comic_thumb.do_action()
                    self.close_next_dialog()
                return
            else:
                comic_book_carousel.load_next()
                return
        else:
            if self.comic_obj.PageCount-1 == comic_scatter.comic_page and\
                    comic_book_carousel.next_slide is None:
                if self.next_dialog_open == False:
                    self.open_next_dialog()
                    self.next_dialog_open = True
                else:
                    if self.next_nav_comic_thumb.action_do == 'load_next_page_comic':
                        self.load_next_page_comic(self.next_nav_comic_thumb)
                    else:
                        self.next_nav_comic_thumb.do_action()
                    self.close_next_dialog()
                return
            else:
                comic_book_carousel.load_next()

    def load_prev_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.use_sections:
            if comic_book_carousel.previous_slide is None:
                if self.prev_dialog_open == False:
                    self.open_prev_dialog()
                    self.prev_dialog_open = True
                else:
                    if self.prev_nav_comic_thumb.action_do == 'load_prev_page_comic':
                        self.load_prev_page_comic(self.prev_nav_comic_thumb)
                    else:
                        self.prev_nav_comic_thumb.do_action()
                    self.close_prev_dialog()
                return
            else:
                comic_book_carousel.load_previous()
                return
        else:
            if comic_scatter.comic_page == 0 and\
                    comic_book_carousel.previous_slide is None:
                if self.prev_dialog_open == False:
                    self.open_prev_dialog()
                    self.prev_dialog_open = True
                else:
                    if self.prev_nav_comic_thumb.action_do == 'load_prev_page_comic':
                        self.load_prev_page_comic(self.prev_nav_comic_thumb)
                    else:
                        self.prev_nav_comic_thumb.do_action()
                    self.close_prev_dialog()
                return
            else:
                comic_book_carousel.load_previous()
                return
                ######

    def build_option_pop(self):
        def call_back_dismiss(instance):
            self.option_isopen = False

        bg_color = self.app.theme_cls.primary_color
        option_bar = OptionToolBar(comic_Id=self.comic_obj.Id)
        self.option_pop = ModalView(pos_hint={'top': 1},
                                    size_hint=(1, None),
                                    height = option_bar.height

                                    )
        self.option_pop.add_widget(option_bar)
        self.option_pop.bind(on_dismiss=call_back_dismiss)

    def toggle_option_bar(self):
        if self.option_isopen == True:
            self.option_pop.dismiss()
            self.option_isopen = False
        else:
            self.option_pop.open()
            self.option_isopen = True


class ComicBookPageControlButton(Button):
    pass


class OptionPopup(Popup):
    pass


class OptionToolBar(MDToolbar):
    title = StringProperty()
    comic_Id = StringProperty()

    def __init__(self, **kwargs):
        super(OptionToolBar, self).__init__(**kwargs)
        app = App.get_running_app()
        screen_manager = app.manager
        comic_book_screen = screen_manager.get_screen(app.manager.current)
        title_txt = comic_book_screen.comic_obj.__str__
        if comic_book_screen.view_mode == 'FileOpen':
            title_txt = f'{title_txt} *File*'
        self.title = title_txt
        root = self
        self.left_action_items = [
            # ["menu", (lambda x: nav_drawer._toggle())],
            ["home", lambda x: root.option_bar_action('base')],
            ['settings', lambda x: app.open_settings()],
            ['fullscreen', lambda x: root.toggle_full_screen()],
        ]
        self.right_action_items = [
            ['file-cabinet', lambda x: app.file_manager_open()],
            ['server',
                lambda x: app.switch_server_lists_screen()],
            ['view-list',
                lambda x: root.option_bar_action('server_readinglists_screen')],
            ['close-box-outline', lambda x: app.stop()]
        ]

    def option_bar_action(self, *args):
        app = App.get_running_app()
        screen_manager = app.manager
        comic_book_screen = screen_manager.get_screen(self.comic_Id)
        s_name = comic_book_screen.comic_obj.Id
        comic_book_screen.option_pop.dismiss()
        if args[0] == 'base':
            app.show_action_bar()
        app.manager.current = str(args[0])

    def toggle_full_screen(self):
        app = App.get_running_app()
        screen_manager = app.manager
        comic_book_screen = screen_manager.get_screen(self.comic_Id)
        if comic_book_screen.full_screen == False:
            Window.fullscreen = 'auto'
            comic_book_screen.full_screen = True
        else:
            Window.fullscreen = False
            comic_book_screen.full_screen = False
