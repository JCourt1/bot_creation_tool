import random
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/dialogues.log")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class Dialogue():

    def __init__(self, nodes):
        self.nodes = nodes

    def toString(self):

        res = ''
        numtabs = 0

        def recursiveString(res, numtabs, nodes):

            for node in nodes:

                res += (numtabs*'\t') + node.name + "\n"

                if isinstance(node, TreeNode):

                    for branch, content in node.branches.items():
                        numtabs += 1
                        res += (numtabs*'\t') + 'branch: ' + branch + "\n"

                        numtabs += 1
                        res = recursiveString(res, numtabs, content)
                        numtabs -= 1

                        numtabs -= 1
            return res

        res = recursiveString(res, numtabs, self.nodes)
        return res

    def processInput(self, currentPointInDialogue, message, intent):

        node, nextStep = self.getNode(currentPointInDialogue, message, intent) 

        if isinstance(node, ValidateInputNode) or isinstance(node, TreeNode):
            raise Exception("Should only ever produce a SimpleNode here")

        content = self.getContent(node, intent)

        return content, str(nextStep)

    def dialogue_finished(self, index):
        return (index + 1) >= len(self.sentences)


    def getNode(self, currentPointInDialogue, message, intent):

        parts = currentPointInDialogue.split(',')
        index_and_branchKey = parts.pop(0).split(':')
        remainingIndex = parts
        index = int(index_and_branchKey[0])
        branchKey = None if len(index_and_branchKey) <= 1 else index_and_branchKey[1]

        logger.info("index = {}".format(index))
        logger.info("self.nodes = {}".format(self.nodes))
        logger.info(self.toString())


        if isinstance(self.nodes[index], SimpleNode):
            node = self.nodes[index]
            nextStep = index + 1
            if nextStep == len(self.nodes):
                nextStep = "finished"

        elif isinstance(self.nodes[index], ValidateInputNode):
            node, nextStep = self.nodes[index].validate(message, str(index))
            if nextStep == len(self.nodes):
                nextStep = "finished"

        elif isinstance(self.nodes[index], TreeNode):

            node, nextStep = self.nodes[index].getSubNode(branchKey, message, remainingIndex, intent)

            if nextStep == 'done':
                nextStep = index + 1
                if nextStep == len(self.nodes):
                    nextStep = "finished"
            else:
                nextStep = str(index) + ':' + nextStep

        return node, str(nextStep)


    def getContent(self, node, intent):

        result = []

        for el in node.content:
            if isinstance(el, dict):
                answers = el.get(intent)
                answers = el.get('default') if answers is None else answers
            elif isinstance(el, list):
                answers = el
            else:
                raise Exception("node.content should contain only lists or dictionaries, but {} is type {}".format(el, type(el)))

            result.append(random.choice(answers))

        return result




class SimpleNode():

    def __init__(self, content=None):

        # Content looks like this - can have dicts or lists as its elements or both, and either 1 or many elements:
        # self.content = [  {"sad": ["sorry about that"], "happy"= ["great!"] }, ["What can I do for you?", "And how can I help then?"]  ]
        self.name = "Simple Node"

        if content:
            for el in content:
                if not (isinstance(el, list) or isinstance(el, dict)):
                    raise Exception("Tried to build a SimpleNode with something that is not either a list or a dictionary, which is forbidden")
            self.content = content
        else:
            self.content = []


class ValidateInputNode(): ## Use case -> simply getting the patient to type some information we want to know. Prevents moving on if they don't.

    def __init__(self, success=None, acceptedWords=None):
        self.name = "Validate Input Node"

        self.success = success # A simple Node

        if acceptedWords == None:
            self.acceptedWords = None
        else:
            self.acceptedWords = [el.lower() for el in acceptedWords]

    def validate(self, message, currentIndex):
        if message.lower() in self.acceptedWords:
            return self.success, int(currentIndex) + 1
        else:
            return SimpleNode([["I'm sorry, could you rephrase that", "You need to type one of these: {}".format(','.join(self.acceptedWords))]]), currentIndex # don't increment

class TreeNode():

    def __init__(self, branches=None):
        self.name = "Tree Node"
        self.branches = branches if branches is not None else {}

    def get_branch_for_intent(self, branchKey):
        branch = self.branches.get(branchKey)
        if branch is None:
            branchKey = 'default'
            branch = self.branches.get(branchKey)
            if branch is None:
                raise Exception("tried {} and then 'default' as keys, and neither worked (it is necessary to define a 'default' key)".format(branchKey))

        return branch, branchKey

    def getSubNode(self, branchKey, message, remainingIndex, intent):

        if branchKey is not None:
            branch, branchKey = self.get_branch_for_intent(branchKey)
            sub_node_index = remainingIndex.pop(0)

        else:
            branch, branchKey = self.get_branch_for_intent(intent)
            sub_node_index = '0'

        if len(remainingIndex) == 0:
            node = branch[int(sub_node_index)]

            if isinstance(node, TreeNode):
                node, subBranchNextStep = node.getSubNode(None, message, remainingIndex, intent)

                if isinstance(node, TreeNode):
                    raise Exception("TreeNode is the first node in another TreeNode (forbidden)")

                if subBranchNextStep == "done":
                    nextStep = int(sub_node_index) + 1
                    if nextStep == len(branch):
                        nextStep = "done"
                    else:
                        nextStep = branchKey + ',' + str(nextStep)
                else:
                     nextStep = str(branchKey) + ',' + str(sub_node_index) + ':' + subBranchNextStep
            elif isinstance(node, ValidateInputNode):
                node, newIndex = node.validate(message, int(sub_node_index))

                if newIndex == len(branch):
                    nextStep = "done"
                else:
                    nextStep = str(branchKey) + ',' + str(newIndex)
            else:
                node = node
                incremented = int(sub_node_index) + 1
                if incremented == len(branch):
                    nextStep = "done"
                else:
                    nextStep = str(branchKey) + ',' + str(incremented)
        else:
            indices = sub_node_index.split(':')

            subNode_i = indices[0]
            subBranch_key = indices[1]

            if isinstance(branch[int(subNode_i)], SimpleNode):
                raise Exception("branch is not None (it is {}), yet the node at index {} is not a TreeNode node".format(subBranch_key, subNode_i))

            subTreeNode = branch[int(subNode_i)]
            node, subBranchNextStep = subTreeNode.getSubNode(subBranch_key, message, remainingIndex, intent)

            if subBranchNextStep == "done":
                nextStep = int(subNode_i) + 1
                if nextStep == len(branch):
                    nextStep = "done"
                else:
                    nextStep = branchKey + ',' + str(nextStep)
            else:
                 nextStep = branchKey + ',' + subNode_i + ":" + subBranchNextStep
        return node, str(nextStep)
