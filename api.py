
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from svi.pipeline import run
from svi.scoring import recommend


app = FastAPI(
    title="SpeakSense Care API",
    description=(
        "AI-assisted text and distress-indicator analysis "
        "for human review. Not a diagnostic tool."
    ),
    version="1.0.0",
)


# Allow the local React development server to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class TextRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10000,
        description="Text to analyse",
    )


@app.get("/")
def home():
    return {
        "app": "SpeakSense Care",
        "message": "API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_text(request: TextRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="Please enter text to analyse.",
        )

    try:
        # Call your existing AI pipeline.
        result = run(text=text)

        if not isinstance(result, dict):
            raise RuntimeError(
                "The existing pipeline did not return a dictionary."
            )

        text_scores = result.get("text_scores", {})
        category = result.get("category")
        svi = result.get("svi")

        if category is None or svi is None:
            raise RuntimeError(
                "The pipeline response is missing SVI or category."
            )

        # Generate recommendations using the existing scoring module.
        recommendations = recommend(category, text_scores)

        return {
            "svi": svi,
            "category": category,
            "text_scores": text_scores,
            "safety_flags": {
                "suicide_review": bool(
                    text_scores.get("suicide_review", False)
                ),
                "threat_review": bool(
                    text_scores.get("threat_review", False)
                ),
            },
            "recommendations": recommendations,
            "notice": (
                "Experimental indicators only. "
                "A qualified human reviewer must assess the context."
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        # Keep internal exception details out of the public response.
        print(f"SpeakSense Care API error: {exc}")
        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis failed. Check the backend terminal "
                "for details."
            ),
        ) from exc
