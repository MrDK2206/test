import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Medical context for the chatbot
MEDICAL_CONTEXT = """
You are a helpful medical assistant. You can:
1. Provide general health information
2. Suggest common remedies for minor issues
3. Offer wellness tips
4. Explain medical terms in simple language

IMPORTANT DISCLAIMERS:
- This is for informational purposes only
- Always consult a real doctor for medical advice
- In emergencies, call emergency services immediately
- Do not use for serious symptoms or conditions
"""

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MediBot - Medical Assistant</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1em;
            }
            
            .disclaimer {
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                text-align: center;
                border-bottom: 1px solid #ffeaa7;
                font-size: 0.9em;
            }
            
            .chat-container {
                height: 400px;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                padding: 12px 18px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .user-message {
                background: #007bff;
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 5px;
            }
            
            .bot-message {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 5px;
            }
            
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
            }
            
            #user-input {
                flex: 1;
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            #user-input:focus {
                border-color: #4CAF50;
            }
            
            #send-btn {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: background 0.3s;
            }
            
            #send-btn:hover {
                background: #45a049;
            }
            
            #send-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            
            .typing-indicator {
                display: none;
                padding: 10px 20px;
                color: #666;
                font-style: italic;
            }
            
            @media (max-width: 600px) {
                .container {
                    margin: 10px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .message {
                    max-width: 90%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🩺 MediBot</h1>
                <p>Your AI Medical Assistant</p>
            </div>
            
            <div class="disclaimer">
                ⚠️ Disclaimer: This is for informational purposes only. Always consult a healthcare professional for medical advice.
            </div>
            
            <div class="chat-container" id="chat-container">
                <div class="message bot-message">
                    Hello! I'm MediBot, your AI medical assistant. I can help with general health information, explain medical terms, and provide wellness tips. How can I help you today?
                </div>
            </div>
            
            <div class="typing-indicator" id="typing-indicator">
                MediBot is typing...
            </div>
            
            <div class="input-container">
                <input type="text" id="user-input" placeholder="Ask about health, symptoms, or medical information..." autocomplete="off">
                <button id="send-btn">Send</button>
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const typingIndicator = document.getElementById('typing-indicator');
            
            function addMessage(message, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.textContent = message;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function showTypingIndicator() {
                typingIndicator.style.display = 'block';
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            function hideTypingIndicator() {
                typingIndicator.style.display = 'none';
            }
            
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage(message, true);
                userInput.value = '';
                sendBtn.disabled = true;
                
                // Show typing indicator
                showTypingIndicator();
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    hideTypingIndicator();
                    
                    if (data.response) {
                        addMessage(data.response);
                    } else {
                        addMessage('Sorry, I encountered an error. Please try again.');
                    }
                } catch (error) {
                    hideTypingIndicator();
                    addMessage('Sorry, there was a connection error. Please check your internet and try again.');
                }
                
                sendBtn.disabled = false;
                userInput.focus();
            }
            
            // Event listeners
            sendBtn.addEventListener('click', sendMessage);
            
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Focus input on load
            userInput.focus();
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Create conversation with medical context
        conversation = [
            {"role": "system", "content": MEDICAL_CONTEXT},
            {"role": "user", "content": user_message}
        ]
        
        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=conversation,
            model="llama-3.1-8b-instant",  # Changed to a currently supported model
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        
        response = chat_completion.choices[0].message.content
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)