"""
Flask Documentation:     http://flask.pocoo.org/docs/
Flask-SQLAlchemy Documentation: http://flask-sqlalchemy.pocoo.org/
SQLAlchemy Documentation: http://docs.sqlalchemy.org/
FB Messenger Platform docs: https://developers.facebook.com/docs/messenger-platform.

This file creates your application.
"""

import os
import re
import flask
import requests
from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_TRACK_MODIFICATIONS=False
FACEBOOK_API_MESSAGE_SEND_URL = (
    'https://graph.facebook.com/v2.6/me/messages?access_token=%s')

ADDRESS_REQUEST_REGEX = re.compile(r'address of (\w+)\?*', re.IGNORECASE)
ADD_TASK_REGEX = re.compile(r'ADD\s(.+)', re.IGNORECASE)
DONE_TASK_REGEX = re.compile(r'DONE\s(.+)', re.IGNORECASE)
LIST_DONE_REGEX = re.compile(r'(list done)', re.IGNORECASE)

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
PAT = os.environ.get(
    "PAT")

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
WEBHOOK_VERIFICATION_TOKEN = os.environ.get(
    "FACEBOOK_WEBHOOK_VERIFY_TOKEN")


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    facebook_id = db.Column(db.String, unique=True)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Free form address for simplicity.
    full_address = db.Column(db.String, nullable=False)

    # Connect each address to exactly one user.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    # This adds an attribute 'user' to each address, and an attribute
    # 'addresses' (containing a list of addresses) to each user.
    user = db.relationship('User', backref='addresses')


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Free form for simplicity. for now, an user can have multiples time the same task. This could be improve
    full_task = db.Column(db.String, nullable=False)

    # Connect each task to exactly one user.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    #This param is a boolean for the task. For default is False.
    is_check = db.Column(db.Boolean, nullable=False, default=False)
    # This adds an attribute 'user' to each task, and an attribute
    # 'tasks' (containing a list of tasks) to each user.
    user = db.relationship('User', backref='tasks')


def handle_message(message, sender_id):
    """This function deals with all the messages from a user. It has all the logic """

    #First query for the user that is taking to the bot
    user = User.query.filter(User.facebook_id == sender_id).first()
    if not user:
        user = User(facebook_id=sender_id)
        db.session.add(user)
        db.session.commit()
        return "Grettings, what is your name? "

    #If there is an user but the bot doesn't have a name
    elif not user.username:
        user.username = message
        db.session.add(user)
        db.session.commit()
        return "Hi, %s! Type LIST to know your to-do list" % (user.username)

    elif "LIST DONE" in message:
        done_task = Tasks.query.filter(Tasks.user_id == user.id, Tasks.is_check.is_(True)).all()
        number_done = len(done_task)
        print done_task
        done_list = []
        for task in done_task:
            done_list.append((str(task.id), task.full_task))
        print done_list
        dones = [' '.join(item) for item in done_list]
        return "You currently have %i items DONE in your to-do list. %s." % (number_done, dones)

    elif "LIST" in message:
        all_task = user.tasks
        number_task = len(all_task)
        if not all_task:
            return "%s, you don't have to-dos in your list. Do you want to add a new task? Please type ADD before your task" % (user.username)

        else:
            notdone_task = Tasks.query.filter(Tasks.user_id == user.id, Tasks.is_check.is_(False)).all()

            notdone_list = []
            for task in notdone_task:
                notdone_list.append((str(task.id), task.full_task))

            string_list = [' '.join(item) for item in notdone_list]
            return "You currently have %i items in your to-do list. %s." % (len(notdone_list), string_list)

        return "All you %i tasks are done. Do you want to add a task? Please type ADD before your task" % (number_task)


    elif "ADD" in message:
        new_task_message = ADD_TASK_REGEX.search(message)
        new_task = new_task_message.group(1)
        user_new_task = Tasks(full_task=new_task, user=user)
        db.session.add(user_new_task)
        db.session.commit()
        return "To-do item '%s' added to list." % (new_task)

    elif "DONE" in message:
        new_done_message = DONE_TASK_REGEX.search(message)
        new_done_task_string = new_done_message.group(1)
        new_done_task = Tasks.query.filter(Tasks.full_task == new_done_task_string, Tasks.user_id == user.id).first()
        if not new_done_task:
            return "Sorry %s, I don't have that to-do item for you. Are you sure you type correctly? Please type the same item"
        else:
            new_done_task.is_check = True
            db.session.merge(new_done_task)
            db.session.commit()
            return "To-do item #%i (%s) marked as done." % (new_done_task.id, new_done_task.full_task)

    return "Hi, %s. I'm a to-do bot. You can ADD items, mark as DONE items, see all your LIST, or all your LIST DONE items.\n What do you want to do?" % (user.username)


@app.route('/')
def index():
    """Simple example handler.

    This is just an example handler that demonstrates the basics of SQLAlchemy,
    relationships, and template rendering in Flask.

    """
    # Just for demonstration purposes
    for user in User.query:  #
        print 'User %d, username %s' % (user.id, user.username)
        for address in user.addresses:
            print 'Address %d, full_address %s' % (
                address.id, address.full_address)

    # Render all of this into an HTML template and return it. We use
    # User.query.all() to obtain a list of all users, rather than an
    # iterator. This isn't strictly necessary, but just to illustrate that both
    # User.query and User.query.all() are both possible options to iterate over
    # query results.
    return flask.render_template('index.html', users=User.query.all())

#This comment isn't Skynet level AI either, but I like the "keep it short policy"
@app.route('/fb_webhook', methods=['GET', 'POST'])
def fb_webhook():
    """This handler deals with incoming Facebook Messages.

    In this example implementation, we handle the initial handshake mechanism,
    then just echo all incoming messages back to the sender. Not exactly Skynet
    level AI, but we had to keep it short...

    """
    # Handle the initial handshake request.
    if flask.request.method == 'GET':
        if (flask.request.args.get('hub.mode') == 'subscribe' and
            flask.request.args.get('hub.verify_token') ==
            WEBHOOK_VERIFICATION_TOKEN):
            challenge = flask.request.args.get('hub.challenge')
            return challenge
        else:
            print 'Received invalid GET request'
            return ''  # Still return a 200, otherwise FB gets upset.

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json
    print payload

    # TODO: Validate app ID and other parts of the payload to make sure we're
    # not accidentally processing data that wasn't intended for us.

    # Handle an incoming message.
    # TODO: Improve error handling in case of unexpected payloads.
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

    # Return an empty response.
    return ''

if __name__ == '__main__':
    app.run(debug=True)
