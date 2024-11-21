import http.server
import socketserver
import json
from urllib.parse import unquote
import wikipediaapi
from gtts import gTTS
from pydub import AudioSegment
import os
from bs4 import BeautifulSoup
import requests

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="Project-Cosebot/1.0 (https://github.com/Cosebot/Project-Cosebot)"
)

# Function to generate bot responses
def get_bot_response(user_message):
    responses = {
        "hi": "Hello! How can I assist you?",
        "hello": "Hi there! How can I help?",
        "how are you?": "I'm doing great as usual! How can I assist?",
        "bye": "Goodbye! Have a great day!",
        "what is your name?": "I'm Roronoa Zoro! But you can call me Zoro.",
        "thank you": "You're welcome! Let me know if there's anything else I can do.",
        "what can you do?": "As I am in my update 2, I can chat, search Wikipedia, scrape websites, and even reply using my voice!",
        "how old are you?": "I am 30!",
    }

    if user_message.lower().startswith("wiki "):
        topic = user_message[5:]
        return get_wikipedia_summary(topic)

    if user_message.lower().startswith("scrape "):
        url = user_message[7:]
        return scrape_website(url)

    return responses.get(user_message.lower(), "Sorry, I don't understand that.")

# Function to get a Wikipedia summary
def get_wikipedia_summary(topic):
    page = wiki_wiki.page(topic)
    if page.exists():
        return page.summary[:500] + "..."  # Return first 500 characters
    else:
        return "Sorry, I couldn't find anything on Wikipedia for that topic."

# Function to scrape a website
def scrape_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return "Here is the title of the page: " + soup.title.string
    except Exception as e:
        return f"Failed to scrape the website: {str(e)}"

# def generate_tts_response(text):
    # Generate TTS audio using gTTS
    tts = gTTS(text)
    tts.save("response.mp3")
    
    # Lower the pitch using Pydub
    sound = AudioSegment.from_file("response.mp3")
    octaves = -0.3  # Adjust this value to lower pitch further (negative for deeper voice)
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    
    # Apply the pitch change
    sound = sound._spawn(sound.raw_data, overrides={"frame_rate": new_sample_rate})
    sound = sound.set_frame_rate(44100)  # Set back to standard frame rate
    
    # Export the modified audio
    sound.export("response.mp3", format="mp3")
   
    return "response.mp3"

# The request handler class
class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the HTML, CSS, and JavaScript
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Python Chatbot</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f5f5f5;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .chatbox {{
                        background-color: #fff;
                        width: 300px;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        padding: 20px;
                        display: flex;
                        flex-direction: column;
                        height: 400px;
                    }}
                    .chatlogs {{
                        flex-grow: 1;
                        overflow-y: auto;
                        margin-bottom: 10px;
                    }}
                    .chat-input {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    .chat-input input {{
                        width: 80%;
                        padding: 8px;
                        border-radius: 5px;
                        border: 1px solid #ddd;
                    }}
                    .chat-input button {{
                        padding: 8px 12px;
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }}
                    .user-msg {{
                        text-align: right;
                        margin: 10px 0;
                        padding: 10px;
                        background-color: #f1f1f1;
                        border-radius: 10px;
                        max-width: 80%;
                        margin-left: auto;
                    }}
                    .bot-msg {{
                        text-align: left;
                        margin: 10px 0;
                        padding: 10px;
                        background-color: #e0e0e0;
                        border-radius: 10px;
                        max-width: 80%;
                    }}
                </style>
            </head>
            <body>
                <div class="chatbox">
                    <div class="chatlogs" id="chatlogs"></div>
                    <div class="chat-input">
                        <input type="text" id="userInput" placeholder="Type your message...">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
                <script>
                    function sendMessage() {{
                        var userInput = document.getElementById("userInput").value;
                        if (userInput.trim() !== "") {{
                            var chatlogs = document.getElementById("chatlogs");

                            // Display user message
                            chatlogs.innerHTML += "<div class='user-msg'>" + userInput + "</div>";
                            document.getElementById("userInput").value = "";

                            // Send input to Python backend and get response
                            fetch('/get_response?message=' + encodeURIComponent(userInput))
                            .then(response => response.json())
                            .then(data => {{
                                // Display bot response
                                chatlogs.innerHTML += "<div class='bot-msg'>" + data.response + "</div>";
                                chatlogs.scrollTop = chatlogs.scrollHeight;

                                // If audio file exists, play it
                                if (data.audio) {{
                                    var audio = new Audio('/' + data.audio);
                                    audio.play();
                                }}
                            }});
                        }}
                    }}
                </script>
            </body>
            </html>
            """.encode())
        elif self.path.startswith('/get_response'):
            # Handle chatbot response requests
            try:
                message = unquote(self.path.split('=')[1])  # Extract message from URL
                response = get_bot_response(message)
                audio_file = generate_tts_response(response)  # Generate TTS
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"response": response, "audio": audio_file}).encode())
            except IndexError:
                self.send_error(400, "Bad Request: No message provided.")
        elif self.path.startswith('/response.mp3'):
            # Serve the audio file
            self.send_response(200)
            self.send_header("Content-type", "audio/mpeg")
            self.end_headers()
            with open("response.mp3", "rb") as file:
                self.wfile.write(file.read())

# Server setup
def run(server_class=http.server.HTTPServer, handler_class=MyHandler, port=8000):
    with socketserver.TCPServer(("", port), handler_class) as httpd:
        print(f"Serving on port {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()