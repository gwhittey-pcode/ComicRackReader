from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivy.properties import StringProperty
from kivy.metrics import dp


class MDTooltipIconButton(MDIconButton, MDTooltip):
    pass


class MDToolbarTooltips(MDToolbar):
    tooltip_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_action_bar(self, action_bar, action_bar_items):
        action_bar.clear_widgets()
        new_width = 0
        for item in action_bar_items:
            new_width += dp(48)
            action_bar.add_widget(
                MDTooltipIconButton(
                    icon=item[0],
                    on_release=item[2],
                    opposite_colors=True,
                    text_color=self.specific_text_color,
                    theme_text_color="Custom",
                    tooltip_text=item[1],
                )
            )
        action_bar.width = new_width
