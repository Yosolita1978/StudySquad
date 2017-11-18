import os
import re
import flask
import requests
from flask import render_template
from flask_sqlalchemy import SQLAlchemy


FACEBOOK_API_MESSAGE_SEND_URL = (
    'https://graph.facebook.com/v2.6/me/messages?access_token=%s')

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
PAT = os.environ.get(
    "PAT")

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
WEBHOOK_VERIFICATION_TOKEN = os.environ.get(
    "FACEBOOK_WEBHOOK_VERIFY_TOKEN")


db = SQLAlchemy(app)
SQLALCHEMY_TRACK_MODIFICATIONS=False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    facebook_id = db.Column(db.String, unique=True)

def greeting(message, user):
    """ returns greeting to user with yes or no button of is it right"""
    reply = "Meeeoooowwww! Hiiiii your name is %s is that right?"
    return reply

def name_fix(message, user):
    """fix name if broke. return okay yay all fixed. Now what to do you want to learn today?"""

def learn_tech(message, user):
    """ returns a TEXT question of what technology they want to learn"""
    reply = "Noiiiice! What do you want to learn?"
    return reply

def learn_tech_level(message, user):
    """ returns a BUTTON followup question of what level they want to learn"""
    message = {
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"button",
            "text":"What do you want to do next?",
            "buttons":[
              {
                "type":"web_url",
                "url":"https://www.messenger.com",
                "title":"Beginner"
              },
              {
                "type":"web_url",
                "url":"https://www.messenger.com",
                "title":"Intermediate"
              },
              {
                "type":"web_url",
                "url":"https://www.messenger.com",
                "title":"Baller sensei"
              },

            ]
          }
        }
      }
    reply = "are you beginner, medium or advanced?"
    return reply

def learn_when(message, user):
    """ returns a BUTTON question of when they want to learn"""
    reply = "when do you want to learn"
    return reply

def learn_where(message, user):
    """ returns request for location with button """
    reply = "where you at??"
    return reply

def handle_message(message, sender_id):
    """This function deals with all the messages from a user. It has all the logic """

    #First query for the user that is taking to the bot
    # user = User.query.filter(User.facebook_id == sender_id).first()
    user = "Dena"
    print "MESSAGE IS", message, type(message)

    # GREETING
    if message in ('hello', 'hi', 'what\'s up?', 'meow' ):
        print "USER IS", user
        message_text = greeting(message, user)

    # WHAT TO LEARN
    elif message in ('yes'):
        message_text = learn_tech(message, user)


    # WHEN TO LEARN
    elif message in ('javascript', 'js', 'python'):
        message_text = learn_tech_level(message, user)
    elif message in ('day'):
        message_text = learn_when(message, user)
    else:
        message_text = "Sorry try again I dont understand"
    # CREATE SQUAD
    print "RETURN MESSAGE IS", message_text
    return message_text

@app.route('/')
def index():
    """
    homepage central
    """
    return render_template("homepage.html")

#This comment isn't Skynet level AI either, but I like the "keep it short policy"
@app.route('/fb_webhook', methods=['GET', 'POST'])
def fb_webhook():
    """This handler deals with incoming Facebook Messages.

    In this example implementation, we handle the initial handshake mechanism,
    then just echo all incoming messages back to the sender. Not exactly Skynet
    level AI, but we had to keep it short...

    """

    # Handle initial handshake

    if flask.request.method == 'GET':
        print "REQUEST IS", flask.request.method
        if (flask.request.args.get('hub.mode') == 'subscribe' and
            flask.request.args.get('hub.verify_token') ==
            'helloworldbot'):
            challenge = flask.request.args.get('hub.challenge')
            return challenge
        else:
            print 'Received invalid GET request'
            return ''  # Still return a 200, otherwise FB gets upset.

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json
    print "PAYLOAD IS", payload

    for entry in payload['entry']:
        for event in entry['messaging']:
            if 'message' not in event:
                continue
            message = event['message']
            # Ignore messages sent by us.
            if message.get('is_echo', False):
                continue
            # Ignore messages with non-text content.
            if 'text' not in message:
                continue
            sender_id = event['sender']['id']
            message_text = message['text']

            reply = handle_message(message_text, sender_id)

            if reply:
                request_url = FACEBOOK_API_MESSAGE_SEND_URL % (
                PAT)
                requests.post(request_url,
                          headers={'Content-Type': 'application/json'},
                          json={'recipient': {'id': sender_id},
                                'message': {'text': reply}})

    return ''

if __name__ == '__main__':
    app.run(debug=True)
