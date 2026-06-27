"""
Prompt execution logic for Prompt Doctor.
Runs user prompts against sample inputs using the OpenRouter API.
"""

import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def _clean_markdown_fences(text):
    """Remove markdown code fences from model output."""
    cleaned = re.sub(r'```(?:json)?\s*\n?(.*?)\n?```', r'\1', text, flags=re.DOTALL)
    return cleaned.strip()


def run_prompt(prompt, sample_input, model=None, temperature=0.7, max_tokens=2048):
    """
    Execute a user's prompt against the sample input using the OpenRouter API.

    Args:
        prompt: The user's prompt (instructions to the model)
        sample_input: The sample input data to run the prompt against
        model: The model to use (defaults to OPENROUTER_MODEL env var)
        temperature: Model temperature (0.0 - 1.0)
        max_tokens: Maximum tokens in the response

    Returns:
        dict with keys:
            - "success": bool
            - "output": str (model response text)
            - "error": str (if success is False)
            - "raw_response": dict (the full API response, for debugging)
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        return {
            "success": False,
            "output": "",
            "error": "OpenRouter API key not configured. Please set OPENROUTER_API_KEY in .env file.",
        }

    if not model:
        model = OPENROUTER_MODEL

    # Combine the user's prompt with the sample input
    # The user's prompt is the instruction, and sample_input is the data to process
    full_prompt = f"{prompt}\n\nInput:\n{sample_input}"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://prompt-doctor.app",
        "X-Title": "Prompt Doctor",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": full_prompt,
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            output = data["choices"][0]["message"]["content"]
            
            # Clean markdown code fences from JSON responses
            cleaned_output = _clean_markdown_fences(output)
            
            return {
                "success": True,
                "output": cleaned_output,
                "error": None,
                "raw_response": data,
            }
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Unexpected API response format: {json.dumps(data)}",
                "raw_response": data,
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "output": "",
            "error": "Request timed out. Please try again.",
        }
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        try:
            error_data = e.response.json() if e.response else {}
            if "error" in error_data:
                error_msg = error_data["error"].get("message", str(e))
        except (ValueError, AttributeError):
            pass
        return {
            "success": False,
            "output": "",
            "error": f"API request failed: {error_msg}",
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Unexpected error: {str(e)}",
        }


def list_available_models():
    """List available models from OpenRouter."""
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        return []

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    try:
        response = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return [m["id"] for m in data.get("data", [])]
    except Exception:
        return []