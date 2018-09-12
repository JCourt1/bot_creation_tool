# from lib.customPatientProcessor import CustomPatientProcessor
from customPatientProcessor import CustomPatientProcessor
from rasa_core.agent import Agent

class CustomPatientBot(Agent):

    def __init__(
            self,
            domain,  # type: Union[Text, Domain]
            policies=None,  # type: Union[PolicyEnsemble, List[Policy], None]
            interpreter=None,  # type: Union[NLI, Text, None]
            tracker_store=None):

        super(CustomPatientBot, self).__init__(domain, policies, interpreter, tracker_store)


    def _create_processor(self, preprocessor=None):
        # type: (Optional[Callable[[Text], Text]]) -> MessageProcessor
        """Instantiates a processor based on the set state of the agent."""
        # Checks that the interpreter and tracker store are set and
        # creates a processor
        self._ensure_agent_is_prepared()
        return CustomPatientProcessor(
                self.interpreter, self.policy_ensemble, self.domain,
                self.tracker_store, message_preprocessor=preprocessor)

    def handle_channel(
            self,
            input_channel,  # type: InputChannel
            dialogues,
            message_preprocessor=None   # type: Optional[Callable[[Text], Text]]
    ):
        # type: (...) -> None
        """Handle messages coming from the channel."""

        processor = self._create_processor(message_preprocessor)
        processor.set_dialogues(dialogues)
        processor.handle_channel(input_channel)
