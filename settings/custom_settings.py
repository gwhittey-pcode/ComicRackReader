
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingItem, SettingSpacer, SettingString
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty, StringProperty, ListProperty, \
    BooleanProperty, NumericProperty, DictProperty
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp


class MySettings(SettingsWithSidebar):
    '''Customized settings panel.
    '''

    def __init__(self, *args, **kargs):
        super(MySettings, self).__init__(*args, **kargs)
        self.register_type('hotkeys', SettingHotkeys)


class SettingHotkeys(SettingString):
    '''Implementation of a string setting on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.textinput.Textinput` so the user can enter a custom
    value.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it's shown.
        :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
        to None.
        '''

    textinput = ObjectProperty(None)
    '''(internal) Used to store the current textinput from the popup and
        to listen for changes.
        :attr:`textinput` is an :class:`~kivy.properties.ObjectProperty` and
        defaults to None.
        '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def _dismiss(self, *largs):
        if self.textinput:
            self.textinput.focus = False
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _validate(self, instance):
        self._dismiss()
        value = self.textinput.text.strip()
        self.value = value

    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = KeyInputPopup(
            title='Type the Key for this hotkey', content=content, size_hint=(None, None),
            size=(popup_width, '250dp'))
        self.popup.setting_obj = self
        # create the textinput used for numeric input
        self.textinput = textinput = TextInput(
            text=self.value, font_size='24sp', multiline=False,
            size_hint_y=None, height='42sp', readonly=True, disabled=True)
        textinput.bind(on_text_validate=self._validate)
        self.textinput = textinput

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(textinput)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class KeyInputPopup(Popup):
    setting_obj = ObjectProperty()

    def __init__(self, **kwargs):
        super(KeyInputPopup, self).__init__(**kwargs)

    def on_open(self, *args):
        print('open')
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('jeydown')

        code, key = keycode
        self.setting_obj.textinput.text = key
        print(f'keycode:{code}')
        # self.dismiss()
