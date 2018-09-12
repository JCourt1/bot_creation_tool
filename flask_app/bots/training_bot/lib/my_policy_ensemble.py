from __future__ import print_function
from __future__ import unicode_literals

import copy
import os, sys

import numpy as np
import typing
from builtins import range
from typing import Optional, Any, List

from rasa_core import utils
from rasa_core.actions.action import ACTION_LISTEN_NAME
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import ActionExecuted, Restarted
from rasa_core.events import UserUtteranceReverted, StoryExported
from rasa_core.interpreter import RegexInterpreter
from rasa_core.policies.ensemble import PolicyEnsemble
from rasa_core.tracker_store import RedisTrackerStore

from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.online_trainer import OnlinePolicyEnsemble
from rasa_core.policies.online_trainer import TrainingFinishedException
from rasa_core import utils
import logging



logger = logging.getLogger()

#########

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/policyensemble.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


##########

if typing.TYPE_CHECKING:
    from rasa_core.domain import Domain
    from rasa_core.trackers import DialogueStateTracker
    from rasa_core.interpreter import NaturalLanguageInterpreter
    from rasa_core.channels import InputChannel

DEFAULT_FILE_EXPORT_PATH = "stories.md"

class AdaptedOnlinePolicyEnsemble(PolicyEnsemble):
    def __init__(self,
                 base_ensemble,  # type: PolicyEnsemble
                 training_trackers,  # type: List[DialogueStateTracker]
                 max_visual_history=10,  # type: int
                 use_visualization=False  # type: bool
                 ):
        super(AdaptedOnlinePolicyEnsemble, self).__init__(base_ensemble.policies)

        # logger.info("training_trackers =")
        # logger.info("**** {} ****".format(training_trackers))
        # logger.info("training_trackers are None?")
        # logger.info(training_trackers == None)

        self.base_ensemble = base_ensemble
        self.training_trackers = training_trackers
        self.max_visual_history = max_visual_history
        self.use_visualization = use_visualization

        self.current_id = 0
        self.extra_intent_examples = []
        self.stories = []

        self.batch_size = 5
        self.epochs = 50




    def run_online_training(self,
                            domain,  # type: Domain
                            interpreter,  # type: NaturalLanguageInterpreter
                            input_channel=None  # type: Optional[InputChannel]
                            ):
        # type: (...) -> None
        # from rasa_core.agent import Agent
        from lib.my_agent import CustomAgent
        if interpreter is None:
            interpreter = RegexInterpreter()

        # domain = Agent._create_domain("domain.yml")
        # tracker_store = RedisTrackerStore(domain, host="redis")
        #host="redis:alpine://redis", port="6379"

        # tracker_store = RedisTrackerStore(domain)
        tracker_store = None
        # tracker = tracker_store.get_or_create_tracker("cliniciansID")

        bot = CustomAgent(domain, self,
                    interpreter=interpreter, tracker_store = tracker_store)
        bot.toggle_memoization(False)

        try:
            bot.handle_channel(
                    input_channel if input_channel else ConsoleInputChannel())
        except TrainingFinishedException:
            pass  # training has finished

    def request_input(self, valid_values=None, prompt=None, max_suggested=6, inputQueue=None, outputQueue=None):

        if inputQueue == None or outputQueue == None:
            raise Exception("Missing either input or output queue!")

        def wrong_input_message():
            msg = "Invalid answer, only {}{} allowed\n".format(
                    ", ".join(valid_values[:max_suggested]),
                    ",..." if len(valid_values) > max_suggested else "")
            # self.input_channel.message_store.log("cliniciansID", "bot", {"type": "text", "text": msg})
            return msg

        msg = None

        while True:
            try:
                # input_value = input(prompt) if prompt else input()
                if prompt:
                    response = msg + prompt if msg is not None else prompt
                    outputQueue.put(["thintKeyOptions", response])
                    # logger.info(prompt)
                    logger.info("logging stuff from inner process")
                    input_value = str(inputQueue.get())
                else:
                    # logger.info("logging stuff from inner process")
                    input_value = str(inputQueue.get())

                if valid_values is not None and input_value not in valid_values:
                    # outputQueue.put(input_value)
                    # outputQueue.put(str(type(input_value)))
                    msg = wrong_input_message()
                    # logger.info(msg)
                    continue
            except ValueError:
                msg = wrong_input_message()
                # logger.info(msg)
                continue
            return input_value

    def predict_next_action(self, tracker, domain, inputQueue=None, outputQueue=None):
        # type: (DialogueStateTracker, Domain) -> int
        """Predicts the next action the bot should take after seeing x.

        This should be overwritten by more advanced policies to use ML to
        predict the action. Returns the index of the next action"""
        probabilities = self.probabilities_using_best_policy(tracker, domain, inputQueue, outputQueue)
        max_index = int(np.argmax(probabilities))
        # logger.debug("Predicted next action '{}' with prob {:.2f}.".format(
        #         domain.action_for_index(max_index).name(),
        #         probabilities[max_index]))
        return max_index

    def probabilities_using_best_policy(self, tracker, domain, inputQueue, outputQueue):
            # type: (DialogueStateTracker, Domain) -> List[float]
            # given a state, predict next action via asking a human

            recipient_id = "cliniciansID"

            probabilities = self.base_ensemble.probabilities_using_best_policy(
                    tracker, domain)
            logger.info("second!")
            pred_out = int(np.argmax(probabilities))
            # logger.info("third!")
            latest_action_was_listen = self._print_history(tracker, inputQueue=inputQueue, outputQueue=outputQueue)
            # logger.info("fourth!")
            # sys.stdout.flush()
            logger.info("\n\nAll messages (at the top): \n\n")
            logger.info(tracker.export_stories())

            action_name = domain.action_for_index(pred_out).name()
            if latest_action_was_listen:
                msg = ""
                msg = "The bot wants to [{}] due to the intent. \n ⬇ Is this correct? ⬇\n".format(action_name)
                outputQueue.put(["thintBotAction", msg])
                # logger.info(msg)
                sys.stdout.flush()


                user_input = self.request_input(
                        ["1", "2", "3", "0"],
                        "\t1.\tYes\n" +
                        "\t2.\tNo, intent is right but the action is wrong\n" +
                        "\t3.\tThe intent is wrong\n" +
                        "\t0.\tExport current conversations as stories and quit\n", inputQueue=inputQueue, outputQueue=outputQueue)
            else:
                msg = "The bot wants to [{}].\n ⬇ Is this correct? ⬇\n".format(action_name)
                # logger.info(msg)
                outputQueue.put(["thintBotAction", msg])
                # logger.info(msg)
                sys.stdout.flush()


                user_input = self.request_input(
                        ["1", "2", "0"],
                        "\t1.\tYes.\n" +
                        "\t2.\tNo, the action is wrong.\n" +
                        "\t0.\tExport current conversations as stories and quit\n", inputQueue=inputQueue, outputQueue=outputQueue)

            if user_input == "1":
                # max prob prediction was correct
                if action_name == ACTION_LISTEN_NAME:

                    msg = "⬆ Type in your next message above ⬆"
                    outputQueue.put(["thintBotAction", msg])
                    outputQueue.put(["thintKeyOptions", "\n"]) ## Hack to clear it

                    # logger.info(msg)
                    sys.stdout.flush()

                return probabilities

            elif user_input == "2":
                # max prob prediction was false, new action required
                # action wrong
                y = self._request_action(probabilities, domain, tracker, inputQueue=inputQueue, outputQueue=outputQueue)

                # update tracker with new action
                new_action_name = domain.action_for_index(y).name()

                # need to copy tracker, because the tracker will be
                # updated with the new event somewhere else
                training_tracker = tracker.copy()
                training_tracker.update(ActionExecuted(new_action_name))

                self._fit_example(training_tracker, domain)

                self.write_out_story(tracker)

                return utils.one_hot(y, domain.num_actions)

            elif user_input == "3":
                # intent wrong and maybe action wrong
                logger.info("\n\nJust entered option 3 \n\n")
                intent = self._request_intent(tracker, domain, inputQueue=inputQueue, outputQueue=outputQueue)
                latest_message = copy.copy(tracker.latest_message)
                latest_message.intent = intent

                tracker.update(UserUtteranceReverted())
                tracker.update(latest_message)
                logger.info("\n\nAll messages (now in 3): \n\n")
                logger.info(tracker.export_stories())

                for e in domain.slots_for_entities(latest_message.entities):
                    tracker.update(e)
                return self.probabilities_using_best_policy(tracker, domain, inputQueue, outputQueue)

            elif user_input == "0":

                # file_prompt = ("File to export to (if file exists, this "
                #                "will append the stories) "
                #                "[{}]: ").format(DEFAULT_FILE_EXPORT_PATH)
                # export_file_path = self.request_input(prompt=file_prompt, inputQueue=inputQueue, outputQueue=outputQueue)

                # if not export_file_path:
                #     export_file_path = DEFAULT_FILE_EXPORT_PATH

                export_file_path = '../data/stories/stories.md'

                self._export_stories(tracker, export_file_path)
                outputQueue.put("SHUTDOWN")
                raise TrainingFinishedException()

            else:
                # logger.info("Righty!")
                raise Exception(
                        "Incorrect user input received '{}'".format(user_input))

    @staticmethod
    def _export_stories(tracker, export_file_path):
        # export current stories and quit


        exported = StoryExported(export_file_path)
        tracker.update(exported)
        logger.info("Stories got exported to '{}'.".format(
                os.path.abspath(exported.path)))

    def continue_training(self, trackers, domain, **kwargs):
        # type: (List[DialogueStateTracker], Domain, **Any) -> None
        for p in self.policies:

            if isinstance(p, KerasPolicy):
                p.model.compile(loss='categorical_crossentropy',
                              optimizer='rmsprop',
                              metrics=['accuracy'])

            p.continue_training(trackers, domain, **kwargs)

    def _fit_example(self, tracker, domain):
        # takes the new example labelled and learns it
        # via taking `epochs` samples of n_batch-1 parts of the training data,
        # inserting our new example and learning them. this means that we can
        # ask the network to fit the example without overemphasising
        # its importance (and therefore throwing off the biases)

        self.training_trackers.append(tracker)
        self.continue_training(self.training_trackers, domain,
                               batch_size=self.batch_size,
                               epochs=self.epochs)

    def write_out_story(self, tracker):
        # takes our new example and writes it in markup story format
        self.stories.append(tracker.export_stories())

    def _request_intent(self, tracker, domain, inputQueue=None, outputQueue=None):
        # take in some argument and ask which intent it should have been
        # save the intent to a json like file

        if inputQueue == None or outputQueue == None:
            raise Exception("Missing either input or output queue!")


        outputString = "------\n"
        outputString += "Message: "
        outputString += tracker.latest_message.text + "\n" + "What intent is this? ➔"
        outputQueue.put(["thintBotAction", outputString])
        outputString = "| Number | Intent | \n | --- | --- |\n"
        for idx, intent in enumerate(domain.intents):
            outputString += '|{}|{}|\n'.format(idx, intent)

        outputQueue.put(["thintActionList", outputString])
        out = int(self.request_input(
                utils.str_range_list(0, len(domain.intents)), inputQueue=inputQueue, outputQueue=outputQueue))
        json_example = {
            'text': tracker.latest_message.text,
            'intent': domain.intents[out]
        }
        self.extra_intent_examples.append(json_example)
        intent_name = domain.intents[out]
        return {'name': intent_name, 'confidence': 1.0}

    def _print_history(self, tracker, inputQueue=None, outputQueue=None):
        # prints the historical interactions between the bot and the user,
        # to help with correctly identifying the action
        if inputQueue == None or outputQueue == None:
            raise Exception("Missing either input or output queue!")

        latest_listen_flag = False
        tr_json = []
        for tr in tracker.generate_all_prior_trackers():
            tr_json.append({
                'action': tr.latest_action_name,
                'intent': tr.latest_message.intent[
                    'name'] if tr.latest_message.intent else "",
                'entities': tr.latest_message.entities
            })

        answer = "| | |  \n | --- | --- |\n"
        tr_json = tr_json[-self.max_visual_history:]
        logger.info(tr_json)
        n_history = len(tr_json)
        for idx, hist_tracker in enumerate(tr_json):

            # answer += "\tbot did:\t{}\n".format(hist_tracker['action'])
            # if hist_tracker['action'] == 'action_listen':
            #     if idx < n_history - 1:
            #         answer += "\tuser did:\t{}\n".format(hist_tracker['intent'])
            #         for entity in hist_tracker['entities']:
            #             answer += "\twith {}:\t{}\n".format(entity['entity'],
            #                                             entity['value'])
            #     if idx == n_history - 1:
            #         answer += "\tuser said:\t{}\n".format(tracker.latest_message.text)
            #         answer += "\t\t whose intent is:\t{}\n".format(
            #                 hist_tracker['intent'])
            #         for entity in hist_tracker['entities']:
            #             answer += "\twith {}:\t{}\n\n".format(entity['entity'],
            #                                             entity['value'])
            #         latest_listen_flag = True

            answer += "| Bot: | {} |\n".format(hist_tracker['action'])
            if hist_tracker['action'] == 'action_listen':
                if idx < n_history - 1:
                    answer += "| User: |{} |\n".format(hist_tracker['intent'])
                    for entity in hist_tracker['entities']:
                        answer += "| with {}: | {} |\n".format(entity['entity'],
                                                        entity['value'])
                if idx == n_history - 1:
                    answer += "| | |\n"*2 + " | User's latest message: | {} |\n".format(tracker.latest_message.text)
                    answer += "| | |\n"*2 + "| Predicted intent: | {} |\n ".format(
                            hist_tracker['intent'])
                    for entity in hist_tracker['entities']:
                        answer += "| with {}: | {} |\n".format(entity['entity'],
                                                        entity['value'])
                    latest_listen_flag = True

        slot_strs = []
        for k, s in tracker.slots.items():
            slot_strs.append("{}: [{}]".format(k, str(s.value)))

        # answer = answer + "\n\n\n" + "| Current slots: | {} |\n".format(", ".join(slot_strs))

        outputQueue.put(["thintHistory", answer])



        return latest_listen_flag

    def _request_action(self, predictions, domain, tracker, inputQueue=None, outputQueue=None):
        # given the intent and the text (NOT IMPLEMENTED)
        # what is the correct action?
        if inputQueue == None or outputQueue == None:
            raise Exception("Missing either input or output queue!")

        self._print_history(tracker, inputQueue=inputQueue, outputQueue=outputQueue)
        outputQueue.put(["thintBotAction", "what is the next action for the bot? ➔\n"])

        outputstring = "| No. | Action name | Probability | \n | --- | --- | --- |\n"

        for idx in range(domain.num_actions):
            action_name = domain.action_for_index(idx).name()
            outputstring += "|{:>10}|{:>40}   | {:03.2f}|\n".format(idx, action_name,
                                                    predictions[idx])

        outputQueue.put(["thintActionList", outputstring])
        out = int(self.request_input(
                utils.str_range_list(0, domain.num_actions), inputQueue=inputQueue, outputQueue=outputQueue))
        outputQueue.put(["thintBotAction", "thanks! The bot will now "
              "[{}]\n -----------".format(domain.action_for_index(out).name())])

        if out == 0: # If the action is "listen", we need to clear up the interface
            outputQueue.put(["thintKeyOptions", "\n"])
            outputQueue.put(["thintActionList", "\n"])



        return out
