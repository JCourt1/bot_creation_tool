from flask import Flask, render_template, session, flash, request, redirect, url_for, make_response, jsonify, abort

from helperFunctions.dialogueWriter import write_dialogue
from helperFunctions.setupInfo import get_dialogue_files, get_intents, get_models, is_bot_off
import os, sys
import os.path
import json
import socket, errno
import subprocess
import signal
import time
import pymongo
import datetime
import re
import bcrypt
import uuid


app = Flask(__name__)
botPid = None
trainP = None

app.config.update(
    BOTHOST="http://0.0.0.0:5002",
    WEBSITEPORT=4000,
    DEBUG = False
)

if "_bot_production_server" in os.environ:

    app.config.update(
        BOTHOST= "http://0.0.0.0:5002",
        WEBSITEPORT= 80,
        DEBUG = False
    )

client = pymongo.MongoClient("mongodb://mhtmongodb:5xXKDKil2MeMigtUrUXHaksZwQocivCftlJ7CVtH842Gv9PmuSIphMc28enPsZUIPeikcfEjvkBCdSmkP5Wj7w==@mhtmongodb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")
db = client['test-database']
collection = db['test-collection']

def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        stopBot()
        stopTraining()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

@app.route("/")
def patient():
    if not session.get("loggedIn"):
        return render_template("login.html")
    else:
        return render_template('patient.html', bothost=app.config['BOTHOST'], setup_data= { "userName": session["userName"]})


@app.route("/admin")
def admin():
    if not session.get("adminLoggedIn") or not session.get("userName"):
        return render_template("adminLogin.html")
    else:


        setup_data = { "userName": session["userName"],
                        "dialogue_files": get_dialogue_files(),
                        "intents": get_intents(),
                        "d_models": get_models()
                    }

        print(setup_data) #json.dumps()

        return render_template('clinician.html', bothost=app.config['BOTHOST'], setup_data= setup_data)

@app.route("/updateDModelsList")
def update_d_models_list():

    return jsonify(get_models())


@app.route("/login", methods=["POST"])
def login():
    response = make_response(redirect('/'))
    count = db.users.find( { "userName": request.form['username'] }).count()

    if count:
        doc = db.users.find_one({"userName":request.form['username']})
        hashed = doc['password']
        if hashed == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashed):
            session["loggedIn"] = True
            session["userName"] = str(doc["userName"])


            cid = bytes(str(uuid.uuid4()).encode('utf-8'))
            print(cid)
            # response.set_cookie('user_id', session["userName"])
            # response.set_cookie(b'conversation_id', bytes(str(cid).encode('utf-8')))
            response.set_cookie(b'conversation_id', cid)
            db.users.update_one({'userName': session["userName"]}, { '$push': { 'cids': cid } }, upsert=True)
            doc = db.users.find_one({"userName":request.form['username']})

            def myfunc(a):
                return a.decode('UTF-8')

            print(list(map(myfunc, doc['cids'])))


        else:
            flash('Either the username or password is incorrect!')

    else:
        flash('Either the username or password is incorrect!')

    return response

@app.route("/adminlogin", methods=["POST"])
def adminlogin():

    if request.form["username"] == "admin":

        doc = db.users.find_one({"userName":request.form['username']})
        hashed = doc['password']
        # For now, the pw is adminpassword
        if hashed == bcrypt.hashpw(request.form['password'].encode('utf-8'), hashed):
            session["adminLoggedIn"] = True
            session["userName"] = str(doc["userName"])
        else:
            flash('Either the username or password is incorrect!')
            # flash('Wrong password!')

    else:
        # flash('Wrong username!')
        flash('Either the username or password is incorrect!')
    return redirect(url_for('admin'))

@app.route("/logout", methods=["POST"])
def logout():

    if session.get('userName'):
        session.pop('userName')

    if session.get('loggedIn'):
        session.pop('loggedIn')
        return redirect(url_for('patient'))
    elif session.get('adminLoggedIn'):
        session.pop('adminLoggedIn')
        return redirect(url_for('admin'))

    return redirect(url_for('patient'))




@app.route("/register", methods=["POST"])
def register():
    error = None

    userName = request.form["username"]
    password = request.form["password"]
    confirmedpassword = request.form["confirmpassword"]

    # Check if username already exists
    userexists = db.users.find( { "userName": userName }).count()

    if userexists:
        print(db.users.find_one( { "userName": userName })['userName'])
        flash("That username already exists!")
        error = 1

    # Check if password is valid
    pwordmsg = None

    if password == "":
        pwordmsg = "Please enter a password!"
    elif len(password) < 6:
        pwordmsg = "Please enter a longer password! (min 6 chars)"
    elif not confirmedpassword == password:
        pwordmsg = "passwords don't match"

    if pwordmsg is not None:
        flash(pwordmsg)
        error = 1

    if not error is None:
        return redirect(url_for('patient') + "/#backtoregister")
    else:
        # users = db['users']
        db.users.insert_one({"userName": userName,
                 "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
                 "dateRegistered": datetime.datetime.utcnow(),
                 "cids": []})
        flash("success!")
        return redirect(url_for('patient') + "/#backtoregister")


@app.route("/changePassword", methods=["POST"])
def changePassword():
    oldPW = request.form["oldPW"]
    newPW1 = request.form["newPW1"]
    newPW2 = request.form["newPW2"]

    if newPW1 != newPW2:
        result = "The new password fields don't match."
    elif len(newPW1) < 6:
        result = "Passwords must be at least 6 characters long."
    else:
        # check oldPW is correct

        userName = session.get('userName')
        doc = db.users.find_one({"userName": userName})

        hashedPW = doc['password']
        # For now, the pw is adminpassword
        if hashedPW == bcrypt.hashpw(oldPW.encode('utf-8'), hashedPW):
            db.users.update({"userName": userName}, {'$set': { 'password': bcrypt.hashpw(newPW1.encode('utf-8'), bcrypt.gensalt())}})
            result = "Password successfully changed!"
        else:
            result = "The password you entered is incorrect."

    return result











@app.route("/getnames")
def get_names():
    pData = db.users.find({"admin": {"$exists": False}}, {"userName": 1, '_id': 0}) ## Should get all users by their name
    names = [doc for doc in pData]

    return jsonify(names)

@app.route("/getdetails", methods=["POST"])
def get_details():
    # try:
        userName = request.form.get("userName")

        print(request.form)
        print("userName is {}".format(userName))

        cids = db.users.find_one({"userName": userName}, {"cids": 1})

        conversations = db.conversations.find( {"$and": [ { "cid": {"$in": cids['cids']} }, {"selfHarmFlag": {"$exists": False}} ]}, {'_id': False})
        selfHarmConversations = db.conversations.find( {"$and": [ { "cid": {"$in": cids['cids']} }, {"selfHarmFlag": {"$exists": True}} ]}, {'_id': False})



        selfHarmConversations = [doc for doc in selfHarmConversations]
        conversations = [doc for doc in conversations if doc not in selfHarmConversations]

        return jsonify({"conversations": conversations, "selfHarmConversations": selfHarmConversations})


@app.route("/checkpbotoff")
def checkpbotoff():
    res = is_bot_off(botPid)
    return json.dumps(res)

@app.route("/checktbotoff")
def checktbotoff():
    res = is_bot_off(trainP)
    return json.dumps(res)


@app.route("/addDialogue", methods=["POST"])
def add_dialogue():

    # "../bots/data/dialogues"

    print(request.form )
    copiedDict = request.form.to_dict()
    print(copiedDict)

    dialogueName = copiedDict.pop("DialogueName")
    dialogueType = copiedDict.pop("DialogueType")

    basefile = copiedDict.pop("BaseFile")
    newfile = copiedDict.pop("NewFile")

    script_dir = os.path.dirname(__file__)
    print("script_dir = {}".format(script_dir))
    rel_path = "./bots/data/dialogues/"
    abs_file_path = os.path.join(script_dir, rel_path)
    print(abs_file_path)

    result = write_dialogue(copiedDict, dialogueName, dialogueType, abs_file_path + basefile, abs_file_path + newfile)
    print(result)

    return result

@app.route("/deleteDialogue", methods=["POST"])
def delete_dialogue():

    file = "./bots/data/dialogues/" + request.form['dfile']

    if os.path.isfile(file):
        os.remove(file)
        response = request.form['dfile'] + " has been deleted"
    else:
        response = request.form['dfile'] + "does not exist"

    return response


def startBot(base_model, dialogue_file):
    global botPid
    base_model = "/models/dialogueModels/" + base_model
    p = subprocess.Popen(["python", "-m", "bot", "-d", base_model, "-u", "/models/nlu_models/default", "-f", dialogue_file], cwd="./bots/bot")
    botPid = p.pid

def stopBot():
    global botPid
    if botPid is not None:
        os.kill(botPid, signal.SIGTERM)
        botPid = None

def startTraining(base_model, new_model):
    global trainP
    p = subprocess.Popen(["python", "launchTrain.py", "-b", base_model, "-d", new_model], cwd="./bots/training_bot", preexec_fn=os.setsid)
    p.daemon = True
    trainP = p

def stopTraining():
    global trainP

    if trainP is not None:
        poll = trainP.poll()

        if poll == None:
            os.killpg(os.getpgid(trainP.pid), signal.SIGKILL)

    trainP = None

@app.route("/toggle", methods=["POST"])
def toggle():
    if botPid is not None:
        stopBot()
        response = "success"
    else:
        try:
            stopTraining()

            pbot_base_model = request.form['pbot_base_model']
            dfile = request.form['dfile']
            startBot(pbot_base_model, dfile)
            response = "success"
        except:
            response = "failure"
    return response, 200

@app.route("/toggleTrain", methods=["POST"])
def toggleTrain():
    if trainP is not None:
        print()
        stopTraining()
        response = "success"
    else:
        try:
            stopBot()
            base_model = request.form['base_model']
            new_model = request.form['new_model']
            startTraining(base_model, new_model)
            response = "success"
        except:
            response = "failure"
    return response, 200








## Due to debug mode being on, the app reloads and startBot messes up,
## unless use_reloader is set to false, or startBot is placed inside the below:
# @app.before_first_request
# def setup():
#     if botPid is None:
#         startBot()


if __name__ == "__main__":

    import multiprocess
    multiprocess.set_start_method('spawn')
    app.secret_key = os.urandom(12)
    app.run(debug=app.config['DEBUG'], host= '0.0.0.0', port=app.config['WEBSITEPORT']) #, use_reloader=False
