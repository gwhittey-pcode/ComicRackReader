from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.theming import ThemeManager

Builder.load_string("""
#:import MDRaisedButton kivymd.uix.button.MDRaisedButton


<MyLabel@Label>
    color: 0, 0, 0, 1
    size_hint: None, None
    size: self.texture_size


<MyScreen@Screen>
    RecycleView:
        id: rv
        key_viewclass: 'viewclass'
        key_size: 'height'

        RecycleBoxLayout:
            padding: dp(10)
            spacing: dp(10)
            default_size: None, dp(48)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'


<ItemList>
    padding: dp(15)
    spacing: dp(10)
    elevation: 10

    Image:
        source: "data/logo/kivy-icon-128.png"
        size_hint: None, None
        size: dp(48), dp(48)
        pos_hint: {"center_y": .5}
    
    BoxLayout:
        orientation: "vertical"
        pos_hint: {"center_y": .5}
        size_hint: None, None
        size: self.minimum_size

        MyLabel:
            text: "Welcome"

        MyLabel:
            text: "to"

        MyLabel:
            text: "hell"
            
    Widget:
        
    MDRaisedButton:
        text: "Press"
        pos_hint: {"center_y": .5}
""")


class ItemList(MDCard):
    pass


class Test(App):
    theme_cls = ThemeManager()

    def build(self):
        return Factory.MyScreen()

    def on_start(self):
        for i in range(50):
            self.root.ids.rv.data.append(
                {
                    "viewclass": "ItemList",
                    "height": dp(64)
                }
            )


Test().run()
