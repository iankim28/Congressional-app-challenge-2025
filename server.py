from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import json

import os

from constants import MEMOS_PATH

app = Flask(__name__)
CORS(app)

def llama3_session(messages):
    url = "http://localhost:11434/api/chat"
    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["message"]["content"]

def message_formatter(m, is_user=True):
    role = "user" if is_user else "system"
    return {"role": role, "content": m}

def llama3_wrapper(message_history):
    # read my_memos.txt
    my_memos_path = MEMOS_PATH
    lines = []
    with open(my_memos_path, "r") as fp:
        for l in fp:
            lines.append(l.strip())
    my_memo = "\n".join(lines)

    first_message = [
        {
            "role": "user",
             "content": "Based on the following memos I will ask some questions: " + my_memo,
        }
    ]
    first_response = llama3_session(first_message)

    messages = first_message + [message_formatter(first_response, False)] + message_history
    response = llama3_session(messages)

    return response

messages = []
@app.route('/api/process', methods=['POST'])
def process_input():
    global messages

    data = request.get_json()
    conversation = data.get('conversation', [])
    
    # Get latest user message
    user_message = conversation[-1]['content'] if conversation else ''
    if len(user_message) == 0:
        return jsonify({'response': "Please enter your question"})

    messages.append(message_formatter(user_message, True))
    response = llama3_wrapper(messages)
    messages.append(message_formatter(response, False))
    messages = messages[-10:]

    # Example logic (replace with your model / logic)
    #response_text = f"Echo: {user_message[::-1]}"  # reply with reversed text
    response_text = f"{response}"  # reply with reversed text

    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)

