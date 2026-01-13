import os
import json
import base64
from datetime import datetime
from openai import OpenAI
import pypdf
import docx
import streamlit as st

# Default LM Studio Configuration
DEFAULT_BASE_URL = "http://localhost:1234/v1"
DEFAULT_API_KEY = "lm-studio" # LM Studio doesn't require a real key usually

def get_client(base_url=DEFAULT_BASE_URL, api_key=DEFAULT_API_KEY):
    """Returns an OpenAI client configured for LM Studio."""
    return OpenAI(base_url=base_url, api_key=api_key)

def get_models(base_url=DEFAULT_BASE_URL, api_key=DEFAULT_API_KEY):
    """Fetches the list of available models from the LM Studio API.
    
    Prioritizes getting ONLY loaded models using the LM Studio specific API.
    Falls back to standard OpenAI-compatible list if that fails.
    """
    try:
        # 1. Try LM Studio specific endpoint to get loaded models only
        # Construct API URL from Base URL (e.g. http://localhost:1234/v1 -> http://localhost:1234/api/v0/models)
        if "/v1" in base_url:
            api_url = base_url.replace("/v1", "/api/v0/models")
        else:
            api_url = base_url.rstrip("/") + "/api/v0/models"
            
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Filter for loaded models
            loaded_models = [m["id"] for m in data.get("data", []) if m.get("state") == "loaded"]
            
            # If we found loaded models, return them
            if loaded_models:
                return loaded_models
            
            # If no models are loaded, strictly return empty list to avoid showing all files
            # UNLESS the user has no loaded models, in which case we MUST return all models
            # so they can at least select one to load.
            # If we return [], app.py defaults to "local-model" which breaks the API.
            # So, if loaded list is empty, we fall through to the standard list (all models).
            pass # Fall through to fallback

    except Exception as e:
        # Silently fail specific API call
        pass

    # 2. Fallback: Standard OpenAI compatible list
    # Use this if specialized API failed OR if no models were found loaded.
    # This ensures we always have *some* valid model IDs to show, rather than a broken "local-model".
    try:
        client = get_client(base_url, api_key)
        models = client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def encode_image(uploaded_file):
    """Encodes an uploaded image file to base64."""
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def get_system_tools():
    """Returns the list of available tools for the model."""
    return [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Writes content to a file. Overwrites if exists.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file (e.g., 'src/main.py')"
                        },
                        "content": {
                            "type": "string",
                            "description": "The full content to write to the file."
                        }
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Reads the content of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path to the file."
                        }
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Executes a shell command in the current directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute (e.g., 'pip list', 'python main.py')."
                        }
                    },
                    "required": ["command"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "Lists files and directories in the given path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list (default: '.')."
                        }
                    },
                    "required": ["path"],
                },
            },
        }
    ]

def extract_text_from_file(uploaded_file):
    """Extracts text from uploaded PDF, DOCX, or TXT files."""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    # Image handling
    if file_extension in ['png', 'jpg', 'jpeg']:
        return f"[Image File: {uploaded_file.name}]" # Placeholder for text extraction logic, actual image data handled separately

    text = ""
    
    try:
        if file_extension == 'pdf':
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif file_extension in ['docx', 'doc']:
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            # Assume text file
            text = uploaded_file.getvalue().decode("utf-8")
            
        return text.strip()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def save_chat_history(chat_id, messages, title=None):
    """Saves chat history to a local JSON file."""
    if not os.path.exists('chats'):
        os.makedirs('chats')
    
    if not title or title == "LM Studio Client":
        # Generate a title from the first message if not provided
        # Find first user message
        user_msg = next((m['content'] for m in messages if m['role'] == 'user'), None)
        if user_msg:
             if isinstance(user_msg, list): # Multimodal
                 for block in user_msg:
                     if block.get("type") == "text":
                         user_msg = block.get("text", "")
                         break
             if isinstance(user_msg, str):
                title = user_msg[:30] + "..." if len(user_msg) > 30 else user_msg
             else:
                title = "New Chat"
        else:
            title = "New Chat"
        
    chat_data = {
        'id': chat_id,
        'title': title,
        'timestamp': datetime.now().isoformat(),
        'messages': messages
    }
    
    with open(f'chats/{chat_id}.json', 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, indent=2)

def load_chat_history(chat_id):
    """Loads chat history from a local JSON file."""
    try:
        with open(f'chats/{chat_id}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_all_chats():
    """Returns a list of all saved chats."""
    if not os.path.exists('chats'):
        return []
    
    chats = []
    for filename in os.listdir('chats'):
        if filename.endswith('.json'):
            try:
                with open(f'chats/{filename}', 'r', encoding='utf-8') as f:
                    chat = json.load(f)
                    
                    # Fix "LM Studio Client" titles on the fly if encountered
                    title = chat.get('title', 'Untitled Chat')
                    if title == "LM Studio Client":
                         # Try to regenerate from messages
                         msgs = chat.get('messages', [])
                         user_msg = next((m['content'] for m in msgs if m['role'] == 'user'), None)
                         if user_msg:
                            if isinstance(user_msg, list):
                                for block in user_msg:
                                    if block.get("type") == "text":
                                        user_msg = block.get("text", "")
                                        break
                            if isinstance(user_msg, str):
                                title = user_msg[:30] + "..." if len(user_msg) > 30 else user_msg
                    
                    chats.append({
                        'id': chat['id'],
                        'title': title,
                        'timestamp': chat.get('timestamp', '')
                    })
            except:
                continue
                
    # Sort by timestamp descending
    chats.sort(key=lambda x: x['timestamp'], reverse=True)
    return chats

def delete_chat(chat_id):
    """Deletes a chat file."""
    if os.path.exists(f'chats/{chat_id}.json'):
        os.remove(f'chats/{chat_id}.json')
