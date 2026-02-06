from __future__ import annotations

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock

class SplashScreen(Screen):
    def on_enter(self):
        # animate logo
        logo = self.ids.logo_label
        tagline = self.ids.tagline_label
        
        # Reset
        logo.opacity = 0
        tagline.opacity = 0
        logo.pos_hint = {"center_x": 0.5, "center_y": 0.45}
        
        # Sequence
        anim = Animation(opacity=1, pos_hint={"center_x": 0.5, "center_y": 0.5}, duration=1.2, t='out_back')
        anim.start(logo)
        
        anim_tag = Animation(opacity=1, duration=1.0)
        # Delay tagline slightly
        Clock.schedule_once(lambda dt: anim_tag.start(tagline), 0.8)
        
        # Transition to home after animation (3 seconds total)
        from kivy.app import App
        Clock.schedule_once(lambda dt: App.get_running_app().go_home(), 3.5)
