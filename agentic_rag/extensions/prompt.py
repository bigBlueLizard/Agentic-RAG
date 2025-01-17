from typing import List
import requests
from constants import GEMINI_API_URL, REQUEST_HEADERS


class Agent:
    def __init__(self, instructions: str):
        self.prompt = f"""
You are a very obeying agent which will do as the instructions below say and you always give concise and informative answers: {instructions}
"""

    def wolfram(self, query: str):
        """
        This tool answers mathematical queries using wolfram alpha
        """
        #TODO: implement
        return

    def answer_with_context_gemini(self, context: str, query: str, additional_instructions: str | None = None) -> dict:
        prompt = self.prompt + "Context: \n" + context + f"\nQuery:\n{query}\n"
        if additional_instructions:
            prompt += f"\nAdditional Instructions: {additional_instructions}"
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            GEMINI_API_URL, headers=REQUEST_HEADERS, json=data)

        if response.status_code == 200:
            try:
                res = response.json()
                res['data'] = data

                answer = res['candidates'][0]['content']['parts'][0]['text']
                return {"answer": answer}

            except KeyError:
                return {"error": "the LLM probably found it offensive", "error_code": 403}
        else:
            return {
                "error": f"Error: {response.status_code} - {response.text}",
                "error_code": 500
            }

    def answer_without_context_gemini(self, query: str, additional_instructions: str | None = None) -> dict:
        """
        This method answers a query using the Gemini API without any context.
        """
        prompt = self.prompt + f"\nQuery:\n{query}\n"
        if additional_instructions:
            prompt += f"\nAdditional Instructions: {additional_instructions}"
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            GEMINI_API_URL, headers=REQUEST_HEADERS, json=data)

        if response.status_code == 200:
            try:
                res = response.json()
                res['data'] = data

                answer = res['candidates'][0]['content']['parts'][0]['text']
                return {"answer": answer}

            except KeyError:
                return {"error": "the LLM probably found it offensive", "error_code": 403}
        else:
            return {
                "error": f"Error: {response.status_code} - {response.text}",
                "error_code": 500
            }
