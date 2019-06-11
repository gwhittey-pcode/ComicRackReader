from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import ObjectProperty,StringProperty,ListProperty,NumericProperty,DictProperty
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image,AsyncImage
from kivy.uix.button import Button,ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from libs.utils.comic_server_conn import ComicServerConn

from libs.utils.convert_base64 import convert_to_image
from kivy.graphics.transformation import Matrix
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window


class ComicBookPageScatter(ScatterLayout):
    zoom_state = StringProperty()
    comic_page = NumericProperty()
    def __init__(self, **kwargs):
        super(ComicBookPageScatter, self).__init__(**kwargs)
        self.zoom_state = 'normal'
        self.move_state = 'open'
    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.zoom_state == 'zoomed':
                self.zoom_state = 'normal'
                mat = self.transform_inv
                self.apply_transform(mat,anchor=(0,0))
            elif self.zoom_state == 'normal':
                self.zoom_state = 'zoomed'
                mat = Matrix().scale(2,2,2)
                self.apply_transform(mat,anchor=touch.pos)
        return super(ComicBookPageScatter, self).on_touch_down(touch)

    def on_transform_with_touch(self,touch):
         self.zoom_state = 'zoomed'
         return super(ComicBookPageScatter, self).on_transform_with_touch(touch)


class ComicBookPageImage(AsyncImage):
        '''Fired once the image is downloaded and ready to use'''
        comic_slug = StringProperty()
        comic_page_num = NumericProperty()
        fetch_data = ObjectProperty()
        comic_page = NumericProperty()
        comic_page_type = StringProperty
        def __init__(self,**kwargs):
            super(ComicBookPageImage, self).__init__(**kwargs)
    
        def _new_image_downloaded(self, scatter , outer_grid,comic_obj,var_i,src_url,proxyImage):
            '''Fired once the image is downloaded and ready to use'''
            def _remove_widget():
                carousel.remove_widget(scatter)

            def _add_parts():
                strech_image = App.get_running_app().config.get('Display', 'stretch_image')
                if strech_image == '1':
                    s_allow_stretch=True
                    s_keep_ratio=False
                else:
                    s_allow_stretch=False
                    s_keep_ratio=True
                part_1 = ComicBookPageImage(comic_slug=comic_obj.slug,
                                            id='pi_'+str(var_i)+'b', 
                                            comic_page=var_i,
                                            allow_stretch=s_allow_stretch,
                                            keep_ratio=s_keep_ratio
                                            )
                part_2 = ComicBookPageImage(comic_slug=comic_obj.slug, 
                                            id='pi_'+str(var_i)+'b', 
                                            comic_page=var_i,
                                            allow_stretch=s_allow_stretch, 
                                            keep_ratio=s_keep_ratio
                                            )
                scatter_1 = ComicBookPageScatter(id='comic_scatter'+str(var_i), comic_page=var_i)
                scatter_2 = ComicBookPageScatter(id='comic_scatter'+str(var_i)+'b', comic_page=var_i)
                part_1.texture = proxyImage.image.texture.get_region(0,0,c_width/2,c_height)
                part_2.texture = proxyImage.image.texture.get_region((c_width/2+1),0,c_width/2,c_height)
                scatter_1.add_widget(part_1)
                scatter_2.add_widget(part_2)
                if last_page == True:
                    carousel.add_widget(scatter_1)
                    carousel.add_widget(scatter_2)
                else:
                    carousel.add_widget(scatter_1,i)
                    carousel.add_widget(scatter_2,i+1)
            if proxyImage.image.texture:
                split_dbl_page = App.get_running_app().config.get('Display', 'dblpagesplit')
                if proxyImage.image.texture.width > 2*Window.width and split_dbl_page == '1':
                    last_page = False
                    app = App.get_running_app()
                    inner_grid_id ='inner_grid' + str(var_i)
                    page_image_id = str(var_i)
                    carousel = App.get_running_app().manager.get_screen(comic_obj.Id).ids.comic_book_carousel
                    inner_grid_id = 'inner_grid%s'%str(var_i)
                    c_width = self.texture.width
                    c_height = self.texture.height
                    i = 0
                    for slide in carousel.slides:
                        if slide.id == scatter.id:
                            if slide.comic_page == comic_obj.PageCount-1:
                                last_page = True
                            _remove_widget()
                            _add_parts()
                        i+=1

                else:
                    if proxyImage.image.texture.width > 2*Window.width:
                        scatter.size_hint=(2,1)
                if comic_obj.PageCount-1 == var_i:
                    App.get_running_app().manager.get_screen(comic_obj.Id).load_UserCurrentPage()

class ComicCarousel(Carousel):
    def on_touch_move(self, touch):
        if not self.touch_mode_change:
            if self.ignore_perpendicular_swipes and \
                    self.direction in ('top', 'bottom'):
                if abs(touch.oy - touch.y) < self.scroll_distance:
                    if abs(touch.ox - touch.x) > self.scroll_distance:
                        self._change_touch_mode()
                        self.touch_mode_change = True
            elif self.ignore_perpendicular_swipes and \
                    self.direction in ('right', 'left'):
                if abs(touch.ox - touch.x) < self.scroll_distance:
                    if abs(touch.oy - touch.y) > self.scroll_distance:
                        self._change_touch_mode()
                        self.touch_mode_change = True

        if self._get_uid('cavoid') in touch.ud:
            return
        if self._touch is not touch:
            super(ComicCarousel, self).on_touch_move(touch)
            return self._get_uid() in touch.ud
        if touch.grab_current is not self:
            return True
        ud = touch.ud[self._get_uid()]
        direction = self.direction
        if ud['mode'] == 'unknown':
            if direction[0] in ('r', 'l'):
                distance = abs(touch.ox - touch.x)
            else:
                distance = abs(touch.oy - touch.y)
            if distance > self.scroll_distance:
                if self.index != None:
                    current_slide = self.current_slide
                    
                    if current_slide == self.slides[-1]:
                        comic_book_screen =App.get_running_app().manager.current_screen
                        comic_book_screen.open_next_dialog()
                
                ev = self._change_touch_mode_ev
                if ev is not None:
                    ev.cancel()
                ud['mode'] = 'scroll'
        else:
            if direction[0] in ('r', 'l'):
                self._offset += touch.dx
            if direction[0] in ('t', 'b'):
                self._offset += touch.dy
        return super(ComicCarousel, self).on_touch_move(touch)



#Button for screen tapping control
class ComicBookPageControlButton(Button):
    location = StringProperty()

    def enable_me(self,instance):
        self.disabled = False

    def on_touch_down(self, touch):
        if touch.is_double_tap:
             if self.collide_point(*touch.pos):
                comic_book_screen =App.get_running_app().manager.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)
        if self.disabled:
            if self.collide_point(*touch.pos):
                comic_book_screen =App.get_running_app().manager.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)

        return super(ComicBookPageControlButton, self).on_touch_down(touch)
    def on_touch_up(self, touch):
        if touch.is_double_tap:
            if self.collide_point(*touch.pos):
                comic_book_screen =App.get_running_app().manager.current_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_up(touch)
        else:
            
            return super(ComicBookPageControlButton, self).on_touch_up(touch)

    
    def click(btn):
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, .5)
        comic_book_screen = App.get_running_app().manager.current_screen
        app = App.get_running_app()
        if btn.location == '':
            return
        tap_option =  App.get_running_app().config.get('Screen Tap Control', str(btn.location))
        if tap_option == 'Next Page':
            comic_book_screen.load_next_slide()
        elif tap_option == 'Prev Page':
            comic_book_screen.load_prev_slide()
        elif tap_option == 'Open Page Nav':
            comic_book_screen.page_nav_popup_open()
        elif tap_option == 'Open Collection Browser':
             if len(comic_book_screen.readinglist_obj.comics)>1:
                comic_book_screen.comicscreen_open_collection_popup()
             else:
                 return
        elif tap_option == 'Prev Comic':
            comic_book_screen.load_prev_comic()
        elif tap_option == 'Next Comic':
            comic_book_screen.load_next_comic()
        elif tap_option == 'Return to Comic List Screen':
            app.manager.current = 'readinglistscreen'
        elif tap_option == 'Go to List of Reading Lists':
            app.manager.current = 'base'
        else:
            return

#<<<<Following are class for popup at bottom page for pressing and going to page x
class ThumbPopPagePopup(Popup):
    pass

class ThumbPopPageScroll(ScrollView):
    pass

class ThumbPopPageOutterGrid(GridLayout):
    pass

class ThumbPopPageInnerGrid(GridLayout):
    pass

class ThumbPopPagebntlbl(Button):
    pass

class ThumbPopPageSmallButton(Button):
    pass

class ThumbPopPageImage(ButtonBehavior,Image):
        comic_slug = StringProperty()
        fetch_data = ObjectProperty()
        comic_page = NumericProperty()
        def __init__(self,**kwargs):
            super(ThumbPopPageImage, self).__init__(**kwargs)
            base_url = App.get_running_app().config.get('Server', 'url')
            
           

        def got_json(self,req, result):     
            img = convert_to_image(result["page"])
            self.texture = img.texture

    
        def click(self,instance):
            app = App.get_running_app()
            # app.root.current = 'comic_book_screen'
            page_nav_popup = app.root.ids.comic_book_screen.page_nav_popup
            page_nav_popup.dismiss()
            carousel = App.get_running_app().manager.current_screen.ids.comic_book_carousel
            for slide in carousel.slides:
                if slide.id == self.id:
                    use_slide = slide
            carousel.load_slide(use_slide)

class ComicBookPageThumb(ButtonBehavior,AsyncImage):
        '''Fired once the image is downloaded and ready to use'''
        comic_slug = StringProperty()
        fetch_data = ObjectProperty()
        comic_page = NumericProperty()
        def __init__(self,**kwargs):
            super(ComicBookPageThumb, self).__init__(**kwargs)
            base_url = App.get_running_app().config.get('Server', 'url')
        def click(self,instance):
            app = App.get_running_app()
            # app.root.current = 'comic_book_screen'
            page_nav_popup = app.manager.current_screen.page_nav_popup
            page_nav_popup.dismiss()
            carousel =App.get_running_app().manager.current_screen.ids.comic_book_carousel
            for slide in carousel.slides:
                if slide.id == self.id:
                    use_slide = slide
            carousel.load_slide(use_slide)

class CommonComicsScroll(ScrollView):
    pass
class CommonComicsOuterGrid(GridLayout):
    pass

class CommonComicsCoverLabel(Label):
    pass

class CommonComicsCoverInnerGrid(GridLayout):
    pass

class CommonComicsCoverImage(ButtonBehavior,AsyncImage):
    comic_obj = ObjectProperty()
    readinglist_obj = ObjectProperty()
    clock_set = StringProperty()


    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False

    # def open_comic(self,*args):
    #     self.disabled = True
    #     app = App.get_running_app()
    #     app.root.current = 'comic_book_screen'
    #     new_reading_list = ComicReadingList()
    #     new_reading_list.add_comic(self.comic)
    #     comic_screen = app.manager.get_screen('comic_book_screen')
    #     comic_screen.load_comic_book(self.comic,new_reading_list)
    #     Clock.schedule_once(self.enable_me, .5)

    def open_collection(self,*args):
        self.disabled = True
        app = App.get_running_app()
        from libs.uix.baseclass.comicbookscreen import ComicBookScreen
        new_screen_name = str(self.comic_obj.Id)
        if new_screen_name not in app.manager.screen_names:
            new_screen = ComicBookScreen(readinglist_obj=self.readinglist_obj,comic_obj=self.comic_obj,name=new_screen_name)
            app.manager.add_widget(new_screen)
        app.manager.current = new_screen_name
        Clock.schedule_once(self.enable_me, .5)

    def open_next_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
        comic_screen = app.manager.current_screen
        comic_screen.load_comic_book(self.comic_obj,self.readinglist_obj)
        Clock.schedule_once(self.enable_me, .5)

    def open_prev_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
       
        comic_screen = app.manager.current_screen
        comic_screen.last_load = comic_screen.last_section
        comic_screen.load_comic_book(self.comic_obj,self.readinglist_obj)
        Clock.schedule_once(self.enable_me, .5)

