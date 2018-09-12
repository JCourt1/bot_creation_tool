from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse

import sys
sys.path.append('lib/')

print("\n\n\n\n\n\n")
print("In bot.py, sys.path is:")
print(sys.path)
print("\n\n\n\n\n\n")


from lib.bot_server_channel import BotServerInputChannel
from lib.customPatientBot import CustomPatientBot
from lib.dialogue_handler import DialogueHandler

from rasa_core.agent import Agent
from rasa_core import utils




def create_argparser():
    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
        '-d', '--core',
        required=True,
        type=str,
        help="core model to run"
    )

    parser.add_argument(
        '-u', '--nlu',
        type=str,
        help="nlu model to run"
    )

    parser.add_argument(
        '-f', '--dfile',
        default="defaultDialogues.txt",
        type=str,
        help="dialogue file to use"
    )

    parser.add_argument(
        '-p', '--port',
        default=5002,
        type=int,
        help="port for the server"
    )

    parser.add_argument(
        '-o', '--log_file',
        type=str,
        default="logs/rasa_core.log",
        help="store log file in specified file"
    )

    utils.add_logging_option_arguments(parser)
    return parser


def preprocessor(message_text):
    text = message_text.strip()
    return text


if __name__ == "__main__":

    parser = create_argparser()
    cmdline_args = parser.parse_args()

    dialogue_handler = DialogueHandler(cmdline_args.dfile)
    d_types = dialogue_handler.get_types()

    dialogues = {type: dialogue_handler.get_names(type) for type in d_types}

    agent = CustomPatientBot.load('..'+cmdline_args.core, '..'+cmdline_args.nlu)
    channel = BotServerInputChannel(agent, dialogue_handler, port=cmdline_args.port)
    agent.handle_channel(channel, dialogues, message_preprocessor=preprocessor)
