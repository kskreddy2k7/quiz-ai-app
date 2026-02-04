from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


class ReviewItem(BoxLayout):
    question_text = StringProperty("")
    answer_text = StringProperty("")
    explanation_text = StringProperty("")


class ReviewPopup(Popup):
    pass


class ResultsScreen(Screen):
    score_text = StringProperty("")
    encouragement_text = StringProperty("")
    explanation_text = StringProperty("")

    def open_review(self, filter_mistakes=False):
        app = App.get_running_app()
        popup = ReviewPopup()
        if filter_mistakes:
            popup.title = "Review Mistakes"
        
        content_list = popup.ids.review_list
        content_list.clear_widgets()

        for i, q in enumerate(app.active_questions):
            user_ans = app.user_answers.get(i, "No answer")
            is_correct = (user_ans == q.answer)
            
            if filter_mistakes and is_correct:
                continue

            # Formatting answer text to highlight correct/wrong
            ans_display = f"[color={'6BFF8A' if is_correct else 'FF6B6B'}]Selected: {user_ans}[/color]\n"
            if not is_correct:
                ans_display += f"[color=6BFF8A]Correct: {q.answer}[/color]"

            item = ReviewItem(
                question_text=f"Q{i+1}: {q.prompt}",
                answer_text=ans_display,
                explanation_text=q.explanation
            )
            content_list.add_widget(item)

        if filter_mistakes and not content_list.children:
             # If no mistakes, show a friendly message or don't open? 
             # Let's show a label.
             from kivy.uix.label import Label
             content_list.add_widget(Label(text="No mistakes! You're a pro! 🏆", size_hint_y=None, height="100dp"))

        popup.open()
