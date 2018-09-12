from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys, time
from twisted.web.static import File
from twisted.web.resource import NoResource
from twisted.internet import reactor
from klein import Klein
from collections import defaultdict
from datetime import datetime
import json
import logging
from uuid import uuid4
import multiprocessing
import argparse

from lib.my_agent import CustomAgent

from rasa_core import utils
from rasa_nlu.server import check_cors
from rasa_core.channels.channel import InputChannel, OutputChannel, UserMessage
from rasa_core.policies.sklearn_policy import SklearnPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.featurizers import MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer
from rasa_core.interpreter import NaturalLanguageInterpreter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/launchTrain.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class FileMessageStore():

    DEFAULT_FILENAME = "message_store.json"

    def __init__(self, filename=DEFAULT_FILENAME):
        self._store = defaultdict(list)
        self._filename = filename

    def log(self, cid, username, message, uuid=None):
        if uuid is None:
            uuid = str(uuid4())
        self._store[cid].append(
            {
                "time": datetime.utcnow().isoformat(),
                "username": username,
                "message": message,
                "uuid": uuid,
            }
        )
        self.save()

    def removeHintsOfType(self, cid, type):
        self._store[cid] = list(filter(lambda x: x["message"]["type"] != type, self._store[cid]))

    def clear(self, cid):
        self._store[cid] = []
        self.save()

    def save(self):
        json.dump(self._store, open(self._filename, "w"))

    def __getitem__(self, key):
        return self._store[key]


class CommunicationOutputChannel(OutputChannel):
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def send_text_message(self, recipient_id, message):
        self.output_queue.put(message)

    #######

    def send_training_hint(self, recipient_id, message):
        self.output_queue.put(["thint", message])

    #######

    def send_text_with_buttons(self, recipient_id, message, buttons, **kwargs):
        """Sends buttons to the output.
        Default implementation will just post the buttons as a string."""

        self.send_text_message(recipient_id, message)
        self.output_queue.put(["button", buttons])

    def send_image_url(self, recipient_id, image_url):
        # type: (Text, Text) -> None
        """Sends an image. Default will just post the url as a string."""

        self.output_queue.put(["img_url", image_url])



class CommunicationChannel(InputChannel):

    app = Klein()

    def __init__(self, to_bot_queue, to_human_queue, message_store=FileMessageStore(), port=5002):
        logging.basicConfig(level="DEBUG")
        logging.captureWarnings(True)
        self.message_store = message_store
        self.port = port
        self.cors_origins = [u'*']
        self.to_bot_queue = to_bot_queue
        self.to_human_queue = to_human_queue
        self.flag = False



    @app.route("/conversations/<cid>/log", methods=["GET"])
    @check_cors
    def show_log(self, request, cid):
        request.setHeader("Content-Type", "application/json")
        while not self.to_human_queue.empty():
            response = self.to_human_queue.get()
            # logger.info(response)
            if response == "SHUTDOWN":
                self.message_store.clear(cid)
                reactor.stop()
            elif response == "UNLOCK_FLAG":
                self.flag = False
            elif isinstance(response,(list,)):

                msg_type = response[0]
                if msg_type in ["thintBotAction", "thintHistory", "thintActionList", "thintKeyOptions"]:
                    self.message_store.log(cid, "bot", {"type": msg_type, "text": response[1]})
                elif msg_type == "button":
                    self.message_store.log(
                        recipient_id, "bot", {"type": msg_type, "buttons": response[1]}
                    )
                elif msg_type == "img_url":
                    self.message_store.log(
                        recipient_id, "bot", {"type": "image", "image": response[1]}
                    )
                else:
                    raise Exception("response type isn't an allowed value")

            else:
                self.message_store.log(cid, "bot", {"type": "text", "text": response})
        return json.dumps(self.message_store[cid])


    @app.route("/conversations/<cid>/say", methods=["GET"])
    @check_cors
    def say(self, request, cid):

        message, = request.args.get(b"message", [])
        _payload = request.args.get(b"payload", [])
        _display_name = request.args.get(b"display_name", [])
        _uuid = request.args.get(b"uuid", [])

        if self.flag:
            self.to_bot_queue.put(message.decode("utf-8"))
        else:
            usrmsg = UserMessage(
                message.decode("utf-8"),
                output_channel=CommunicationOutputChannel(self.to_human_queue),
                sender_id=cid,
            )

            self.flag = True
            self.to_bot_queue.put(usrmsg)


    def start(self):
        logger.info("Started http server on port %d" % self.port)
        self.app.run("0.0.0.0", self.port)


    @app.route("/health", methods=["GET"])
    @check_cors
    def health(self, request):
        return "healthy"

    @app.route("/", branch=True, methods=["GET"])
    def static(self, request):
        if self.static_files is None:
            return NoResource()
        else:
            return File(self.static_files)


def server(to_bot_queue, to_human_queue):

    channel = CommunicationChannel(to_bot_queue, to_human_queue)
    channel.start()







class TrainingInputChannel(InputChannel):

    def __init__(self, to_bot_queue, to_human_queue):
        self.on_message = None
        self.tracker_store = None
        self.to_bot_queue = to_bot_queue
        self.to_human_queue = to_human_queue
        self.counter = 0

    def start(self):

        while True:
            if self.counter == 0:
                logger.info("I've started")
            # logger.info("I've gone %s time(s)" % self.counter)
            self.counter += 1

            usrmsg = to_bot_queue.get()
            self.on_message(usrmsg, to_bot_queue, to_human_queue)
            to_human_queue.put("UNLOCK_FLAG")


    def start_async_listening(self, message_queue):
        self.start(message_queue.enqueue)

    def start_sync_listening(self, message_handler, tracker_store):
        self.on_message = message_handler
        self.tracker_store = tracker_store
        self.start()


def trainingBot(to_bot_queue, to_human_queue, base_model, output_model, nlu_model, training_data):

    utils.configure_colored_logging(loglevel="INFO")


    max_history = None
    interactive_learning_on = True

    channel = TrainingInputChannel(to_bot_queue, to_human_queue)
    preloaded_model = True

    if preloaded_model:
        agent = CustomAgent.load(base_model, NaturalLanguageInterpreter.create(nlu_model))
        training_data = agent.load_data(training_data)

        agent.train_online_preloaded_model(
                training_data,
                input_channel=channel,
                model_path=output_model)
    else:
        agent = CustomAgent("domain.yml",
                      policies=[MemoizationPolicy(max_history=max_history), KerasPolicy(MaxHistoryTrackerFeaturizer(BinarySingleStateFeaturizer(),
                                                                   max_history=max_history)), FallbackPolicy(fallback_action_name="utter_fallback", nlu_threshold=0.3)])

        training_data = agent.load_data(training_data)
        agent.interpreter = NaturalLanguageInterpreter.create(nlu_model)
        agent.train_online(
                training_data,
                input_channel=channel,
                model_path=output_model,
                augmentation_factor=50,
                epochs=250,
                batch_size=10,
                validation_split=0.2)

    agent.persist(output_model)


def create_argparser():
    parser = argparse.ArgumentParser(
            description='starts training')

    parser.add_argument(
        '-b', '--baseModel',
        required=True,
        type=str,
        help="core model to run")

    parser.add_argument(
        '-d', '--destinationModel',
        type=str,
        help="nlu model to run")

    return parser



if __name__ == '__main__':

    ### Multiprocessing setup
    import multiprocessing.managers
    backup_autoproxy = multiprocessing.managers.AutoProxy

    def redefined_autoproxy(token, serializer, manager=None, authkey=None,
          exposed=None, incref=True, manager_owned=True):
        return backup_autoproxy(token, serializer, manager, authkey,
                         exposed, incref)
    multiprocessing.managers.AutoProxy = redefined_autoproxy

    m = multiprocessing.Manager()

    to_bot_queue = m.Queue()
    to_human_queue = m.Queue()


    parser = create_argparser()
    cmdline_args = parser.parse_args()

    base_model = '../models/dialogueModels/' + cmdline_args.baseModel
    output_model = '../models/dialogueModels/' + cmdline_args.destinationModel

    nlu_model = '../models/nlu_models/default'
    training_data = '../data/stories/stories.md'


    botProcess = multiprocessing.Process(target=trainingBot, args=(to_bot_queue, to_human_queue, base_model, output_model, nlu_model, training_data))
    # Create Server
    serverProcess = multiprocessing.Process(target=server, args=(to_bot_queue, to_human_queue))


    botProcess.start()
    serverProcess.start()

    botProcess.join()
    serverProcess.join()
