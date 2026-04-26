# core/llm_client.py
import requests
from config import cfg


class LLMClient:
    def __init__(self):
        print(f"[LLM] Member A endpoint: {cfg.LLM_API_URL}")

    def ask(self, question):
        """
        Send question to Member A's RAG+LLM API
        Returns answer text string
        """
        print(f"[LLM] Asking: '{question[:80]}'")
        try:
            response = requests.post(
                cfg.LLM_API_URL,
                json={"question": question},
                timeout=cfg.LLM_TIMEOUT
            )
            response.raise_for_status()
            answer = response.json()["answer"]
            print(f"[LLM] Answer: '{answer[:80]}'")
            return answer

        except requests.exceptions.ConnectionError:
            # Member A's server not running yet
            print("[LLM] Member A not reachable — using fallback response")
            return "I am processing your question. Please give me a moment to respond."

        except requests.exceptions.Timeout:
            print("[LLM] Request timed out")
            return "That is taking longer than expected. Please ask again."

        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return "Sorry, I encountered an issue. Please try again."
