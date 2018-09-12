from rasa_core.actions.action import Action
from rasa_core.events import ConversationPaused
from rasa_core.events import SlotSet
import requests
import random
import json

#### https://www.twitch.tv/videos/279105616
####
#### Tutorial by the rasa team about custom actions


class SayGoodbye(Action):
    def name(self):
        return "action_say_goodbye"

    def run(self, dispatcher, tracker, domain):

        messages = ["Bye then! Hope to speak soon.", "Goodbye! Come back and speak with me soon!", "Ok, I hope you will be back soon!", "Bye then, it was good to talk to you."]
        dispatcher.utter_message(random.choice(messages))

        return []

class ReplyToFeelingExpressed(Action):
    def name(self):
        return "reply_to_feeling"

    def run(self, dispatcher, tracker, domain):
        slotty = tracker.get_slot('sentiment')
        senderID = tracker.current_state()["sender_id"]

        if slotty == "Depressed":
            message = "I'm sorry to hear that {}."
        elif slotty == "Anxious":
            message = "I'm sorry to hear that {}."
        elif slotty == "Happy":
            message = "That's great to hear {}!"
        else:
            message = "Alright."

        dispatcher.utter_message(message.format("[patient's name]"))

        return []

class ShowDialogues(Action):

    def name(self):
        return "show_dialogues"

    def run(self, dispatcher, tracker, domain, d_names=[]):
        # dispatcher.utter_template("present_dialogues")

        dispatcher.utter_message("(The patient is presented with all dialogues)")

        return []

class ShowQuestionnaires(Action):

    def name(self):
        return "show_questionnaires"

    def run(self, dispatcher, tracker, domain, q_names=[]):
        # dispatcher.utter_template("present_dialogues")

        dispatcher.utter_message("(The patient is presented with a list of all questionnaires)")

        return []


class ShowPHQ9(Action):

    def name(self):
        return "show_phq9"

    def run(self, dispatcher, tracker, domain, q_names=[]):

        dispatcher.utter_message("(The patient is presented with the PHQ9 questionnaire)")

        return []


class ShowGAD7(Action):

    def name(self):
        return "show_gad7"

    def run(self, dispatcher, tracker, domain, q_names=[]):

        dispatcher.utter_message("(The patient is presented with the GAD7 questionnaire)")


        return []


class LogSelfHarmMessage(Action):
    def name(self):
        return "action_log_self_harm"

    def run(self, dispatcher, tracker, domain):

        responses = ["I'm really sorry to hear you are feeling that way.", "I am really sorry about that.", "I am sorry for what you are going through."]

        dispatcher.utter_message(random.choice(responses))
        # db.conversations.update_one({'cid': tracker.sender_id}, { "$set": {"selfHarmFlag": 1}}, upsert=True)
        dispatcher.utter_message("(Conversation is flagged as featuring self harm)")

        return []
