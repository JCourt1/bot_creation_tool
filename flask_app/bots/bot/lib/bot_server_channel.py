from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from twisted.web.static import File
from twisted.web.resource import NoResource
from klein import Klein
from collections import defaultdict
from datetime import datetime
import json
import logging
from uuid import uuid4
import jwt
import random
import pymongo

# from lib.dialogue_handler import DialogueHandler

from rasa_nlu.server import check_cors
from rasa_core.channels.channel import UserMessage
from rasa_core.channels.channel import InputChannel, OutputChannel
from rasa_core.events import SlotSet
from rasa_core.events import ConversationResumed, ActionExecuted

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/bschannel.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)



client = pymongo.MongoClient("mongodb://mhtmongodb:5xXKDKil2MeMigtUrUXHaksZwQocivCftlJ7CVtH842Gv9PmuSIphMc28enPsZUIPeikcfEjvkBCdSmkP5Wj7w==@mhtmongodb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
db = client['test-database']

class MongoDBMessageStore:

    def __init__(self):
        self._store = defaultdict(list)

        # cursor = db.conversations.find({"utterances": {"$exists": True}})
        # for document in cursor:
        #     k = document["cid"]
        #     v = document["utterances"]
        #     self._store[k] = v

    def log(self, cid, username, message, uuid=None):
        if uuid is None:
            uuid = str(uuid4())

        newUtterance = {
                            "time": datetime.utcnow().isoformat(),
                            "username": username,
                            "message": message,
                            "uuid": uuid
                        }
        self._store[cid].append(newUtterance)
        self.save(cid, newUtterance)

    def clear(self, cid):
        self._store[cid] = []
        db.conversations.update({'cid': cid}, {'$set': {'utterances': []}})
        # self.save()

    def save(self, cid, newUtterance):

        cid = bytes(cid.encode('utf-8'))

        db.conversations.update_one({'cid': cid}, { '$push': { 'utterances': newUtterance } }, upsert=True)

        # json.dump(self._store, open(self._filename, "w"))

    def __getitem__(self, key):
        return self._store[key]



# class FileMessageStore:
#
#     DEFAULT_FILENAME = "message_store.json"
#
#     def __init__(self, filename=DEFAULT_FILENAME):
#         self._store = defaultdict(list)
#         self._filename = filename
#         try:
#             for k, v in json.load(open(self._filename, "r")).items():
#                 self._store[k] = v
#         except IOError:
#             pass
#
#     def log(self, cid, username, message, uuid=None):
#         if uuid is None:
#             uuid = str(uuid4())
#         self._store[cid].append(
#             {
#                 "time": datetime.utcnow().isoformat(),
#                 "username": username,
#                 "message": message,
#                 "uuid": uuid
#             }
#         )
#         self.save()
#
#     def clear(self, cid):
#         self._store[cid] = []
#         self.save()
#
#     def save(self):
#         json.dump(self._store, open(self._filename, "w"))
#
#     def __getitem__(self, key):
#         return self._store[key]


class BotServerOutputChannel(OutputChannel):
    def __init__(self, message_store):
        self.message_store = message_store
        self.questionnaireInterrupt = None

    def send_text_message(self, cid, message):
        self.message_store.log(cid, "bot", {"type": "text", "text": message})

    def send_text_with_buttons(self, cid, message, buttons, **kwargs):

        self.send_text_message(cid, message)
        self.message_store.log(
            cid, "bot", {"type": "button", "buttons": buttons}
        )

    def send_image_url(self, cid, url):

        self.message_store.log(
            cid, "bot", {"type": "image", "image": url}
        )


class BotServerInputChannel(InputChannel):

    app = Klein()


    def __init__(
        self, agent, dialogue_handler, port=5002, static_files=None, message_store=MongoDBMessageStore()
    ):
        logging.basicConfig(level="DEBUG")
        logging.captureWarnings(True)
        self.message_store = message_store
        self.static_files = static_files
        self.on_message = lambda x: None
        self.cors_origins = [u'*']
        # self.cors_origins = [u'http://localhost:4000']
        self.agent = agent
        self.port = port
        self.dialogue_handler = dialogue_handler
        self.DIALOGUE_ERRORS = ["That dialogue is non existant", "Please choose one of the dialogues presented above"]

    def setHeaders(self, request):
        request.setHeader("Content-Type", "application/json")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        # request.setHeader("Access-Control-Allow-Origin", "http://127.0.0.1:4000")
        # request.setHeader("Access-Control-Allow-Origin", "http://0.0.0.0:4000")
        # request.setHeader("Access-Control-Allow-Origin", "http://0.0.0.0")

        ## trick for getting past the cookies problem.
        allowed_header = request.getHeader('Origin')
        request.setHeader("Access-Control-Allow-Origin", allowed_header)

    def getCurrentPointInDialogue(self, request):
        if request.getCookie(b'dialogue_step') is None:
            currentDialogueStep = "0"
        elif jwt.decode(request.getCookie(b'dialogue_step'), '@TODO Secret', algorithm='HS256')['pointInDialogue'] == 'None':
            currentDialogueStep = "0"
        else:
            currentDialogueStep = jwt.decode(request.getCookie(b'dialogue_step'), '@TODO Secret', algorithm='HS256')["pointInDialogue"]
        return currentDialogueStep

    def resetCookie(self, request, cookie_name, key, value):
        cookie_value = jwt.encode({key: value}, '@TODO Secret', algorithm='HS256')
        request.addCookie(bytes(cookie_name, encoding='utf-8'), cookie_value)



    @app.route("/conversations/<cid>/log")
    @check_cors
    def show_log(self, request, cid):

        self.setHeaders(request)

        if request.getCookie(b'session_token') is None:
            session_id = uuid4().hex
            session_token = jwt.encode({'foo': session_id}, '@TODO Secret', algorithm='HS256')
            request.addCookie(b'session_token', session_token)
            logger.info("Session id is set to {}".format(session_id))
        else:
            session_token = jwt.decode(request.getCookie(b'session_token'), '@TODO Secret', algorithm='HS256')
            logger.info("Session token is {}".format(session_token))

        return json.dumps(self.message_store[cid])



    @app.route("/conversations/<cid>/say", methods=["GET"])
    @check_cors
    def say(self, request, cid):

        self.setHeaders(request)

        message, = request.args.get(b"message", [])
        _payload = request.args.get(b"payload", [])
        _display_name = request.args.get(b"display_name", [])
        _uuid = request.args.get(b"uuid", [])
        logger.info(message)

        message = message.decode("utf-8")

        output_channel = BotServerOutputChannel(self.message_store)

        if message == "_restart":
            self.message_store.clear(cid)
        else:
            if len(_uuid) > 0:
                self.message_store.log(
                    cid,
                    cid,
                    {"type": "text", "text": message},
                    _uuid[0].decode("utf-8"),
                )
            else:
                self.message_store.log(
                    cid, cid, {"type": "text", "text": message}
                )

        tracker = self.agent.tracker_store.get_or_create_tracker(cid)
        paused_flag = tracker.is_paused()

        logger.info(tracker.current_state())
        logger.info("message is %s" % message)

        if len(_payload) > 0:
            logger.info("using payload")
            self.on_message(
                UserMessage(
                    _payload[0].decode("utf-8"),
                    output_channel= output_channel,
                    sender_id=cid,
                )
            )
        else:
            logger.info("using message")
            self.on_message(
                UserMessage(
                    message,
                    output_channel= output_channel,
                    sender_id=cid,
                )
            )

        tracker = self.agent.tracker_store.get_or_create_tracker(cid)
        intent = tracker.latest_message.intent
        logger.info(intent)

        if output_channel.questionnaireInterrupt is not None:
            paused_flag = True
            message = output_channel.questionnaireInterrupt
            output_channel.questionnaireInterrupt = None

        if paused_flag:

            dname_cookie = request.getCookie(b'dialogue_name')
            dname_val_is_None = False if dname_cookie is None else jwt.decode(request.getCookie(b'dialogue_name'), '@TODO Secret', algorithm='HS256')['name'] == 'None'

            dg_is_valid = True

            if dname_cookie is None or dname_val_is_None:

                flag, type = self.dialogue_handler.check_dialogue_exists(message)

                if flag:
                    dialogueName = message
                    dialogue_name = jwt.encode({'name': message}, '@TODO Secret', algorithm='HS256')
                    request.addCookie(b'dialogue_name', dialogue_name)
                else:
                    errorChoosingDialogue = random.choice(self.DIALOGUE_ERRORS)
                    logger.info(errorChoosingDialogue)
                    output_channel.send_text_message(cid, errorChoosingDialogue)
                    dg_is_valid = False
            else:
                dialogueName = jwt.decode(request.getCookie(b'dialogue_name'), '@TODO Secret', algorithm='HS256')['name']
                logger.info(dialogueName)

            if dg_is_valid:

                currentPointInDialogue = self.getCurrentPointInDialogue(request)

                try:
                    newPointInDialogue = self.dialogue_handler.handle_dialogue(dialogueName, currentPointInDialogue, output_channel, cid, message, intent['name'])
                except:
                    newPointInDialogue = "finished"

                if newPointInDialogue is not "finished": # just increment the step
                    logger.info("incrementing step cookie")
                    self.resetCookie(request, 'dialogue_step', 'pointInDialogue', newPointInDialogue)
                else: ## unpause the tracker
                    logger.info("dialogue is finished")
                    events = [ConversationResumed()]

                    action_name = "special_resume_action_name"
                    if action_name is not None:
                        tracker.update(ActionExecuted(action_name))

                    for e in events:
                        tracker.update(e)

                    self.agent.tracker_store.save(tracker)

                    self.resetCookie(request, 'dialogue_name', 'name', 'None')
                    self.resetCookie(request, 'dialogue_step', 'pointInDialogue', 'None')


    @app.route("/health", methods=["GET"])
    def health(self, request):
        return "healthy"

    @app.route("/", branch=True, methods=["GET"])
    @check_cors
    def static(self, request):
        if self.static_files is None:
            return NoResource()
        else:
            return File(self.static_files)

    def start(self, on_message):
        self.on_message = on_message
        logger.info("Started http server on port %d" % self.port)
        self.app.run("0.0.0.0", self.port)

    def start_async_listening(self, message_queue):
        self.start(message_queue.enqueue)

    def start_sync_listening(self, message_handler):
        self.start(message_handler)
