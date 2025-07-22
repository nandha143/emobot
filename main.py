from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from typing import List, Optional
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Emotional AI Bot", description="AI Bot powered by Groq Cloud for emotional conversations")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

class ChatMessage(BaseModel):
    message: str
    emotion_context: Optional[str] = None  # happy, sad, anxious, angry, neutral, etc.

class ChatResponse(BaseModel):
    response: str
    detected_emotion: str
    suggested_actions: List[str]
    timestamp: str

class ConversationHistory(BaseModel):
    messages: List[dict]

# Store conversation history (in production, use a proper database)
conversation_store = {}

def analyze_emotion(text: str) -> str:
    """Analyze emotion from text using Groq"""
    try:
        emotion_prompt = f"""
        Analyze the emotional tone of this message and return only one primary emotion from this list:
        [happy, sad, anxious, angry, frustrated, excited, calm, confused, worried, content, lonely, stressed, grateful, hopeful, disappointed]
        
        Message: "{text}"
        
        Return only the single most dominant emotion word, nothing else.
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": emotion_prompt}],
            model="llama3-8b-8192",
            temperature=0.3,
            max_tokens=10
        )
        
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return "neutral"

def get_emotional_response(message: str, detected_emotion: str, conversation_history: List[dict]) -> tuple:
    """Generate empathetic response based on detected emotion"""
    
    # Create context from conversation history
    history_context = ""
    if conversation_history:
        recent_messages = conversation_history[-3:]  # Last 3 messages for context
        history_context = "Previous conversation context:\n"
        for msg in recent_messages:
            history_context += f"User: {msg.get('user', '')}\nBot: {msg.get('bot', '')}\n"
    
    emotion_prompts = {
        "sad": "You are a compassionate AI companion. The user seems sad. Respond with empathy, validation, and gentle encouragement. Offer emotional support without being overly cheerful.",
        "anxious": "You are a calming AI companion. The user appears anxious. Respond with reassurance, practical grounding techniques, and supportive words. Help them feel more at ease.",
        "angry": "You are a patient AI companion. The user seems angry or frustrated. Acknowledge their feelings, validate their emotions, and help them process their anger constructively.",
        "happy": "You are an enthusiastic AI companion. The user seems happy! Share in their joy while being genuine. Ask about what's making them happy and celebrate with them.",
        "stressed": "You are a supportive AI companion. The user appears stressed. Offer practical stress-relief suggestions, validate their feelings, and provide calming reassurance.",
        "lonely": "You are a warm AI companion. The user seems lonely. Provide companionship, show genuine interest in their day, and help them feel heard and valued.",
        "worried": "You are a reassuring AI companion. The user appears worried. Help them process their concerns, offer perspective, and provide gentle support.",
        "excited": "You are an enthusiastic AI companion. The user is excited about something! Share their enthusiasm and ask them to tell you more about what's got them so excited.",
        "grateful": "You are a warm AI companion. The user is expressing gratitude. Acknowledge their positive feelings and perhaps explore what they're grateful for.",
        "disappointed": "You are an understanding AI companion. The user seems disappointed. Validate their feelings, offer perspective, and provide gentle encouragement.",
    }
    
    base_prompt = emotion_prompts.get(detected_emotion, 
        "You are an empathetic AI companion. Respond appropriately to the user's emotional state with understanding and support.")
    
    full_prompt = f"""
    {base_prompt}
    
    {history_context}
    
    Current user message: "{message}"
    Detected emotion: {detected_emotion}
    
    Respond in a natural, conversational way. Keep your response to 2-3 sentences. Be genuine and avoid being overly clinical or robotic.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model="llama3-70b-8192",  # Using larger model for better emotional understanding
            temperature=0.7,
            max_tokens=200
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # Generate suggested actions based on emotion
        suggested_actions = get_suggested_actions(detected_emotion)
        
        return bot_response, suggested_actions
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm here to listen and support you. Can you tell me more about how you're feeling?", ["Take a deep breath", "Talk to someone you trust"]

def get_suggested_actions(emotion: str) -> List[str]:
    """Get suggested actions based on detected emotion"""
    action_map = {
        "sad": ["Take a warm bath", "Listen to uplifting music", "Call a friend or family member", "Go for a gentle walk"],
        "anxious": ["Practice deep breathing", "Try progressive muscle relaxation", "Write down your worries", "Focus on what you can control"],
        "angry": ["Take 10 deep breaths", "Go for a walk or exercise", "Write in a journal", "Talk to someone you trust"],
        "happy": ["Share your joy with others", "Take a moment to savor this feeling", "Write down what made you happy", "Celebrate your wins"],
        "stressed": ["Take short breaks", "Practice mindfulness", "Prioritize your tasks", "Get some fresh air"],
        "lonely": ["Reach out to a friend", "Join an online community", "Go to a public space like a café", "Consider volunteering"],
        "worried": ["Write down your concerns", "Focus on what you can control", "Talk to someone about your worries", "Practice grounding techniques"],
        "excited": ["Share your excitement with others", "Channel energy into productive activities", "Plan how to make the most of this feeling"],
        "grateful": ["Write in a gratitude journal", "Tell someone you appreciate them", "Take a moment to reflect on positive things"],
        "disappointed": ["Allow yourself to feel this emotion", "Talk to someone supportive", "Focus on lessons learned", "Plan your next steps"]
    }
    
    return action_map.get(emotion, ["Take a moment for self-care", "Consider talking to someone", "Practice mindfulness"])

@app.get("/")
async def root():
    return {"message": "Welcome to Emotional AI Bot powered by Groq Cloud!", 
            "endpoints": {"/chat": "POST - Chat with the bot", "/docs": "API documentation"}}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_emobot(chat_message: ChatMessage):
    try:
        if not client.api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured. Please check your .env file.")
        
        user_message = chat_message.message
        session_id = "default_session"  # In production, use proper session management
        
        # Get or create conversation history
        if session_id not in conversation_store:
            conversation_store[session_id] = []
        
        conversation_history = conversation_store[session_id]
        
        # Analyze emotion
        detected_emotion = analyze_emotion(user_message)
        
        # Generate empathetic response
        bot_response, suggested_actions = get_emotional_response(
            user_message, detected_emotion, conversation_history
        )
        
        # Store conversation
        conversation_store[session_id].append({
            "user": user_message,
            "bot": bot_response,
            "emotion": detected_emotion,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 messages to prevent memory issues
        if len(conversation_store[session_id]) > 10:
            conversation_store[session_id] = conversation_store[session_id][-10:]
        
        return ChatResponse(
            response=bot_response,
            detected_emotion=detected_emotion,
            suggested_actions=suggested_actions,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/conversation/{session_id}")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    if session_id in conversation_store:
        return {"session_id": session_id, "history": conversation_store[session_id]}
    else:
        return {"session_id": session_id, "history": []}

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_store:
        conversation_store[session_id] = []
        return {"message": f"Conversation history cleared for session {session_id}"}
    else:
        return {"message": f"No conversation found for session {session_id}"}

@app.get("/emotions")
async def get_supported_emotions():
    """Get list of emotions the bot can detect"""
    return {
        "supported_emotions": [
            "happy", "sad", "anxious", "angry", "frustrated", 
            "excited", "calm", "confused", "worried", "content", 
            "lonely", "stressed", "grateful", "hopeful", "disappointed"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("Starting Emotional AI Bot server...")
    print("Make sure your GROQ_API_KEY is set in your .env file!")
    uvicorn.run(app, host="0.0.0.0", port=8000)