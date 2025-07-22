# 🤖 Emotional AI Bot

An empathetic AI chatbot powered by Groq Cloud that understands and responds to human emotions.

## ✨ Features

- **Emotion Detection**: Analyzes user messages to detect emotions like happy, sad, anxious, angry, etc.
- **Empathetic Responses**: Provides contextually appropriate responses based on detected emotions
- **Actionable Suggestions**: Offers practical suggestions for emotional well-being
- **Beautiful UI**: Clean, modern chat interface with emotion badges
- **Real-time Chat**: Fast responses powered by Groq's LLaMA models

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/emotionalchatbot.git
   cd emotionalchatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the backend**
   ```bash
   python main.py
   ```

5. **Open the frontend**
   - Open `frontend.html` in your browser, or
   - Serve it via HTTP: `python -m http.server 3000` then go to `http://localhost:3000/frontend.html`

## 🔧 API Endpoints

- `GET /` - Welcome message and API info
- `POST /chat` - Chat with the bot
- `GET /emotions` - List of supported emotions
- `GET /health` - Health check
- `GET /conversation/{session_id}` - Get conversation history
- `DELETE /conversation/{session_id}` - Clear conversation

## 🎯 Supported Emotions

Happy, Sad, Anxious, Angry, Frustrated, Excited, Calm, Confused, Worried, Content, Lonely, Stressed, Grateful, Hopeful, Disappointed

## 🛠️ Tech Stack

- **Backend**: FastAPI, Groq Cloud, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI Model**: LLaMA 3 (via Groq)

## 📝 Usage Example

```python
import requests

response = requests.post("http://127.0.0.1:8000/chat", 
    json={"message": "I'm feeling really anxious about my presentation tomorrow"})

print(response.json())
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- Never commit your `.env` file or API keys to the repository
- The bot provides emotional support but is not a replacement for professional mental health care
- Conversation history is stored in memory and will be lost when the server restarts

## 🙋‍♀️ Support

If you have any questions or issues, please open an issue on GitHub.

---

Made with ❤️ and AI
