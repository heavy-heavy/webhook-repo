from datetime import datetime
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient

from config import Config

app=Flask(__name__)
app.config.from_object(Config)

client=MongoClient(app.config['MONGO_URI'])
db=client.github_events

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/webhook',methods=['POST'])
def handle_webhook():
    event_type=request.headers.get('x-Github_Events')
    payload=request.json

    # Handle "push" event
    if event_type == 'push':
        handle_push_event(payload)
    # Handle "pull_request" event
    elif event_type == 'pull_request':
        handle_pull_request_event(payload)
    else:
        return jsonify({'msg': 'Event not processed'}), 200

    return jsonify({'msg': 'Event received'}), 200

def handle_push_event(payload):
    """Handles GitHub push events."""
    author = payload['pusher']['name']
    to_branch = payload['ref'].split('/')[-1]
    timestamp = payload['head_commit']['timestamp']

    event_data = {
        'type': 'push',
        'author': author,
        'to_branch': to_branch,
        'timestamp': datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    }

    # Insert into MongoDB
    db.events.insert_one(event_data)


def handle_pull_request_event(payload):
    """Handles GitHub pull request events."""
    action = payload['action']
    if action not in ['opened', 'closed', 'merged']:
        return  # Only process specific actions

    event_type = 'pull_request' if action != 'merged' else 'merge'
    author = payload['pull_request']['user']['login']
    from_branch = payload['pull_request']['head']['ref']
    to_branch = payload['pull_request']['base']['ref']
    timestamp = payload['pull_request']['created_at']

    event_data = {
        'type': event_type,
        'author': author,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    }

    # Insert into MongoDB
    db.events.insert_one(event_data)

    