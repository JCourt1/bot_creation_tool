import shutil
from shutil import copyfile
import os.path

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("dialogueWriter.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def write_dialogue(formdata, dialogueName, dialogueType, basefile, newfile):

    if not os.path.isfile(basefile):
        return "File doesn't exist..."
    else:
        form_nodes = list(formdata.items())

        ## Assumptions:
        # The form fields are guaranteed to come in in the right order, which means no parsing and ordering is necessary.

        dialogue = {}

        for index, (key, value) in enumerate(form_nodes):

            layers = key.split(',')

            print(layers)

            insertIntoDict(dialogue, layers, value)

        logger.info(dialogue)

        try:
            copyfile(basefile, newfile)
        except shutil.SameFileError:
            shutil.move(basefile, newfile)

        with open(newfile, 'a') as f:

            f.write("\n")
            f.write("++ " + dialogueName + '\n')
            f.write("!!" + dialogueType + '\n')

            lines = writeOut(dialogue)
            print("lines = {}".format(lines))

            f.writelines(lines)

            f.write("== " + '\n')
            f.write("\n")

        return "Dialogue Saved!"



def check_if_vinput_node(key):
    return len(key.split('/')) > 1

def insertIntoDict(curDict, layers, value):

    curKey = layers.pop(0)

    if len(layers) == 0:

        if check_if_vinput_node(curKey):
            parts = curKey.split('/')
            if parts[1] == 'a':
                curDict[(parts[0], "vinode")] = [value]
            else:
                curDict[(parts[0], "vinode")].append(value)
        else:
            curDict[(curKey, "snode")] = value

    else:
        curKey = curKey.split(':')
        index, intent = curKey[0], curKey[1]
        curDict[(index, "tnode")] = {} if (index, "tnode") not in curDict else curDict[(index, "tnode")]
        curDict[(index, "tnode")][(intent, "branch")] = {} if (intent, "branch") not in curDict[(index, "tnode")] else curDict[(index, "tnode")][(intent, "branch")]
        insertIntoDict(curDict[(index, "tnode")][(intent, "branch")], layers, value)

def writeOut(tree, spaces = 0):

    lines = []
    ordered = list(tree.keys())

    for i in ordered:
        nodetype = i[1]

        nodeT = createNode(nodetype)


        if nodetype == "tnode" or nodetype == "branch":
            beginNested = (spaces * ' ' + nodeT + ' ')
            if nodetype == "branch":
                beginNested = beginNested + i[0] # (i[0] has the intent name)

            lines.append(beginNested + '\n')
            for line in (writeOut(tree[i], spaces + 6)):
                lines.append(line)

            lines.append(endNode(nodetype, spaces))
        elif nodetype == "vinode":
            lines.append((spaces * ' ' + nodeT) + '\n')
            lines.append((spaces + 2) * ' ' + '*<' + tree[i][0] + '\n')
            lines.append((spaces + 2) * ' ' + '*>' + tree[i][1] + '\n')

        else:
            lines.append(spaces * ' ' + nodeT + '\n')
            lines.append((spaces + 2) * ' ' + '-' + tree[i] + '\n')

    return lines

def createNode(nodetype):

    res = ':' + nodetype

    if nodetype == "branch":
        res = '$' + nodetype

    return res

    # if nodetype == "simpleNode":

def endNode(nodetype, spaces):

    if nodetype == "tnode":
        specialchar = ':'
    else:
        specialchar = '$'

    return (spaces * ' ' + specialchar + "end" + nodetype + '\n')
