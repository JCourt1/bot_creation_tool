# FLASK_APP=fbConnect.py FLASK_ENV=development flask run
#
# Expose a https Endpoint and Connect a Facebook Page
# The url localhost:5000 only works for requests created on the same computer as the running server. So you need to let facebook know how to reach your flask server. To do this, first install ngrok.
#
# Go to this page and install the version for your operating system. If you're on Mac and have homebrew, the quickest way to install ngrok is with brew cask install ngrok.
#
# Start the ngrok server in your terminal with ngrok http 5000. This will set up a https endpoint to get forwarded to your machine on port 5000, for example https://51b6b3fa.ngrok.io.
#
# Note that if you quit ngrok and restart, this URL will change.
#
# Create a Facebook App and Page
# The next step is to create an app and a page on Facebook. There is good documentation available from Facebook but you'll walk through the main steps here.
#
# To create the app go here and
#
# click on My Apps -> Add a New App and enter a name
# you will be redirected to the dashboard for the app
# under Products, find Add a Product and click on Messenger -> Set Up
# To create the page, you have to:
#
# go the settings for Messenger, scroll down to Token Generation and click on the link to create a new page for your app
# Once you have created a page, go back to the Token Generation settings and select this page from the drop-down menu. Copy the Page Access Token into the placeholder for PAGE_ACCESS_TOKEN in server.py above.
#
# Start your bot server
# Now that you have everything set up, it's time to start your chatbot server! In a separate terminal tab, run
#
# FLASK_APP=server.py flask run
# Set up the webhook
# Finally, you need to register your webhook on the Facebook developers page.
#
# Go to the Messenger tab in Products again and scroll down to Webhooks, click on Setup Webhooks
# Under the Callback URL enter in your ngrok URL, for example, https://51b6b3fa.ngrok.io/webhook. It is important that your flask app is running at this point, because the verify_token() will be called on the next step
# In the Verify Token field, you put the value you specified in your server.py file
# In Subscription Fields make sure messages and messaging_postbacks are ticked Click Verify and Save to perform the authentication
# Important: Go back to Products -> Messenger, and under Select a page to subscribe your webhook to the page events select your page and click Subscribe.
#
# You're done!
# Your bot is now ready to send and receive messages via Facebook Messenger. Right now, your get_bot_response() function is still pretty simple, and doesn't feel like a real chatbot yet! To learn all about building chatbots, check out the Building Chatbots in Python DataCamp course, as well as the Rasa NLU and Rasa Core python libraries.
#




# 
# To change the ngrok endpoint, go to facebook for developers, then under products, go to webhooks, then edit subscription,
# then type in the new endpoint and the verify token found below



from flask import Flask, request

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'HbATlU+IbDZAXw58yplO1/nqWnzEkoxxAo3GLUSDOsU='# <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EAAD6ogUPhZCcBAJ7pZCCCXggQw1fyoMfQoj6MQC852Vf5rJUJGutoDponYl2uEfZBZCVylRrnc9iXZCIVGVyxvHMZC33nLaHSmGE5Y1tAonwg4TTxLROJUmU3IicG616wFkRPeuY9dCWEAeUM6ZBZAMghN3WdaFPjhMZBdJpGndEHyQZDZD'# paste your page access token here>"


def get_bot_response(message):
    """This is just a dummy function, returning a variation of what
    the user said. Replace this function with one connected to chatbot."""
    return "This is a dummy response to '{}'".format(message)


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    response = get_bot_response(message)
    send_message(sender, response)


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


@app.route("/webhook", methods=['POST', 'GET'])
def listen():
    """This is the main function flask uses to
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"










import requests

def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()
