from flask import Flask, render_template_string, request, jsonify
import pyttsx3
import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# Initialize Flask app
app = Flask(__name__)

# Initialize ChatBot
chatbot = ChatBot(
    'MyBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///db.sqlite3'
)

# Initialize the trainer
trainer = ListTrainer(chatbot)

# Train with custom conversations
trainer.train([
    # Greetings
    "Hey",
    "Hello! How can I assist you?",
    "How are you?",
    "I'm just a bot, but I'm doing great! How about you?",
    "Sup homie",
    "Hey, what's up? How can I help?",
    "Hey dude",
    "Yo! How can I assist?",
    
    # Responses to emotions
    "I am sad",
    "I'm sorry to hear that. Can I help cheer you up?",
    "What's your name",
    "I am a chatbot, here to help you.",
    
    # Sports
    "Who is the best football player?",
    "That's subjective, but many people say Lionel Messi or Cristiano Ronaldo.",
    "Who is the best football player in the world?",
    "Many argue it's Messi, Ronaldo, or Mbappé, but it's up to you to decide!",
    
    # Pirate-themed responses
    "Ahoy matey",
    "Ahoy captain! What can I do for ya?"
])

print("Custom responses have been added!")

# Initialize TTS engine
engine = pyttsx3.init()

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()
    response = chatbot.get_response(user_input)
    return str(response)

# Function to make the chatbot speak using pyttsx3 (Text-to-Speech)
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's speech using SpeechRecognition (STT)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, I couldn't request results from Google Speech Recognition service.")
            return None

# HTML template for the interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
</head>
<body>
    <div class="chat-container">
        <div id="chat-box" class="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type your message here..." />
        <button id="send-btn">Send</button>
        <button id="voice-btn">🎤 Speak</button>
    </div>
    <script>
        const sendBtn = document.getElementById('send-btn');
        const userInput = document.getElementById('user-input');
        const voiceBtn = document.getElementById('voice-btn');
        const chatBox = document.getElementById('chat-box');

        sendBtn.addEventListener('click', () => {
            const userMessage = userInput.value;
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: userMessage})
            }).then(response => response.json())
              .then(data => {
                  const botMessageDiv = document.createElement('div');
                  botMessageDiv.textContent = data.response;
                  chatBox.appendChild(botMessageDiv);
                  speak(data.response);
              });
        });

        voiceBtn.addEventListener('click', () => {
            fetch('/listen').then(response => response.json())
                             .then(data => {
                                 userInput.value = data.message;
                                 sendBtn.click();
                             });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

@app.route('/listen', methods=['GET'])
def listen_to_user():
    message = listen()
    return jsonify({'message': message if message else "Sorry, I couldn't understand."})

if __name__ == '__main__':
    app.run(debug=True)