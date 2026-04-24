import requests
import os
import logging

logger = logging.getLogger(__name__)

class NotesGenerator:
    """Handles interaction with Groq AI for note generation"""
    
    @staticmethod
    def get_llm_response(system_prompt, user_content):
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key or groq_key.startswith("your_"):
            return "❌ Error: API Key not configured."

        try:
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
                timeout=25 # Prevents worker timeout on production servers
            )
            data = response.json()
            if 'choices' in data:
                return data['choices'][0]['message']['content']
            return f"❌ AI Error: {data.get('error', 'Unknown response format')}"
        except requests.exceptions.Timeout:
            return "⚠️ The request timed out. Please try with a smaller amount of text."
        except Exception as e:
            logger.error(f"AI Generation Error: {e}")
            return "❌ Connection to AI service failed."

    @classmethod
    def generate_full_notes(cls, content):
        system_prompt = """
        You are a professional pedagogical expert. 
        Transform the input into structured study notes with:
        - Bold headings and bullet points.
        - Simplified 'Explain Like I'm 5' concepts.
        - Practical examples for complex ideas.
        """
        return cls.get_llm_response(system_prompt, content)

    @classmethod
    def generate_revision_notes(cls, content):
        system_prompt = """
        You are a memory specialist. 
        Create a dense, high-impact revision sheet with:
        - Core definitions and formulas only.
        - Memory mnemonics/acronyms for retention.
        - Minimalist, punchy layout.
        """
        return cls.get_llm_response(system_prompt, content)
