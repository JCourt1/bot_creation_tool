import sys
from rasa_core.processor import MessageProcessor
from rasa_core.actions.action import ActionRestart, ACTION_LISTEN_NAME
from rasa_core.channels.direct import CollectingOutputChannel
from rasa_core.events import UserUttered, Restarted
from rasa_core.dispatcher import Dispatcher
import logging
from rasa_core.interpreter import (
    NaturalLanguageInterpreter,
    INTENT_MESSAGE_PREFIX)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/processor.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class CustomProcessor(MessageProcessor):

    def __init__(self,
                 interpreter,  # type: NaturalLanguageInterpreter
                 policy_ensemble,  # type: PolicyEnsemble
                 domain,  # type: Domain
                 tracker_store,  # type: TrackerStore
                 max_number_of_predictions=10,  # type: int
                 message_preprocessor=None,  # type: Optional[LambdaType]
                 on_circuit_break=None  # type: Optional[LambdaType]
                 ):

        super().__init__(interpreter, policy_ensemble, domain, tracker_store, max_number_of_predictions=max_number_of_predictions, message_preprocessor=message_preprocessor, on_circuit_break=on_circuit_break)


    def handle_channel(self, input_channel=None):
        # type: (InputChannel) -> None
        """Handles the input channel synchronously.

        Each message gets processed directly after it got received."""
        input_channel.start_sync_listening(self.handle_message, self.tracker_store)

    def handle_message(self, message, inputQueue=None, outputQueue=None):
        # type: (UserMessage) -> Optional[List[Text]]
        """Handle a single message with this processor."""

        # preprocess message if necessary
        if self.message_preprocessor is not None:
            logger.info("message preprocessor is not none")
            message.text = self.message_preprocessor(message.text)
        # we have a Tracker instance for each user
        # which maintains conversation state
        tracker = self._get_tracker(message.sender_id)


        # Restarted().apply_to(tracker)


        # logger.info("got past get tracker")
        self._handle_message_with_tracker(message, tracker)
        # logger.info("got past _handle_message_with_tracker")
        self._predict_and_execute_next_action(message, tracker, inputQueue, outputQueue)
        # logger.info("Got past _predict_and_execute_next_action")
        # save tracker state to continue conversation from this state
        self._save_tracker(tracker)

        if isinstance(message.output_channel, CollectingOutputChannel):
            return message.output_channel.messages
        else:
            return None

    def _predict_and_execute_next_action(self, message, tracker, inputQueue=None, outputQueue=None):
        # this will actually send the response to the user

        dispatcher = Dispatcher(message.sender_id,
                                message.output_channel,
                                self.domain)
        # keep taking actions decided by the policy until it chooses to 'listen'
        should_predict_another_action = True
        num_predicted_actions = 0

        self._log_slots(tracker)

        # action loop. predicts actions until we hit action listen
        while (should_predict_another_action
               and self._should_handle_message(tracker)
               and num_predicted_actions < self.max_number_of_predictions):
            # this actually just calls the policy's method by the same name
            action = self._get_next_action(tracker, inputQueue, outputQueue)

            should_predict_another_action = self._run_action(action,
                                                             tracker,
                                                             dispatcher, inputQueue=inputQueue, outputQueue=outputQueue)
            num_predicted_actions += 1


        if (num_predicted_actions == self.max_number_of_predictions and
                should_predict_another_action):
            # circuit breaker was tripped
            logger.warn(
                    "Circuit breaker tripped. Stopped predicting "
                    "more actions for sender '{}'".format(tracker.sender_id))
            if self.on_circuit_break:
                # call a registered callback
                self.on_circuit_break(tracker, dispatcher)




    def _handle_message_with_tracker(self, message, tracker):
        # type: (UserMessage, DialogueStateTracker) -> None
        parse_data = self._parse_message(message)

        # don't ever directly mutate the tracker
        # - instead pass its events to log
        tracker.update(UserUttered(message.text, parse_data["intent"],
                                   parse_data["entities"], parse_data))
        # store all entities as slots
        for e in self.domain.slots_for_entities(parse_data["entities"]):
            tracker.update(e)

        logger.debug("Logged UserUtterance - "
                     "tracker now has {} events".format(len(tracker.events)))

    def _parse_message(self, message):
        # for testing - you can short-cut the NLU part with a message
        # in the format _intent[entity1=val1,entity=val2]
        # parse_data is a dict of intent & entities
        if (message.text.startswith(INTENT_MESSAGE_PREFIX) or
                message.text.startswith("_")):
            if RegexInterpreter.is_using_deprecated_format(message.text):
                warnings.warn(
                        "Parsing messages with leading `_` is deprecated and "
                        "will be removed. Instead, prepend your intents with "
                        "`{0}`, e.g. `{0}mood_greet` "
                        "or `{0}restart`.".format(INTENT_MESSAGE_PREFIX))
            parse_data = RegexInterpreter().parse(message.text)
        else:
            try:
                parse_data = self.interpreter.parse(message.text)
            except:
                logger.warning("Error that wasn't expected: %s" % sys.exc_info())

        logger.debug("Received user message '{}' with intent '{}' "
                     "and entities '{}'".format(message.text,
                                                parse_data["intent"],
                                                parse_data["entities"]))
        return parse_data

    def _run_action(self, action, tracker, dispatcher, inputQueue=None, outputQueue=None):
        # events and return values are used to update
        # the tracker state after an action has been taken
        try:
            events = action.run(dispatcher, tracker, self.domain) ### look into overriding the dispatcher. (utter message - perhaps pass through the queue, or get the dispatcher to play nice)
        except Exception as e:
            logger.error("Encountered an exception while running action '{}'. "
                         "Bot will continue, but the actions events are lost. "
                         "Make sure to fix the exception in your custom "
                         "code.".format(action.name()), )
            logger.error(e, exc_info=True)
            events = []
        self.log_bot_utterances_on_tracker(tracker, dispatcher)
        self._log_action_on_tracker(tracker, action.name(), events)
        self._schedule_reminders(events, dispatcher)

        return self.should_predict_another_action(action.name(), events)


    def _get_next_action(self, tracker, inputQueue=None, outputQueue=None):
        # type: (DialogueStateTracker) -> Action

        follow_up_action = tracker.follow_up_action
        if follow_up_action:
            tracker.clear_follow_up_action()
            if self.domain.index_for_action(
                    follow_up_action.name()) is not None:
                return follow_up_action
            else:
                logger.error(
                        "Trying to run unknown follow up action '{}'!"
                        "Instead of running that, we will ignore the action "
                        "and predict the next action.".format(follow_up_action))

        if (tracker.latest_message.intent.get("name") ==
                self.domain.restart_intent):
            return ActionRestart()

        idx = self.policy_ensemble.predict_next_action(tracker, self.domain, inputQueue, outputQueue)
        logger.info("inside get next action")
        logger.info(idx)
        logger.info(self.domain.action_for_index(idx))

        return self.domain.action_for_index(idx)
