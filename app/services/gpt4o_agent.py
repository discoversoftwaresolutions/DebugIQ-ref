import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

def run_gpt4o_agent(prompt: str, model: str = "gpt-4o", temperature: float = 0.3, system_message: str = "You are a world-class software debugging agent. Be accurate, concise, and professional.") -> str:
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[GPT-4o Error]: {str(e)}"
