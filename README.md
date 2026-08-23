# AI Image Understanding & Content Matching Engine

**Author:** Murtada H. Ahmed

## 1. The Mission
The project is about matching images to blog posts based on the meaning of the image. The project includes a mismatch guard that rejects a bad mad when suggesting a wrong picture for a post. This helps in preventing guessing blindly.

## 2. Image Metadata Schema
The images will be sent to Gemini Flash vision model. Then Pydantic will be used to force the AI to return a structured JSON format:
- subject: string, the main focus of the image
- category: string, represents the classification of the image
- attributes: array, visual details
- caption: string, a short description
- confidence: float, a score from 0 to 1 to reflect the confidence of the model

## 3. Matching Strategy & The Guard
1. Embeddings: generate vector embeddings for the image caption and the blog post text
2. Ranking: cosine similarity will be used to rank the image meaning to the post meaning.
3. Mismatch Guard: recommendation will be approved if:
- confidence is high
- cosine similarity passes a strict threshold
- if these are not met, the system rejects it and returns a reason

## 4. Database Design
We will use PostreSQL with the following tables:
- Images: file paths and JSON metadata
- Posts: post titles and text content
- Embeddings: stores the generated vector data for images and posts.
- Reviews: track whether a human approved or rejected system's suggestions.

## 5. Explicit Non-Goal
Only a backend AI system without frontend. The human review will be handled via API endpoints.

## 6. Evaluation
- **Top-1 Precision:** 75.0% (measured on a labeled evaluation dataset).

## 7. Architecture Diagram
```ascii
Images (batch) -> Vision Model -> {tags, caption, confidence} -> embed(caption) -> image_vectors
Posts -> embed(post text) -> post_vectors

GET /posts/:id/images
 ↳ Similarity Ranking (image_vectors × post_vector)
    ↳ Mismatch Guard (tags + threshold + confidence)
       ├─ Suggested image (ranked, explained)
       └─ "No good match" + explanation

```

## 8. Run & Seed Steps

To run this project locally:

1. Ensure Docker is running.

2. Spin up the database: docker compose up -d

3. Seed the database: python src/seed_db.py

4. Start the API server: cd src && uvicorn main:app --reload

5. Run the tests: pytest src/test_engine.py

## 9. 
1. The system currently evaluates a very small corpus of ~50 images.

2. The embeddings rely on external API calls to Google Gemini, meaning processing speed is subject to network latency and rate limits rather than local compute power.
