import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def run_gpt4o_chat(system_prompt, user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"[GPT-4o Error] {str(e)}"
