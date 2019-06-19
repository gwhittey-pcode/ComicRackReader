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
import webbrowser
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty,\
    NumericProperty
from libs.utils.comic_server_conn import ComicServerConn
from kivy.app import App
from libs.utils.convert_base64 import convert_to_image
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
from kivymd.toast import toast
from libs.applibs.kivymd.dialog import MDDialog
from kivy.loader import Loader
import json
from kivymd.toolbar import MDToolbar


class ComicBookScreen(Screen):
    scroller = ObjectProperty()
    top_pop = ObjectProperty()
    section = StringProperty()
    sort_by = StringProperty()

    def __init__(self, readinglist_obj=None, comic_obj=None,
                 paginator_obj=None, pag_pagenum=1, **kwargs):
        super(ComicBookScreen, self).__init__(**kwargs)
        self.fetch_data = None
        self.app = App.get_running_app()
        self.last_load = 0
        self.base_url = self.app.base_url
        self.api_url = self.app.api_url
        self.api_key = self.app.config.get('Server', 'api_key')
        self.current_page = None
        self.comic_obj = ObjectProperty()
        self.comic_obj = None
        self.paginator_obj = ObjectProperty()
        self.paginator_obj = None
        self.fetch_data = ComicServerConn()
        self.api_key = self.app.config.get('Server', 'api_key')
        self.popup_bkcolor = (.5, .5, .5, .87)
        self.pag_pagenum = NumericProperty()
        config_app = App.get_running_app()
        settings_data = json.loads(settings_json_screen_tap_control)

        for setting in settings_data:
            if setting['type'] == 'options':

                tap_config = config_app.config.get(setting[u'section'],
                                                   setting[u'key'])
                if tap_config == 'Disabled':
                    self.ids[setting[u'key']].disabled = True

        self.readinglist_obj = readinglist_obj
        self.comic_obj = comic_obj
        self.paginator_obj = paginator_obj
        self.pag_pagenum = pag_pagenum
        comic_book_carousel = self.ids.comic_book_carousel
        comic_book_carousel.clear_widgets()
        if self.scroller:
            self.scroller.clear_widgets()
        if self.top_pop:
            self.top_pop.clear_widgets()
        number_pages = int(comic_obj.PageCount)
        x_title = self.comic_obj.__str__
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True,
                            do_scroll_y=False, id='page_thumb_scroll',
                            scroll_type=['bars', 'content']
                            )
        self.page_nav_popup = Popup(id='page_nav_popup', title=x_title,
                                    pos_hint={'y': 0},
                                    size_hint=(1, .32),

                                    )
        self.page_nav_popup.add_widget(scroll)
        self.scroller = scroll
        outer_grid = GridLayout(rows=1, size_hint=(None, None), spacing=(5, 0),
                                padding=(5, 0), id='outtergrd')
        outer_grid.bind(minimum_width=outer_grid.setter('width'))
        i = 0

        self.use_pagination = False
        for i in range(0, number_pages):
            self.add_pages(comic_book_carousel, outer_grid, comic_obj, i)
            if i == comic_obj.UserCurrentPage:
                m_UserCurrentPage = 'comic_scatter'+str(i)

        scroll.add_widget(outer_grid)
        self.build_top_nav()
        self.next_comic = self.get_next_comic()
        self.prev_comic = self.get_prev_comic()
        self.build_next_comic_dialog()
        self.build_prev_comic_dialog()

    def open_mag_glass(self):
        comic_book_carousel = self.ids.comic_book_carousel
        current_slide = comic_book_carousel.current_slide
        current_page = comic_book_carousel.current_slide.comic_page
        for child in current_slide.walk():
            print(child.id)
        print(current_page)

    def on_pre_enter(self):
        self.app.hide_action_bar()

    def on_enter(self):
        self.build_option_pop()

    def load_UserCurrentPage(self):
        for slide in self.ids.comic_book_carousel.slides:
            if slide.comic_page == self.comic_obj.UserCurrentPage:
                self.ids.comic_book_carousel.load_slide(slide)

    def slide_changed(self, index):

        if index is not None:
            comic_book_carousel = self.ids.comic_book_carousel
            current_page = comic_book_carousel.current_slide.comic_page
            comic_obj = self.comic_obj
            comic_Id = comic_obj.Id
            prev_id = f'comic_scatter{current_page-1}'
            next_id = f'comic_scatter{current_page+1}'
            update_url = f'{self.api_url}/Comics/{comic_Id}/Progress'
            self.fetch_data.update_progress(update_url, current_page, self)
            p_slide = comic_book_carousel.previous_slide
            for slide in comic_book_carousel.slides:
                for child in slide.walk():
                    if child.id is not None:
                        if "comic_scatter" in child.id:
                            if child.zoom_state == 'zoomed':
                                child.do_zoom(False)

    def progress_updated(self, req, results):
        pass

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

        max_height = App.get_running_app().config.get('Server', 'max_height')
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
                                      elevation_normal=2, padding=(0, 0),
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

        scroll = CommonComicsScroll(id='page_thumb_scroll', size_hint=(
            1, 1), do_scroll_x=True, do_scroll_y=False)
        self.top_pop = Popup(id='page_pop', title='Comics in List',
                             title_align='center', content=scroll,
                             pos_hint={'y': .718}, size_hint=(1, .3),

                             )
        self.top_pop
        grid = CommonComicsOuterGrid(id='outtergrd', size_hint=(
            None, None), spacing=5, padding=(5, 5))
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
            group_str = f' - Group# {page.number} of {page_num}'
            c_title = f'{c_readinglist_name}{group_str}'
            self.top_pop.title = c_title
        else:
            page = self.current_page
            c_pag_pagenum = page.number
            page_num = self.paginator_obj.num_pages()
            c_readinglist_name = self.readinglist_obj.name
            group_str = f" - Group# {page.number} of {page_num}"
            c_title = f'{c_readinglist_name}{group_str}'
            self.top_pop.title = c_title
            comics_list = page.object_list
        if page.has_previous():
            comic_name = 'Prev Page'
            src_thumb = 'assets/prev_page.jpg'
            inner_grid = CommonComicsCoverInnerGrid(
                id='inner_grid'+str('prev'), padding=(1, 1))
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
                                          padding=(0, 0),
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
            src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"
            inner_grid = CommonComicsCoverInnerGrid(
                id='inner_grid'+str(comic.Id))
            comic_thumb = CommonComicsCoverImage(
                source=src_thumb, id=str(comic.Id), comic_obj=comic)
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
                                          padding=(0, 0),
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
                                          padding=(0, 0),
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
            new_screen = ComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=c_pag_pagenum,
                comic_obj=self.next_comic, name=new_screen_name)
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
            new_screen = ComicBookScreen(
                readinglist_obj=self.readinglist_obj,
                paginator_obj=self.paginator_obj,
                pag_pagenum=c_pag_pagenum,
                comic_obj=self.prev_comic, name=new_screen_name)
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
                if len(comics_list) <= 1:
                    next_comic = self.comic_obj
                else:
                    next_comic = comics_list[index]
            else:
                if len(comics_list) <= 1:
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
        comic_name = str(comic.__str__)
        s_url_part = f"/Comics/{comic.Id}/Pages/0?height={round(dp(240))}"
        s_url_api = f"&apiKey={self.api_key}"
        src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"
        inner_grid = CommonComicsCoverInnerGrid(
            id='inner_grid'+str(comic.Id), pos_hint={.5: .5})
        comic_thumb = CommonComicsCoverImage(source=src_thumb, id=str(
            comic.Id), pos_hint={.5: .5}, comic_obj=comic)
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        comic_thumb.paginator_obj = self.paginator_obj
        if index+1 == len(comics_list) and page.has_next():
            comic_thumb.new_page_num = next_page_number
        else:
            comic_thumb.new_page_num = page.number
        inner_grid.add_widget(comic_thumb)

        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if index+1 == page.end_index():
                dialog_title = 'Load Next Page'
            else:
                dialog_title = 'On Last Comic'
        else:
            if index+1 == page.end_index():
                dialog_title = 'Load Next Page'
            else:
                dialog_title = 'Load Next Comic'
        self.next_dialog = Popup(id='next_pop', title=dialog_title,
                                 content=content, pos_hint={.5: .724},
                                 size_hint=(.25, .25)
                                 )
        comic_thumb.bind(on_release=self.next_dialog.dismiss)

        if index >= len(comics_list)-1:
            if len(comics_list) >= 1:
                comic_thumb.bind(on_release=self.load_next_page_comic)
            else:
                return
        else:
            if len(comics_list) >= 1:
                comic_thumb.bind(on_release=self.load_next_page_comic)
            else:
                comic_thumb.bind(on_release=comic_thumb.open_collection)

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
        src_thumb = f"{self.api_url}{s_url_part}{s_url_api}"
        inner_grid = CommonComicsCoverInnerGrid(
            id='inner_grid'+str(comic.Id), pos_hint={.5: .5})
        comic_thumb = CommonComicsCoverImage(source=src_thumb, id=str(
            comic.Id), pos_hint={.5: .5}, comic_obj=comic)
        comic_thumb.readinglist_obj = self.readinglist_obj
        comic_thumb.comic = comic
        if index == 0 and page.has_previous():
            comic_thumb.new_page_num = prev_page_number
        else:
            comic_thumb.new_page_num = page.number
        comic_thumb.readinglist_obj = self.readinglist_obj
        inner_grid.add_widget(comic_thumb)

        smbutton = CommonComicsCoverLabel(text=comic_name)
        inner_grid.add_widget(smbutton)
        content = inner_grid
        if index >= len(comics_list)-1:
            if len(comics_list) >= 1:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'On Last Comic'
        else:
            if len(comics_list) >= 1:
                dialog_title = 'Load Prev Page'
            else:
                dialog_title = 'Load Next Comic'

        self.prev_dialog = Popup(id='prev_pop', title=dialog_title,
                                 content=content, pos_hint={.5: .724},
                                 size_hint=(.25, .25)
                                 )
        comic_thumb.bind(on_release=self.prev_dialog.dismiss)

        comic_thumb.bind(on_release=self.prev_dialog.dismiss)
        if index < len(comics_list):
            if index == 0:
                if len(comics_list) > 1:
                    comic_thumb.bind(on_release=self.load_prev_page_comic)
                else:
                    return
            else:
                if len(comics_list) > 1:
                    comic_thumb.bind(on_release=self.load_prev_page_comic)
                else:
                    comic_thumb.bind(on_release=comic_thumb.open_collection)

    def open_next_dialog(self):
        toast('At last page open next comic')
        self.next_dialog.open()

    def open_prev_dialog(self):
        toast('At first page open prev comic')
        self.prev_dialog.open()

    def load_random_comic(self):
        next_screen_name = self.app.manager.next()
        print(next_screen_name)
        self.app.manager.current = next_screen_name

    def load_next_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if self.comic_obj.PageCount-1 == comic_scatter.comic_page and\
                comic_book_carousel.next_slide is None:
            self.open_next_dialog()
            return
        else:
            comic_book_carousel.load_next()

    def load_prev_slide(self):
        comic_book_carousel = self.ids.comic_book_carousel
        comic_scatter = comic_book_carousel.current_slide
        if comic_scatter.comic_page == 0 and\
                comic_book_carousel.previous_slide is None:
            self.open_prev_dialog()
            return
        else:
            comic_book_carousel.load_previous()

    def build_option_pop(self):
        bg_color = self.app.theme_cls.primary_color
        option_bar = OptionToolBar(comic_Id=self.comic_obj.Id)
        self.option_pop = ModalView(pos_hint={'y': .917},
                                    size_hint=(1, .1),

                                    )
        self.option_pop.add_widget(option_bar)

    def open_option(self):
        self.option_pop.open()


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
        self.title = comic_book_screen.comic_obj.__str__

    def option_bar_action(self, *args):
        app = App.get_running_app()
        screen_manager = app.manager
        comic_book_screen = screen_manager.get_screen(self.comic_Id)
        s_name = comic_book_screen.comic_obj.Id
        comic_book_screen.option_pop.dismiss()
        app.manager.current = str(args[0])
