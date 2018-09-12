from rasa_core.actions.action import Action
from rasa_core.events import ConversationPaused
from rasa_core.events import SlotSet, Restarted
import requests
import random
import json
import pymongo

client = pymongo.MongoClient("mongodb://mhtmongodb:5xXKDKil2MeMigtUrUXHaksZwQocivCftlJ7CVtH842Gv9PmuSIphMc28enPsZUIPeikcfEjvkBCdSmkP5Wj7w==@mhtmongodb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
db = client['test-database']

#### https://www.twitch.tv/videos/279105616
####
#### Tutorial by the rasa team about custom actions


class SayGoodbye(Action):
    def name(self):
        return "action_say_goodbye"

    def run(self, dispatcher, tracker, domain):

        messages = ["Bye then! Hope to speak soon.", "Goodbye! Come back and speak with me soon!", "Ok, I hope you will be back soon!", "Bye then, it was good to talk to you."]
        dispatcher.utter_message(random.choice(messages))

        return [Restarted()]




class ReplyToFeelingExpressed(Action):
    def name(self):
        return "reply_to_feeling"

    def run(self, dispatcher, tracker, domain):
        slot = tracker.get_slot('sentiment')
        senderID = tracker.current_state()["sender_id"]
        senderID = bytes(senderID.encode('utf-8'))
        senderName = db.users.find_one({"cids": senderID}, {"userName": 1, '_id': 0})
        senderName = senderName['userName'] if senderName is not None else ''

        print("sender ID is: {} \n\n\n\n\n".format(senderID))
        print(db.users.find_one({"userName": "JoeC"}))

        if slot == "Depressed":
            message = "I'm sorry to hear that {}."
        elif slot == "Anxious":
            message = "I'm sorry to hear that {}."
        elif slot == "Happy":
            message = "That's great to hear {}!"
        else:
            message = "Alright."

        dispatcher.utter_message(message.format(senderName))

        return []

class ShowDialogues(Action):

    def name(self):
        return "show_dialogues"

    def run(self, dispatcher, tracker, domain, d_names=[]):
        # dispatcher.utter_template("present_dialogues")
        textArray = ["I can talk about any of these things:", "Here are all the things I know about, choose one!", "Here are all the things we can talk about:"]
        buttons = [{"payload": d, "title": d} for d in d_names]

        dispatcher.utter_button_message(random.choice(textArray), buttons)

        return [ConversationPaused()]

class ShowQuestionnaires(Action):

    def name(self):
        return "show_questionnaires"

    def run(self, dispatcher, tracker, domain, q_names=[]):
        # dispatcher.utter_template("present_dialogues")
        textArray = ["Here are all the questionnaires:", "These are the questionnaires: "]
        buttons = [{"payload": q, "title": q} for q in q_names]

        dispatcher.utter_button_message(random.choice(textArray), buttons)

        return [ConversationPaused()]


class ShowPHQ9(Action):

    def name(self):
        return "show_phq9"

    def run(self, dispatcher, tracker, domain, botoutput):

        dispatcher.utter_message("Ok, let's begin.")
        dispatcher.output_channel.questionnaireInterrupt = "phq9"

        return [ConversationPaused()]


class ShowGAD7(Action):

    def name(self):
        return "show_gad7"

    def run(self, dispatcher, tracker, domain, q_names=[]):
        # dispatcher.utter_template("present_dialogues")

        dispatcher.utter_message("Ok, let's begin.")
        dispatcher.output_channel.questionnaireInterrupt = "gad7"

        return [ConversationPaused()]

class LogSelfHarmMessage(Action):
    def name(self):
        return "action_log_self_harm"

    def run(self, dispatcher, tracker, domain):

        responses = ["I'm really sorry to hear you are feeling that way.", "I am really sorry about that.", "I am sorry for what you are going through."]

        dispatcher.utter_message(random.choice(responses))
        db.conversations.update_one({'cid': bytes(tracker.sender_id.encode('utf-8'))}, { "$set": {"selfHarmFlag": 1}}, upsert=True)

        return []

# class ActionShowTracker(Action):
#
#     def name(self):
#         return "action_show_tracker"
#
#     def run(self, dispatcher, tracker, domain):
#         cur_state = tracker.current_state()
#
#         dispatcher.utter_message(json.dumps(cur_state))
#
#         return []




#
# class RandomTest(Action):
#     def name(self):
#         return "random_test"
#
#     def run(self, dispatcher, tracker, domain):
#
#         r = requests.get('https://api.blablabla.com/blabla')
#         response = json.loads(r.text)
#
#
#         slotty = tracker.get_slot('someSlot')
#         dispatcher.utter_message(message)
#
#         return [SlotSet('someSlot', url_name)]
