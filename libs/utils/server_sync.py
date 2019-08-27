from kivy.app import App
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.label import Label


def sync_server_reduced(reading_list_obj=None,):
    def my_callback(instance):
        print('Popup', instance, 'is being dismissed but is prevented!')
        return True
    for comic in reading_list_obj.comics:
        print(comic.__str__)
    popup = Popup(content=Label(text=reading_list_obj.name),
                  size_hint=(.5, .32))
    # popup.bind(on_dismiss=my_callback)
    popup.open()
