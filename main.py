from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

from langchain.llms import OpenAI

from langchain.memory import ConversationSummaryBufferMemory

from langchain.chains import ConversationChain

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789'
socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")

api_key = "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"

my_map = {}


def set_up():
    llm = OpenAI(openai_api_key = api_key,
             model_name="text-davinci-002",
             temperature=0.5, max_tokens=150,
            )
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)

    return ConversationChain (
        llm=llm,
        memory=memory,
        verbose=True
    )

# @app.route('/')
# def index():
#     return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session_id = request.sid
    room_name = f'room_{session_id}'
    conversation = set_up()
    my_map[room_name] = conversation

    join_room(room_name)

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    room_name = f'room_{session_id}'
    del my_map[room_name]
    leave_room(room_name)

@socketio.on('message')
def handle_message(message):
    session_id = request.sid
    room_name = f'room_{session_id}'
    conversation = my_map[room_name]
    response = conversation.predict(input = message)
    emit('message', response, room=room_name)

if __name__ == '__main__':
    socketio.run(app, debug=True)
