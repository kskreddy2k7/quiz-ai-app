from __future__ import annotations

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from app.ui.theme import Theme

class QuizOptionWidget(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    selected = BooleanProperty(False)
    is_correct = BooleanProperty(False)
    revealed = BooleanProperty(False)
    
    # Internal usage
    bg_color = ListProperty([0, 0, 0, 0])
    
    def on_state(self, instance, value):
        self._update_color()

    def on_selected(self, instance, value):
        self._update_color()
        
    def on_revealed(self, instance, value):
        self._update_color()

    def _update_color(self):
        # Default State
        base_color = Theme.color(Theme.BG_CARD, 0.6)
        
        if self.revealed:
            if self.is_correct:
                self.bg_color = Theme.color(Theme.ACCENT_TEAL, 0.8) # Green
            elif self.selected:
                self.bg_color = Theme.color(Theme.ACCENT_RED, 0.8) # Red
            else:
                 self.bg_color = Theme.color(Theme.BG_CARD, 0.3) # Dim others
        elif self.selected:
             self.bg_color = Theme.color(Theme.PRIMARY, 0.6) # Highlight selected before submit (if we had 2-step)
             # In this app, selection = immediate submit, so this state is transient
        else:
             self.bg_color = base_color


class QuizPlayScreen(Screen):
    question_text = StringProperty("")
    option_texts = ListProperty([])
    progress_text = StringProperty("")
    
    # State
    options_widgets = ListProperty([])
    selected_option = StringProperty("")

    def on_option_texts(self, instance, value):
        self._build_options()

    def _build_options(self):
        container = self.ids.options_container
        container.clear_widgets()
        self.options_widgets = []
        self.selected_option = ""
        self.ids.submit_btn.disabled = True
        
        for opt_text in self.option_texts:
            widget = QuizOptionWidget(text=opt_text)
            widget.bind(on_release=self.on_option_select)
            container.add_widget(widget)
            self.options_widgets.append(widget)

    def on_option_select(self, widget):
        # Update selection state
        for w in self.options_widgets:
            w.selected = (w == widget)
        
        self.selected_option = widget.text
        self.ids.submit_btn.disabled = False

    def submit_selection(self):
        if not self.selected_option:
            return
            
        app = App.get_running_app()
        if not app.active_questions: 
            return
            
        # Lock everything
        for w in self.options_widgets:
            w.disabled = True
        self.ids.submit_btn.disabled = True
            
        app.submit_answer(self.selected_option)
