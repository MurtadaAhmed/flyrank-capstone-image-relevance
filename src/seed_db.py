import json
from database import SessionLocal, ImageRecord, PostRecord

PROCESSED_IMAGES_PATH = "../data/processed_images.json"
POSTS_PATH = "../data/posts.json"

def seed_database():
    db = SessionLocal()
    print("Loading images into the database...")
    with open(PROCESSED_IMAGES_PATH, "r", encoding="utf-8") as f:
        image_data = json.load(f)
    for img in image_data:
        existing = db.query(ImageRecord).filter(ImageRecord.filename == img['filename']).first()
        if not existing:
            db_image = ImageRecord(
                filename=img["filename"],
                subject=img["subject"],
                caption=img["caption"],
                metadata_tags={"category": img["category"], "attributes": img["attributes"]},
                confidence=img["confidence"],
                embedding=img.get("embedding", [])
            )
            db.add(db_image)
    print("Finished loading images into the database.")

    print("Loading posts into the database...")
    with open(POSTS_PATH, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    for post in posts_data:
        existing = db.query(PostRecord).filter(PostRecord.post_id_string == post['id']).first()
        if not existing:
            db_post = PostRecord(
                post_id_string=post["id"],
                title=post["title"],
                content=post["content"]
            )
            db.add(db_post)
    print("Finished adding posts into the database.")

    db.commit()
    db.close()
    print("Database successfully seeded.")

if __name__ == "__main__":
    seed_database()