import json
from database import SessionLocal, PostRecord, ImageRecord
from matching_engine import get_embedding, cosine_similarity

EVAL_LABELS_PATH = "../data/eval_labels.json"

def run_evaluation():
    db = SessionLocal()

    with open(EVAL_LABELS_PATH, "r", encoding="utf-8") as f:
        eval_labels = json.load(f)

    images = db.query(ImageRecord).all()

    correct_predictions = 0
    total_predictions = len(eval_labels)

    for post_id_str, expected_subject in eval_labels.items():
        post = db.query(PostRecord).filter(PostRecord.post_id_string == post_id_str).first()
        if not post:
            continue
        post_vector = get_embedding(f"{post.title}: {post.content}")
        scored_candidates = []
        for img in images:
            if not img.embedding: continue
            score = cosine_similarity(post_vector, img.embedding)
            scored_candidates.append((score, img))
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_img = scored_candidates[0][1]
        is_correct = expected_subject.lower() in top_img.subject.lower() or top_img.subject.lower() in expected_subject.lower()

        if is_correct:
            correct_predictions += 1
            print(f"{post.title} -> Expected: '{expected_subject}', Got: '{top_img.subject}'")
        else:
            print(f"{post.title} -> Expected: '{expected_subject}', Got: '{top_img.subject}'")

    precision = (correct_predictions / total_predictions) * 100

    print(f"Final Top-1 Precision: {precision:.1f}%")

    db.close()



if __name__ == "__main__":
    run_evaluation()