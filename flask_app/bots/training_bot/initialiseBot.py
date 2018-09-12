from rasa_core.policies.sklearn_policy import SklearnPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.featurizers import MaxHistoryTrackerFeaturizer, BinarySingleStateFeaturizer
from rasa_core.interpreter import NaturalLanguageInterpreter
from rasa_core import utils

# from lib.my_agent import CustomAgent
import argparse
import sys
# sys.path.append('../patientBot')
sys.path.append('../bot')
sys.path.append('../bot/lib')
from customPatientBot import CustomPatientBot


training_data_file = ''
max_history = None


def create_argparser():
    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
        '-u', '--nlu',
        type=str,
        default= "../models/nlu_models/default",
        help="nlu model to use")

    parser.add_argument(
        '-m', '--model_output',
        type=str,
        default= "../models/dialogueModels/custom",
        help="path of output dialogue model")

    parser.add_argument(
        '-td', '--training_data_file',
        type=str,
        default= "../data/stories/stories.md",
        help="data to build model with")

    utils.add_logging_option_arguments(parser)
    return parser


def preprocessor(message_text):
    text = message_text.strip()
    return text


if __name__ == "__main__":

    parser = create_argparser()
    cmdline_args = parser.parse_args()

    #  CustomPatientBot("domain.yml"

    agent = CustomPatientBot("domain.yml",
                  policies=[MemoizationPolicy(max_history=max_history), KerasPolicy(MaxHistoryTrackerFeaturizer(BinarySingleStateFeaturizer(),
                                                               max_history=max_history)), FallbackPolicy(fallback_action_name="utter_fallback", nlu_threshold=0.3)])


    training_data = agent.load_data(cmdline_args.training_data_file)
    agent.interpreter = NaturalLanguageInterpreter.create(cmdline_args.nlu)
    agent.train(
                training_data,
                augmentation_factor=50,
                epochs=250,
                batch_size=10,
                validation_split=0.2
        )

    agent.persist(cmdline_args.model_output)
