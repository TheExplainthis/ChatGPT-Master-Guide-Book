from typing import List, Dict
import openai


class ModelInterface:
    def chat_completion(self, messages: List[Dict]) -> str:
        pass


class OpenAIModel(ModelInterface):
    def __init__(self, api_key: str, model_engine: str):
        openai.api_key = api_key
        self.model_engine = model_engine

    def chat_completion(self, messages) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model_engine,
                messages=messages
            )
            role = response['choices'][0]['message']['role']
            content = response['choices'][0]['message']['content'].strip()
            return role, content
        except Exception as e:
            raise e
