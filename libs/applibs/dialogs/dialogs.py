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
from kivy.metrics import dp
from kivy.uix.modalview import ModalView

from kivymd.cards import MDCard, MDSeparator
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.button import MDFlatButton

from . selection import Selection


Builder.load_string(
'''
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDTextField kivymd.textfields.MDTextField

# Окно для ввода текста.

[InputText@ModalView]:
    size_hint: .8, .4
    background_color: 0, 0, 0, .2

    MDCard:

        BoxLayout:
            orientation: 'vertical'
            padding: dp(15)

            MDLabel:
                font_style: 'Title'
                theme_text_color: 'Primary'
                text: ctx.title
                halign: 'left'

            MDTextField:
                id: text_field
                size_hint: 1, None
                height: dp(48)
                hint_text: ctx.hint_text

            Widget:
            Widget:

            AnchorLayout:
                anchor_x: 'right'
                size_hint: 1, None
                height: dp(48)
                padding: dp(8), dp(8)
                spacing: dp(4)

                GridLayout:
                    rows: 1
                    size_hint: None, None
                    height: dp(36)
                    width: self.minimum_width

                    MDFlatButton:
                        text: ctx.text_button_ok
                        on_release: ctx.events_callback(text_field.text)
                        theme_text_color: 'Custom'
                        text_color: app.theme_cls.primary_color

                    MDFlatButton:
                        text: ctx.text_button_cancel
                        on_release: ctx.events_callback(None)
                        theme_text_color: 'Custom'
                        text_color: app.theme_cls.primary_color

# Окно прогресса.

[Progress@ModalView]:
    size_hint: .8, .4
    background_color: 0, 0, 0, .2
    auto_dismiss: False

    MDCard:
        BoxLayout:
            orientation: 'vertical'
            padding: dp(0), dp(10)

            Widget:

            MDSpinner:
                id: progress
                size_hint: None, None
                size: dp(46), dp(46)
                pos_hint: {'center_x': .5}
                active: True

            Label:
                id: label
                text: ctx.text_wait
                color: ctx.text_color
                markup: True
                halign: 'center'
                size_hint_y: None
                font_size: '14sp'
                height: dp(50)

            Widget:

            MDFlatButton:
                text: ctx.text_button_cancel
                pos_hint: {'center_x': .5}
                theme_text_color: 'Custom'
                text_color: app.theme_cls.primary_color
                on_release: ctx.events_callback(ctx.text_button_cancel)
'''
)


def dialog(font_style='Body1', theme_text_color='Secondary', title='Title',
           text='Text', valign='top', dismiss=True, buttons=None,
           use_check=False, text_check='', height=300, size_hint=(.85, None),
           ref_callback=None, check_callback=None):
    '''Вывод диалоговых окон.'''

    if buttons is None:
        buttons = []

    text_dialog = MDLabel(
        font_style=font_style, theme_text_color=theme_text_color,
        text=text, valign=valign, markup=True,
        size_hint_y=None
    )
    dialog = MDDialog(
        title=title, content=text_dialog, size_hint=size_hint,
        auto_dismiss=dismiss, height=dp(height)
    )

    text_dialog.bind(texture_size=text_dialog.setter('size'))
    if ref_callback:
        text_dialog.bind(on_ref_press=ref_callback)

    if use_check:
        selection = Selection(text=text_check)
        if check_callback:
            selection.callback = check_callback
        dialog.children[0].children[1].add_widget(selection)

    for list_button in buttons:
        text_button, action_button = list_button
        dialog.add_action_button(text_button, action=action_button)
    dialog.open()

    return dialog


def dialog_progress(text_button_cancel='Cancel', text_wait='Wait',
                    events_callback=None, text_color=None):
    if not text_color:
        text_color = [0, 0, 0, 1]

    spinner = Builder.template(
        'Progress', text_button_cancel=text_button_cancel,
        text_wait=text_wait, events_callback=events_callback,
        text_color=text_color
    )
    spinner.open()

    return spinner, spinner.ids.label

def input_dialog(title='Title', hint_text='Write something',
                 text_button_ok='OK', text_button_cancel='CANCEL',
                 events_callback=None):
    input_dialog = Builder.template(
        'InputText', title=title, hint_text=hint_text,
        text_button_ok=text_button_ok, text_button_cancel=text_button_cancel,
        events_callback=events_callback
     )
    input_dialog.open()

    return input_dialog


def card(content, title=None, background_color=None, size=(.7, .5)):
    '''Вывод диалоговых окон с кастомным контентом.'''

    if not background_color:
        background_color = [1.0, 1.0, 1.0, 1]

    card = MDCard(size_hint=(1, 1), padding=5) #, background_color=background_color)

    if title:
        box = BoxLayout(orientation='vertical', padding=dp(8))
        box.add_widget(
            MDLabel(
                text=title, theme_text_color='Secondary', font_style="Title",
                size_hint_y=None, height=dp(36)
            )
        )
        box.add_widget(MDSeparator(height=dp(1)))
        box.add_widget(content)
        card.add_widget(box)
    else:
        card.add_widget(content)

    dialog = ModalView(size_hint=size, background_color=[0, 0, 0, .2])
    dialog.add_widget(card)
    #dialog.open()

    return dialog
