import os
from openai import OpenAI
from dotenv import load_dotenv

class OpenAILLM:
    def __init__(self):
        load_dotenv()
        self.model = os.getenv("OPENAI_MODEL")
        self.client = OpenAI(
            api_key = os.getenv("OPENAI_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def generate_completion(self, messages, temperature=0.7, max_tokens=2048, response_format=None):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
