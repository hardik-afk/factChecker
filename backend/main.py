import logging
import os


from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conlist

from agent_utils import detect_red_flags, extract_text_from_image, generate_reasoning
from ml_handler import ml_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI App
app = FastAPI(
    title="VeriVibe Backend",
    description="The Agentic News Integrity Shield",
    version="1.0.0",
)

# CORS configuration for the Next.js frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    frontend_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    vibe_score: float
    prediction: str
    red_flags: list[str]
    ai_explanation: str


class VerifyRequest(BaseModel):
    headline: str


class SourceModel(BaseModel):
    name: str
    url: str


class VerifyResponse(BaseModel):
    is_confirmed: bool
    top_sources: list[SourceModel]
    verification_vibe: str


class AnalyzeResponse(BaseModel):
    vibe_score: float
    prediction: str
    red_flags: list[str]
    ai_explanation: str
    is_confirmed: bool
    top_sources: list[SourceModel]
    verification_vibe: str


# ---------------------------------------------------------------------------
# Simulated Antigravity API
# ---------------------------------------------------------------------------
class MockBrowserClient:
    """Simulates invoking the Antigravity Browser API with a subagent skill."""

    async def verify_headline(self, headline: str) -> dict:
        import asyncio
        logger.info(f"Subagent launching to verify: '{headline}'")
        # Simulating subagent network time
        await asyncio.sleep(2.0)

        headline_lower = headline.lower()

        if "space" in headline_lower or "launch" in headline_lower:
            return {
                "is_confirmed": True,
                "top_sources": [
                    {"name": "Reuters", "url": "https://reuters.com/space"},
                    {"name": "BBC", "url": "https://bbc.com/science"},
                    {"name": "AP News", "url": "https://apnews.com/hub/space"}
                ],
                "verification_vibe": "This story is widely verified by major outlets reporting identical launch details."
            }
        elif "hoax" in headline_lower or "alien" in headline_lower or "fake" in headline_lower:
            return {
                "is_confirmed": False,
                "top_sources": [],
                "verification_vibe": "No coverage found on any High-Authority news outlets. This appears to be unsubstantiated."
            }
        else:
            return {
                "is_confirmed": False,
                "top_sources": [{"name": "NYT", "url": "https://nytimes.com/politics"}],
                "verification_vibe": "Only partial, uncorroborated reports were found on authoritative domains."
            }

browser_client = MockBrowserClient()




# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "ok", "message": "VeriVibe Backend is running"}


@app.post("/predict", response_model=PredictResponse)
def analyze_news(request: PredictRequest):
    """
    Analyzes a news snippet using Logistic Regression, Red Flag keyword matching,
    and Gemini 3 Pro Explainable AI reasoning.
    """
    text = request.text.strip()
    
    if not text or len(text) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Bad Request: Text input must be at least 10 characters long."
        )

    logger.info("Running ML inference...")
    # 1. ML Classification
    ml_result = ml_handler.predict(text)
    
    logger.info("Scanning for Red Flags...")
    # 2. Red Flag Detection
    red_flags = detect_red_flags(text)
    
    logger.info("Generating Gemini reasoning...")
    # 3. Agentic Explanation
    ai_explanation = generate_reasoning(text)
    
    return PredictResponse(
        vibe_score=ml_result["vibe_score"],
        prediction=ml_result["prediction"],
        red_flags=red_flags,
        ai_explanation=ai_explanation
    )


@app.post("/ocr-analyze", response_model=PredictResponse)
async def analyze_screenshot(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, extracts text via Gemini Vision OCR,
    and passes it through the ML pipeline to return a Truth Score.
    """
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG and PNG are supported."
        )
        
    image_bytes = await file.read()
    
    logger.info("Extracting text via Gemini Vision...")
    extracted_text = extract_text_from_image(image_bytes, file.content_type)
    
    if not extracted_text or len(extracted_text.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="No news content detected in the image."
        )
        
    logger.info(f"Extracted Text: {extracted_text[:100]}...")
    
    # 1. ML Classification
    ml_result = ml_handler.predict(extracted_text)
    
    # 2. Red Flag Detection
    red_flags = detect_red_flags(extracted_text)
    
    # 3. Agentic Explanation
    ai_explanation = generate_reasoning(extracted_text)
    
    return PredictResponse(
        vibe_score=ml_result["vibe_score"],
        prediction=ml_result["prediction"],
        red_flags=red_flags,
        ai_explanation=ai_explanation
    )


@app.post("/verify", response_model=VerifyResponse)
async def verify_headline(request: VerifyRequest):
    """
    Invokes the Browser Subagent to check the live web for corroborating articles
    from high-authority news platforms.
    """
    headline = request.headline.strip()
    if not headline:
        raise HTTPException(
            status_code=400,
            detail="Bad Request: Headline missing."
        )

    logger.info(f"Triggering Browser Subagent for verification: {headline}")
    
    try:
        # Using the simulated Browser Agent SDK client
        result = await browser_client.verify_headline(headline)
        
        return VerifyResponse(
            is_confirmed=result["is_confirmed"],
            top_sources=[SourceModel(**s) for s in result["top_sources"]],
            verification_vibe=result["verification_vibe"]
        )
    except Exception as e:
        logger.error(f"Browser Subagent execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to run the verification subagent."
        )


from fastapi import Form
from typing import Optional

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_combined(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Unified endpoint that orchestrates prediction, (optional) OCR, and verification together.
    Accepts multipart/form-data: either 'text' or 'file'.
    """
    if file and file.filename:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")
        
        image_bytes = await file.read()
        logger.info("Extracting text via Gemini Vision...")
        extracted_text = extract_text_from_image(image_bytes, file.content_type)
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=422, detail="No news content detected in the image.")
        input_text = extracted_text.strip()
    elif text:
        input_text = text.strip()
        if len(input_text) < 10:
            raise HTTPException(status_code=400, detail="Bad Request: Text input must be at least 10 characters long.")
    else:
        raise HTTPException(status_code=400, detail="Must provide either text or an image file.")

    import asyncio

    logger.info("Running ML inference...")
    ml_result = ml_handler.predict(input_text)
    
    search_query = input_text[:100]
    logger.info("Orchestrating Gemini and Browser Agentic checks concurrently...")
    
    async def get_verification():
        try:
            return await browser_client.verify_headline(search_query)
        except Exception as e:
            logger.error(f"Browser Subagent execution error: {e}")
            return {
                "is_confirmed": False,
                "top_sources": [],
                "verification_vibe": "Verification service unavailable."
            }

    # Run blocking Gemini calls in threads, and async mock browser concurrently
    red_flags, ai_explanation, verification_result = await asyncio.gather(
        asyncio.to_thread(detect_red_flags, input_text),
        asyncio.to_thread(generate_reasoning, input_text),
        get_verification()
    )

    return AnalyzeResponse(
        vibe_score=ml_result["vibe_score"],
        prediction=ml_result["prediction"],
        red_flags=red_flags,
        ai_explanation=ai_explanation,
        is_confirmed=verification_result["is_confirmed"],
        top_sources=[SourceModel(**s) for s in verification_result["top_sources"]],
        verification_vibe=verification_result["verification_vibe"]
    )


