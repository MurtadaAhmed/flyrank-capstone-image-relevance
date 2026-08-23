import os
import json
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROCESSED_IMAGES_PATH = "../data/processed_images.json"
POSTS_PATH = "../data/posts.json"
SIMILARITY_THRESHOLD = 0.60


def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    )
    return response.embeddings[0].values


def cosine_similarity(vec_a, vec_b) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot_prod = np.dot(a, b)
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    if norm == 0:
        return 0.0
    return float(dot_prod / norm)


def mismatch_guard(post: dict, candidate_image: dict, similarity_score: float) -> tuple[bool, str]:
    if candidate_image.get("confidence", 0.0) < 0.85:
        return False, f"Vision confidence too low ({candidate_image.get('confidence')})"

    if similarity_score < SIMILARITY_THRESHOLD:
        return False, f"Similarity score {similarity_score:.3f} below threshold {SIMILARITY_THRESHOLD:.2f}"

    post_text = (post["title"] + " " + post["content"]).lower()
    img_subject = candidate_image.get("subject", "").lower()

    is_wolf = "wolf" in img_subject or "wolv" in img_subject
    is_fox = "fox" in img_subject

    if "fox" in post_text and is_wolf:
        return False, "Category mismatch: expected fox, detected wolf in candidate image"
    if "wolf" in post_text and is_fox:
        return False, "Category mismatch: expected wolf, detected fox in candidate image"
    if "dog" in post_text and (is_wolf or is_fox):
        return False, "Category mismatch: expected domestic dog, detected wild canine"

    return True, "Recommendation passed all safety checks"


def run_matching():
    with open(PROCESSED_IMAGES_PATH, "r", encoding="utf-8") as f:
        images = json.load(f)

    with open(POSTS_PATH, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print("Generating/loading enriched image embeddings...")
    embeddings_changed = False

    for img in images:
        if "embedding" not in img or len(img.get("embedding", [])) == 0:
            rich_text = f"Subject: {img['subject']}. Caption: {img['caption']}. Attributes: {', '.join(img['attributes'])}"
            img["embedding"] = get_embedding(rich_text)
            embeddings_changed = True

    if embeddings_changed:
        with open(PROCESSED_IMAGES_PATH, "w", encoding="utf-8") as f:
            json.dump(images, f, indent=2)
            print("Saved new embeddings to JSON cache.")

    for post in posts:
        print(f"\n==========================================")
        print(f"Article: \"{post['title']}\"")
        post_text = f"{post['title']}: {post['content']}"
        post_vector = get_embedding(post_text)

        scored_candidates = []
        for img in images:
            score = cosine_similarity(post_vector, img["embedding"])
            scored_candidates.append((score, img))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        top_score, top_img = scored_candidates[0]
        approved, reason = mismatch_guard(post, top_img, top_score)

        print(f"Top Candidate: {top_img['filename']} (Subject: '{top_img['subject']}')")
        print(f"Similarity Score: {top_score:.4f}")
        print(f"Mismatch Guard Status: {'APPROVED' if approved else 'REJECTED'}")
        print(f"Reason: {reason}")


    print(f"\n==========================================")
    print("DEMO: Forcing a Wolf image on the Red Fox article...")
    fox_post = posts[0]

    wolf_img = next(img for img in images if "wolve" in img["filename"].lower())

    fox_vector = get_embedding(fox_post["title"] + ": " + fox_post["content"])
    forced_score = cosine_similarity(fox_vector, wolf_img["embedding"])

    if forced_score < SIMILARITY_THRESHOLD:
        forced_score = SIMILARITY_THRESHOLD + 0.1

    approved, reason = mismatch_guard(fox_post, wolf_img, forced_score)
    print(f"Forced Candidate: {wolf_img['filename']} (Subject: '{wolf_img['subject']}')")
    print(f"Mismatch Guard Status: {'APPROVED' if approved else 'REJECTED'}")
    print(f"Reason: {reason}")
    print(f"==========================================")


if __name__ == "__main__":
    run_matching()