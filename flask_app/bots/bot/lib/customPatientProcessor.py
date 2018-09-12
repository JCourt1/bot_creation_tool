
from rasa_core.processor import MessageProcessor
from rasa_core.channels.direct import CollectingOutputChannel
import logging
from customActions import ShowDialogues, ShowQuestionnaires ## Only works because this module is being run from bot.py, which is a directory up, where ActionShowDialogues is.


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/customPatientProcessor.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class CustomPatientProcessor(MessageProcessor):

    def __init__(self,
                 interpreter,  # type: NaturalLanguageInterpreter
                 policy_ensemble,  # type: PolicyEnsemble
                 domain,  # type: Domain
                 tracker_store,  # type: TrackerStore
                 max_number_of_predictions=10,  # type: int
                 dialogues = {},
                 message_preprocessor=None,  # type: Optional[LambdaType]
                 on_circuit_break=None  # type: Optional[LambdaType]
                 ):

        super().__init__(interpreter, policy_ensemble, domain, tracker_store, max_number_of_predictions=max_number_of_predictions, message_preprocessor=message_preprocessor, on_circuit_break=on_circuit_break)

    def set_dialogues(self, dialogues):
        self.dialogues = dialogues

    def handle_message(self, message):
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
        self._predict_and_execute_next_action(message, tracker)
        # logger.info("Got past _predict_and_execute_next_action")
        # save tracker state to continue conversation from this state
        self._save_tracker(tracker)

        if tracker.is_paused():
            logger.info("TRACKER IS PAUSED")

        logger.info(tracker.current_state())

        if isinstance(message.output_channel, CollectingOutputChannel):
            return message.output_channel.messages
        else:
            return None


    def _run_action(self, action, tracker, dispatcher, inputQueue=None, outputQueue=None):
        # events and return values are used to update
        # the tracker state after an action has been taken
        try:
            if isinstance(action, ShowDialogues):
                events = action.run(dispatcher, tracker, self.domain, d_names=self.dialogues['RDialogue'])
            elif isinstance(action, ShowQuestionnaires):
                events = action.run(dispatcher, tracker, self.domain, q_names=self.dialogues['Questionnaire'])
            else:
                events = action.run(dispatcher, tracker, self.domain)
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
