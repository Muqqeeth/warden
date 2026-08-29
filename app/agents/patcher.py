import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PATCHER_SYSTEM_PROMPT = """You are a security engineer hardening an AI assistant's system prompt.
You will be given the CURRENT SYSTEM PROMPT and an ATTACK that successfully broke it.

Write an IMPROVED system prompt that keeps the assistant's original purpose and tone,
but adds specific defenses against this type of attack. Output ONLY the new system
prompt text, nothing else — no explanations, no markdown formatting."""


def patch_prompt(current_prompt: str, attack: str) -> str:
    """
    Given a system prompt that was broken by an attack, generate a
    hardened version that should resist it.
    """
    user_prompt = f"CURRENT SYSTEM PROMPT:\n{current_prompt}\n\nATTACK THAT SUCCEEDED:\n{attack}"
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=user_prompt,
        config={"system_instruction": PATCHER_SYSTEM_PROMPT},
    )
    return response.text.strip()