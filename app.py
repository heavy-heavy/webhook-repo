from datetime import datetime
from flask import Flask, request, jsonify, abort
from pymongo import MongoClient
from flask_cors import CORS

from config import Config

app=Flask(__name__)
CORS(app)
app.config.from_object(Config)

client=MongoClient(app.config['MONGO_URI'])
db=client.github_events
events_collection = db.events 

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/webhook',methods=['POST'])
def handle_webhook():
    event_type=request.headers.get('X-Github-Event')
    payload=request.json

    # Handle "push" event
    if event_type == 'push':
        handle_push_event(payload)
    # Handle "pull_request" event
    elif event_type == 'pull_request':
        if payload['action'] == 'opened':
            handle_pull_request_event(payload)
        elif payload['action'] == 'closed' and payload['pull_request']['merged']:
            handle_merge_event(payload)  # Call merge handler if the pull request is merged
    else:
        return jsonify({'msg': 'Event not processed'}), 200

    return jsonify({'msg': 'Event received'}), 200

def handle_push_event(payload):
    #Handles GitHub push events
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
    #Handles GitHub pull request events
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

def handle_merge_event(payload):
    #Handles GitHub merge events that occur via pull requests.
    author = payload['pull_request']['user']['login']  # Author of the pull request
    from_branch = payload['pull_request']['head']['ref']  # Source branch being merged
    to_branch = payload['pull_request']['base']['ref']  # Target branch for the merge
    timestamp = payload['pull_request']['merged_at']  # Timestamp of the merge

    # Check if the action is 'merged' (specifically looking for merged pull requests)
    if payload['action'] == 'closed' and payload['pull_request']['merged']:
        event_data = {
            'type': 'merge',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ') 
        }

        # Insert the merge event into the MongoDB collection
        db.events.insert_one(event_data)


@app.route('/api/events', methods=['GET'])
def get_events():
    # Fetches the latest events from MongoDB
    events = list(db.events.find().sort('timestamp', -1).limit(100))
    for event in events:
        event['_id'] = str(event['_id'])  # Convert ObjectId to string
    return jsonify(events), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])