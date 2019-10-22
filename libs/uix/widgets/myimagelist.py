from kivy.lang import Builder
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    ObjectProperty,
    NumericProperty,
    ListProperty,
    OptionProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivymd.uix.button import MDIconButton
from kivymd.behaviors.ripplebehavior import RectangularRippleBehavior
from kivymd.theming import ThemableBehavior
from kivymd.uix.imagelist import SmartTileWithLabel, SmartTile
from kivymd.icon_definitions import md_icons

Builder.load_string(
    """
#:import md_icons kivymd.icon_definitions.md_icons

<ComicTileLabel>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box
    _box_label: boxlabel
    _box_header: box_header
    _box_icon: boxicon
    AsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        color: root.img_color
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top

    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos

    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color
            Rectangle:
                pos: self.pos
                size: self.size

        id: box#header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y + root.height - self.height

        MDLabel:
            id: boxlabel
            font_style: root.font_style
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: root.text
            color: root.tile_text_color
            markup: True

    BoxLayout:
        canvas:
            Color:
                rgba: 0, 0, 0, 0.5
            Rectangle:
                pos: self.pos
                size: self.size

        id: box_header
        size_hint_y: None
        padding: dp(5), 0, 0, 0
        height: self.minimum_height #dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y
        opacity:1

        MDIcon:
            id: boxicon
            icon_name: 'read'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: md_icons.get(self.icon_name)
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            opacity: 1 if root.is_read else 0
            font_size: dp(25)
        MDIcon:
            id: boxicon
            icon_name: 'file-check'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: md_icons.get(self.icon_name)
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            opacity: 1 if root.has_localfile else 0
            font_size: dp(25)
        MDLabel:
            id: boxlabel
            icon_name: 'cloud-sync'
            #halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            text: str(root.page_count_text)
            #root.page_count_text
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
"""
)


class ComicTileLabel(SmartTile):
    _box_label = ObjectProperty()
    _box_header = ObjectProperty()
    _box_icon = ObjectProperty()
    # MDLabel properties
    font_style = StringProperty("Caption")
    theme_text_color = StringProperty("Custom")
    tile_text_color = ListProperty([1, 1, 1, 1])
    text = StringProperty("")
    text_header = StringProperty("Sync")
    icon_name = StringProperty()
    is_read = BooleanProperty(False)
    has_localfile = BooleanProperty(False)
    box_header_opaticty = StringProperty(1)
    page_count_text = StringProperty()

    def __init__(self, **kwargs):
        super(ComicTileLabel, self).__init__(**kwargs)

    """Determines the text for the box footer/header"""


class SyncIcon(MDIconButton):
    def on_touch_down(self, touch):
        return True
