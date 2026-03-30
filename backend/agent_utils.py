import logging
import re
from typing import List

import google.generativeai as genai

from .config import GEMINI_API_KEY, RED_FLAGS

logger = logging.getLogger(__name__)

# Configure Gemini once at startup
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("⚠️ GEMINI_API_KEY environment variable is not set!")


def detect_red_flags(text: str) -> List[str]:
    """
    Scan the input text against predefined keywords in config.py.
    
    Returns:
        List of identical phrases found in the user's text for highlighting.
    """
    found_flags = []
    text_lower = text.lower()
    
    for category, keywords in RED_FLAGS.items():
        for kw in keywords:
            # We use a regex word boundary match so we don't flag "corrupt" in "corruption"
            # unless we intended to. Adjust regex to suit exact matches.
            pattern = r"\b" + re.escape(kw.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found_flags.append(kw)
                
    return list(set(found_flags)) # Return unique flags


def generate_reasoning(text: str) -> str:
    """
    Calls the Gemini 3 Pro API to generate a deterministic "Reasoning Summary".
    
    Returns:
        String explanation of why the input is biased or unreliable.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key missing. Cannot generate AI explanation."
        
    try:
        # Prompting Gemini for a concise Explainable AI result
        prompt = (
            f"Analyze this news snippet for credibility:\n\n"
            f"\"{text}\"\n\n"
            f"Identify the top 2 reasons why it might be biased or unreliable. "
            f"Be concise (max 3 sentences). If it appears highly reliable, explain why."
        )
        
        # Best model choice for logic/reasoning
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        return "Unable to generate an AI explanation for this content."
        
    except Exception as e:
        import traceback
        print("\n=== GEMINI ERROR ===")
        traceback.print_exc()
        print("====================\n")
        logger.exception(f"❌ Gemini API Error: {e}")
        
        if "NotFound" in str(type(e)):
            return "Unable to access Gemini model. Please check if your API key is active or if the model name is correct."
            
        return "Explanation service is currently unavailable. Please try again later."

def extract_text_from_image(image_bytes: bytes, mime_type: str) -> str:
    """
    Calls Gemini 1.5 Flash to act as an advanced OCR agent.
    Extracts the primary news headline and body text, ignoring UI elements.
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is missing for OCR extraction.")
        return ""
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = (
            "Extract only the primary news headline and body text from this screenshot. "
            "Ignore UI elements like like/share buttons, timestamps, or advertisements. "
            "Return just the clean text of the article."
        )
        
        image_parts = [
            {
                "mime_type": mime_type,
                "data": image_bytes
            }
        ]
        
        logger.info("Sending image to Gemini for OCR extraction...")
        response = model.generate_content([prompt, image_parts[0]])
        
        if response.text:
            cleaned_text = response.text.strip()
            logger.info("OCR Extraction successful.")
            return cleaned_text
            
        return ""
        
    except Exception as e:
        logger.exception(f"❌ Gemini Vision API Error: {e}")
        return ""
