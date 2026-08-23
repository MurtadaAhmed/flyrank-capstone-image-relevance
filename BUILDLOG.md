# AI Usage Build Log

This document tracks how AI was used during the development of the Image Matching Engine, including where it helped, where it failed, and how the code was adapted.

## Phase 1 & 2: Image Understanding Pipeline
* **Where AI helped:** I used AI to write the initial batch processing loop and map the Gemini vision output to my strict Pydantic schema. 
* **Where it was wrong:** The AI initially provided code for the deprecated `google.generativeai` SDK. It also made a syntax error by using `json.load()` instead of `json.loads()` for string parsing, which caused the script to crash with a `'str' object has no attribute 'read'` error. Finally, it suggested `gemini-3.5-flash`, which immediately hit a `429 RESOURCE_EXHAUSTED` rate limit on the free tier after 5 images.
* **What I changed:** I manually migrated the client architecture to the new `google.genai` SDK. I fixed the JSON parsing typo, and I downgraded the model to `gemini-3.5-flash-lite` while increasing the `time.sleep()` delay to 4.5 seconds to safely stay under the 15 Requests Per Minute quota.

## Phase 3: Matching Engine & Mismatch Guard
* **Where AI helped:** AI assisted in writing the NumPy cosine similarity math and structuring the logic flow for the Mismatch Guard.
* **Where it was wrong:** 
    1. The AI initially set the `SIMILARITY_THRESHOLD` to `0.60`, but using short image captions against dense blog posts resulted in naturally low cosine scores (around 0.40 - 0.50), causing good matches to be rejected. 
    2. The AI's category guard checked for the exact string `"wolf"`. It failed the forced mismatch demo because the vision model labeled the image as `"wolves"` (plural), allowing the bad image to slip through.
* **What I changed:** I rewrote the embedding function to enrich the text payload by combining the `subject`, `caption`, and `attributes` into one dense string before vectorizing. I also updated the Mismatch Guard's logic to safely catch plurals (e.g., checking for `"wolv"` instead of just `"wolf"`).

## Phase 4: FastAPI & Evaluation
* **Where AI helped:** AI generated helped with the architecture for boilerplate FastAPI routing, the Uvicorn server setup, and the SQLAlchemy database models (`ImageRecord`, `PostRecord`, `ReviewRecord`).
* **Where it was wrong:** The AI indented the `sort()` and `return` statements inside the main image-ranking `for` loop. This caused the API to evaluate only the very first image in the database and immediately return it, ignoring the other 49 candidates.
* **What I changed:** I un-indented the sorting and guard evaluation blocks so the loop could finish scoring the entire PostgreSQL database before selecting the `top_score` candidate.