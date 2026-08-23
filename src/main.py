from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, ImageRecord, PostRecord, ReviewRecord
from matching_engine import get_embedding, cosine_similarity, mismatch_guard

app = FastAPI(title="AI Image Matching Engine")

class ReviewCreate(BaseModel):
    post_id: int
    image_id: int
    is_approved: bool
    reason: str

@app.get("/posts/{post_id}/images")
def get_image_suggestions(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostRecord).filter(PostRecord.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_dict = {"title": post.title, "content": post.content}
    post_vector = get_embedding(f"{post.title}: {post.content}")

    images = db.query(ImageRecord).all()
    if not images:
        raise HTTPException(status_code=404, detail="No images in database")

    scored_candidates = []
    for img in images:
        if not img.embedding:
            continue
        score = cosine_similarity(post_vector, img.embedding)

        candidate_dict = {
            "subject": img.subject,
            "confidence": img.confidence
        }
        scored_candidates.append((score, img, candidate_dict))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    top_score, top_img, top_candidate_dict = scored_candidates[0]

    approved, reason = mismatch_guard(post_dict, top_candidate_dict, top_score)

    return {
        "post_id": post.id,
        "post_title": post.title,
        "suggested_image": {
            "id": top_img.id,
            "filename": top_img.filename,
            "subject": top_img.subject,
            "confidence": top_img.confidence,
            "similarity_score": round(top_score, 4)
        },
        "guard_status": "APPROVED" if approved else "REJECTED",
        "reason": reason
    }
@app.post("/reviews")
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    new_review = ReviewRecord(
        post_id=review.post_id,
        image_id=review.image_id,
        is_approved=review.is_approved,
        reason=review.reason
    )
    db.add(new_review)
    db.commit()
    return {"status": "success", "message": "Review recorded in audit trail"}