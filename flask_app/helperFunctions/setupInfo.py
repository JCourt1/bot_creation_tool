import os

def get_dialogue_files():
    res = os.listdir("./bots/data/dialogues")
    return res

def get_intents():
    intents = []

    with open("./bots/bot/domain.yml") as f:
        flag = False
        for line in f:
            line = line.lstrip()
            if line.startswith("intents:"):
                flag = True
                continue
            if flag:
                if line.startswith('-'):
                    intents.append(line.replace('-', '', 1).strip()) # extract all intents
                else:
                    flag = False
                    break

    return intents

def get_models():

    models = os.listdir("./bots/models/dialogueModels")

    return models


def is_bot_off(pid):
    if pid == None:
        return True
    else:
        False
