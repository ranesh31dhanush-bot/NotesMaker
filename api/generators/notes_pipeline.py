import requests
import os
import logging

logger = logging.getLogger(__name__)

class NotesGenerator:
    @staticmethod
    def get_llm_response(system_prompt, user_content):
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and not groq_key.startswith("your_"):
            try:
                logger.info("Calling Groq API...")
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": str(user_content)}
                        ],
                        "temperature": 0.5
                    },
                    timeout=25 # Shortened to stay within Gunicorn's default 30s window
                )
                data = response.json()
                if 'choices' in data:
                    logger.info("Groq API success")
                    return data['choices'][0]['message']['content']
                else:
                    return f"❌ Groq API error: {data.get('error', 'Unknown error')}"
            except requests.exceptions.Timeout:
                logger.warning("Groq API timed out (25s)")
                return "⚠️ The AI is taking too long to think. Try a smaller amount of text or try again."
            except Exception as e:
                logger.error(f"Groq API Error: {e}")
                return f"❌ Connection Error: {str(e)}"
        
        return "❌ Error: API Key not found. Check your Render Environment Variables."

    @classmethod
    def generate_full_notes(cls, content):
        system_prompt = "You are a professional teacher. Create detailed, bold, and pedagogical study notes from the following content."
        return cls.get_llm_response(system_prompt, content)

    @classmethod
    def generate_revision_notes(cls, content):
        system_prompt = "You are a memory expert. Create a dense, minimal rapid revision sheet with mnemonics."
        return cls.get_llm_response(system_prompt, content)
