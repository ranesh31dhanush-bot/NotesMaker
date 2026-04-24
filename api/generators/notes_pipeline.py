import requests
import os

class NotesGenerator:
    @staticmethod
    def get_llm_response(system_prompt, user_content):
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and not groq_key.startswith("your_"):
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
                        "temperature": 0.5 # Lower temperature for more structured, consistent notes
                    },
                    timeout=45
                )
                data = response.json()
                if 'choices' in data:
                    return data['choices'][0]['message']['content']
                else:
                    return f"❌ Groq API error: {data.get('error', 'Unknown error')}"
            except Exception as e:
                return f"❌ Groq Connection Error: {str(e)}"
        
        return "❌ Error: API Key not found. Please check your .env.example file."

    @classmethod
    def generate_full_notes(cls, content):
        system_prompt = """
        YOU ARE JOHN, A PROFESSIONAL TEACHER CREATING HIGH-QUALITY NOTES.
        
        GOAL: Transform the provided unstructured content into a structured pedagogical masterpiece.
        
        OUTPUT REQUIREMENTS:
        - Clear, bold headings for every major topic.
        - Simple, beginner-friendly explanations (explain like I'm 10).
        - PROVIDE AT LEAST ONE PRACTICAL EXAMPLE for every major concept found.
        - CLEAR DEFINITIONS for all technical terms.
        - STEP-BY-STEP BREAKDOWNS for any processes or logic.
        
        STYLE:
        - Use bullet points for readability.
        - Use bold text for key terms.
        - Avoid complex jargon.
        - DO NOT copy raw text from the input; synthesize and teach.
        - Exclude irrelevant info or chat filler.
        """
        return cls.get_llm_response(system_prompt, f"UNSTRUCTURED CONTENT TO TRANSFORM:\n\n{content}")

    @classmethod
    def generate_revision_notes(cls, content):
        system_prompt = """
        YOU ARE SALLY, A UX DESIGNER AND MEMORY EXPERT CREATING A RAPID REVISION SHEET.
        
        GOAL: Compress the content so a student can revise EVERYTHING in 10 minutes.
        
        OUTPUT REQUIREMENTS:
        - Only key ideas and keywords.
        - Short, punchy bullet points.
        - NO EXPLANATIONS unless absolutely necessary for context.
        - USE MEMORY TRICKS (Mnemonics, acronyms, or analogies) to help retention.
        - HIGHLIGHT FORMULAS AND CORE DEFINITIONS explicitly.
        
        STRUCTURE:
        - Topic -> 3–6 bullets max per topic.
        - Use a minimal, dense layout.
        
        TONE:
        - Dense, Minimal, Exam-focused.
        """
        return cls.get_llm_response(system_prompt, f"CONTENT TO COMPRESS FOR REVISION:\n\n{content}")
