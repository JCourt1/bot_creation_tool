
from dialogues import Dialogue, SimpleNode, ValidateInputNode, TreeNode
import logging
import re
import sys
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/dialogue_handler.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class DialogueHandler():

    def __init__(self, filename, prefix="../data/dialogues/"):

        path = prefix + filename
        self.dialogues = {}
        self.dialogues = DialogueCreator().createDialogues(path)

    def handle_dialogue(self, dialogueName, currentPointInDialogue, output_channel, recipient_id, message, intent):

        flag, type = self.check_dialogue_exists(dialogueName)

        if flag:
            output, newPointInDialogue = self.dialogues[type][dialogueName].processInput(currentPointInDialogue, message=message, intent=intent)

            if isinstance(output, list):
                for singleMessage in output:

                    output_channel.send_text_message(recipient_id, singleMessage)
            else:
                raise Exception('output should be a list')
            return newPointInDialogue

        else:
            raise Exception("Dialogue with the name: {} does not exist".format(dialogueName))

    def get_types(self):
        return self.dialogues.keys()

    def get_names(self, type):
        return self.dialogues[type].keys()

    def check_dialogue_exists(self, dialogueName):

        for key in self.get_types():
            if dialogueName in self.dialogues[key]:
                return True, key

        return False, None

class DialogueCreator():

    dialogues = defaultdict(dict)

    dName = ''
    nodes = []
    latestSnode = None
    latestVInode = None
    tNodeStack = []
    branchesStack = []

    def configureVInode(self, viNode, line):
        line = line.replace('*', '', 1)
        if line.startswith('<'):
            line = line.replace('<', '', 1).lstrip()
            words = line.split('/')
            viNode.acceptedWords = [el.lower() for el in words]
        elif line.startswith('>'):
            line = line.replace('>', '', 1)
            sentences = line.split('/')
            if viNode.success is None:
                viNode.success = SimpleNode([sentences])
            else:
                viNode.success.content.append(sentences)

    def listHandler(self, line):

        line = line.replace('-', '', 1)
        sentences = line.split('/')
        self.latestSnode.content.append(sentences)

    def nodeHandler(self, line):

        code = line.split()[0]
        new_node = self.nodeFactory(code)

        if code == ":endtnode":
            self.tNodeStack.pop()
        else:
            tNode = self.peek(self.tNodeStack)
            print(self.tNodeStack)
            print("tNode is {}".format(tNode))
            print("new_node is {}".format(new_node))

            if tNode is None:
                self.nodes.append(new_node)
            else:
                logger.info("self.branchesStack = {}".format(self.branchesStack))
                tNode.branches[self.peek(self.branchesStack)].append(new_node)

            if isinstance(new_node, TreeNode):
                self.tNodeStack.append(new_node)

            elif isinstance(new_node, SimpleNode):
                self.latestSnode = new_node
            elif isinstance(new_node, ValidateInputNode):
                self.latestVInode = new_node


    def branchHandler(self, line):

        code = line.split()[0]
        if code == "$branch":
            branch_name = line.split()[-1]
            logger.info("branch_name = {}".format(branch_name))
            self.branchesStack.append(branch_name)
            self.peek(self.tNodeStack).branches[branch_name] = []
        elif code == "$endbranch":
            self.branchesStack.pop()

    def peek(self, stack):
        if stack == []:
            return None
        else:
            return stack[-1]

    def nodeFactory(self, code):
        lookupObject = {
            ':snode': SimpleNode,
            ':vinode': ValidateInputNode,
            ':tnode': TreeNode
        }

        if code not in lookupObject.keys():
            return None

        return lookupObject[code]()

    def createDialogues(self, file):
        with open(file) as f:

            for line in f:
                line = line.strip()
                if line.startswith('++'):
                    self.dName = line.replace('++', '', 1).lstrip().strip('\n')
                elif line.startswith('!!'):
                    self.dType = line.replace('!!', '', 1).lstrip().strip('\n')
                elif line.startswith(':'):
                    self.nodeHandler(line)
                elif line.startswith('$'):
                    self.branchHandler(line)
                elif line.startswith('-'):
                    self.listHandler(line)
                elif line.startswith('*'):
                    print(self.latestVInode)
                    self.configureVInode(self.latestVInode, line)
                elif line.startswith('=='):
                # end of this dialogue
                    self.dialogues[self.dType][self.dName] = Dialogue(self.nodes)
                    logger.info(self.dName)
                    self.nodes = []

        return self.dialogues
