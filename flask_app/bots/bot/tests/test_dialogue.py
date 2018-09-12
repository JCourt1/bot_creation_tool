import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../data/dialogues/")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../lib")

from lib.dialogues import Dialogue, SimpleNode, ValidateInputNode, TreeNode
from lib.dialogue_handler import DialogueHandler


node1 = SimpleNode([['Hello'], ['second']])

node2 = SimpleNode( [{"sad": ["sorry about that"], "happy": ["great!", "fantastic", "wonderful", "amazing"], "default":["default1!", "default2!"] }, ["What can I do for you?", "And how can I help then?"]])


n1 = SimpleNode([['Welcome']])
n2 = SimpleNode([['my oh my', 'well I say so!'], ['haha..']])
n3 = SimpleNode([['cba!']])

nx = SimpleNode([['Welcome'], ['Bonjour']])
ny = SimpleNode([['Second'], ['OkSecond']])
nz = SimpleNode( [{"silly": ["sdfkjhgdifhg"], "unpredictable": ["HAAA!", "i", "iwxf", "HL"], "default":['another default!'] }, ["pickle", "pockle"]])

nodey = SimpleNode( [['nodeynode']])

branch1 = [n1, n2, n3]
branch2 = [nx, ny, nz]
branch3 = [nodey]

treeN = TreeNode({'dismayed':branch1, 'upbeat':branch2, 'default':branch3})



node4 = SimpleNode( [['last step']])

d1 = Dialogue([node1, node2, treeN, node4])


branchA = [n1, treeN, treeN]
branchB = [n1, treeN, n2]
branchC = [nodey]

TreeNwithNested = TreeNode({'terrific':branchA, 'hopeful':branchB, 'default':branchC})
d2 = Dialogue([node1, TreeNwithNested, treeN, node4])

fail = SimpleNode([["You need to type one of these 'bonjour', 'salut', 'hola'"]])
success = SimpleNode([["Yes!!"]])
allowedWords = ['bonjour', 'salut', 'hola']
vinputNode = ValidateInputNode(success, allowedWords)

d3 = Dialogue([vinputNode, node1])


def test_validateInputLoop():

    ns = '0'

    counter = 0

    while ns is not "finished":
        if counter > 10:
            break
        content, ns = d3.processInput(ns, message="hola", intent = 'upbeat')
        print(content)
        print("nextStep = {}".format(ns))

        counter += 1

    assert ns == "finished"

def test_little():
    content, ns = d3.processInput('0', message="hola", intent = 'upbeat')
    print(content)
    print("nextStep = {}".format(ns))


def test_loop_with_nested():

    ns = '0'

    while ns is not "finished":
        content, ns = d2.processInput(ns, message="akjhdhakjfh", intent = 'upbeat')
        print(content)
        print("nextStep = {}".format(ns))

    assert ns == "finished"


def test_specific_results():


    content, nextStep = d2.processInput('1:hopeful,0', message="akjhdhakjfh", intent = 'upbeat')
    content2, nextStep2 = d2.processInput('1', message="akjhdhakjfh", intent = 'hopeful')
    assert(content == content2)
    assert(nextStep == nextStep2)


    content, nextStep = d1.processInput('2:dismayed,2', message="akjhdhakjfh", intent = 'upbeat')
    assert(content == ['cba!'])
    # print(content)
    assert(nextStep == '3')
    # print(nextStep)


    content, nextStep = d1.processInput('2', message="akjhdhakjfh", intent = 'dismayed')
    assert(content == ['Welcome'])
    # print(content)
    assert(nextStep == '2:dismayed,1')
    # print(nextStep)


    content, nextStep = d1.processInput('2', message="akjhdhakjfh", intent = 'happy')
    assert(content == ['nodeynode'])


def test_dialogueHandler_init():

    dh = DialogueHandler("defaultDialogues.txt", prefix="/Users/joseph/Desktop/Bot_Final_Submission/flask_app/bots/data/dialogues/")


    for type in dh.get_types():

        for dialogue in dh.dialogues[type].values():
            print(dialogue.toString())





    # print(content)
    # assert(nextStep == ['3'])
    # print(nextStep)
