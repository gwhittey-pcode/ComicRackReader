# -*- coding: utf-8 -*-

'''
VKGroups

Copyright © 2010-2018 HeaTTheatR

Для предложений и вопросов:
<kivydevelopment@gmail.com>

Данный файл распространяется по условиям той же лицензии,
что и фреймворк Kivy.

'''

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty


ACTIVITY = '''
#:import MDLabel kivymd.label.MDLabel
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox

<Selection>:
    spacing: dp(5)
    size_hint_y: None
    height: dp(48)

    MDCheckbox:
        id: check
        size_hint: None, None
        size: dp(40), dp(40)
        on_state: root.callback(self.active)
        pos_hint: {'center_y': .5}

    MDLabel:
        id: label
        text: root.text
        markup: True
        theme_text_color: 'Primary'
        halign: 'left'
'''


class Selection(BoxLayout):
    text = StringProperty()
    callback = ObjectProperty(lambda x: None)


Builder.load_string(ACTIVITY)
