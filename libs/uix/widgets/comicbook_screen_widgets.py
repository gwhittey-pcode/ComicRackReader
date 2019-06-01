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



class ComicBookPageScatter(ScatterLayout):
    zoom_state = StringProperty()
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


class ComicBookPageImage(Image):
        '''Fired once the image is downloaded and ready to use'''
        comic_slug = StringProperty()
        fetch_data = ObjectProperty()
        comic_page = NumericProperty()
        def __init__(self,**kwargs):
            super(ComicBookPageImage, self).__init__(**kwargs)
            base_url = App.get_running_app().config.get('Server', 'url')
            fetch_data = ComicServerConn()
            url_send = f'{base_url}issue/{self.comic_slug}/get-page/{self.comic_page}/'
            fetch_data.get_server_data(url_send,self)

        def got_json(self,req, result):     
            img = convert_to_image(result["page"])
            self.texture = img.texture


        #def _remove_widget():
        #    carousel.remove_widget(scatter)


class ComicCarousel(Carousel):
    pass

#Button for screen tapping control

class ComicBookPageControlButton(Button):
    location = StringProperty()
    def enable_me(self,instance):
        Logger.debug('I am enabled')
        self.disabled = False

    def on_touch_down(self, touch):
        if self.disabled:
            if self.collide_point(*touch.pos):
                comic_book_screen =App.get_running_app().root.ids.comic_book_screen
                comic_book_carousel = comic_book_screen.ids.comic_book_carousel
                current_slide = comic_book_carousel.current_slide
                return current_slide.on_touch_down(touch)

        return super(ComicBookPageControlButton, self).on_touch_down(touch)

    def click(btn):
        btn.disabled = True
        Clock.schedule_once(btn.enable_me, .5)
        comic_book_screen =App.get_running_app().root.ids.comic_book_screen
        app = App.get_running_app()
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
            app.manager.current = 'basescreen'
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
            fetch_data = ComicServerConn()
            url_send = f'{base_url}issue/{self.comic_slug}/get-page/{self.comic_page}/'
            fetch_data.get_server_data(url_send,self)

        def got_json(self,req, result):     
            img = convert_to_image(result["page"])
            self.texture = img.texture

    
        def click(self,instance):
            app = App.get_running_app()
            # app.root.current = 'comic_book_screen'
            page_nav_popup = app.root.ids.comic_book_screen.page_nav_popup
            page_nav_popup.dismiss()
            carousel = App.get_running_app().root.ids.comic_book_screen.ids.comic_book_carousel
            for slide in carousel.slides:
                if slide.id == self.id:
                    use_slide = slide
            carousel.load_slide(use_slide)

class ComicBookPageThumb(ButtonBehavior,Image):
        '''Fired once the image is downloaded and ready to use'''
        comic_slug = StringProperty()
        fetch_data = ObjectProperty()
        comic_page = NumericProperty()
        def __init__(self,**kwargs):
            super(ComicBookPageThumb, self).__init__(**kwargs)
            base_url = App.get_running_app().config.get('Server', 'url')
            fetch_data = ComicServerConn()
            url_send = f'{base_url}issue/{self.comic_slug}/get-page/{self.comic_page}/'
            fetch_data.get_server_data(url_send,self)

        def got_json(self,req, result):     
            img = convert_to_image(result["page"])
            self.texture = img.texture
        def click(self,instance):
            app = App.get_running_app()
            # app.root.current = 'comic_book_screen'
            page_nav_popup = app.root.ids.comic_book_screen.page_nav_popup
            page_nav_popup.dismiss()
            carousel = App.get_running_app().root.ids.comic_book_screen.ids.comic_book_carousel
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
    comic = ObjectProperty()
    readinglist_obj = ObjectProperty()
    clock_set = StringProperty()


    def enable_me(self,instance):
        Logger.debug('enabling %s'%self.id)
        self.disabled = False

    def open_comic(self,*args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        new_reading_list = ComicReadingList()
        new_reading_list.add_comic(self.comic)
        comic_screen = app.manager.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,new_reading_list)
        Clock.schedule_once(self.enable_me, .5)

    def open_collection(self,*args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.manager.get_screen('comic_book_screen')
        comic_screen.use_pagination = False
        comic_screen.last_load = 0
        comic_screen.load_comic_book(self.comic,self.readinglist_obj)
        Clock.schedule_once(self.enable_me, .5)

    def open_next_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.manager.get_screen('comic_book_screen')
        comic_screen.load_comic_book(self.comic,self.readinglist_obj)
        Clock.schedule_once(self.enable_me, .5)

    def open_prev_section(self, *args):
        self.disabled = True
        app = App.get_running_app()
        app.root.current = 'comic_book_screen'
        comic_screen = app.manager.get_screen('comic_book_screen')
        comic_screen.last_load = comic_screen.last_section
        comic_screen.load_comic_book(self.comic,self.readinglist_obj)
        Clock.schedule_once(self.enable_me, .5)

