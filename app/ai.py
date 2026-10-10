"""AI auto-tagging: Amazon Rekognition for photos, Amazon Comprehend for documents."""
import io
import os
import re
from collections import Counter

import boto3
from pypdf import PdfReader

REGION = os.environ.get("AWS_REGION", "us-east-1")
MAX_TAGS = 8
IMAGE_TYPES = (".jpg", ".jpeg", ".png")
TEXT_TYPES = (".pdf", ".txt", ".md", ".csv")
LEADING_WORDS = re.compile(r"^(the|a|an|this|that|these|those|my|our|your)\s+", re.IGNORECASE)


def auto_tags(filename, data):
    """Return up to MAX_TAGS tags for a file. Returns [] if the type isn't supported or AI fails."""
    name = filename.lower()
    try:
        if name.endswith(IMAGE_TYPES) and len(data) <= 5 * 1024 * 1024:  # Rekognition limit
            return image_tags(data)
        if name.endswith(TEXT_TYPES):
            return text_tags(extract_text(name, data))
    except Exception as error:  # AI is a bonus: never let it break an upload
        print(f"auto_tags failed for {filename}: {error}")
    return []


def image_tags(data):
    rekognition = boto3.client("rekognition", region_name=REGION)
    labels = rekognition.detect_labels(Image={"Bytes": data}, MaxLabels=MAX_TAGS, MinConfidence=80)["Labels"]
    return [label["Name"] for label in labels]


def extract_text(name, data):
    if name.endswith(".pdf"):
        pages = PdfReader(io.BytesIO(data)).pages[:5]
        text = " ".join(page.extract_text() or "" for page in pages)
    else:
        text = data.decode("utf-8", errors="ignore")
    return text.encode("utf-8")[:4500].decode("utf-8", errors="ignore")  # keep Comprehend calls small


def text_tags(text):
    if not text.strip():
        return []
    comprehend = boto3.client("comprehend", region_name=REGION)
    phrases = comprehend.detect_key_phrases(Text=text, LanguageCode="en")["KeyPhrases"]

    # The phrases that appear most often make the best tags.
    counts, first_seen = Counter(), {}
    for p in phrases:
        phrase = LEADING_WORDS.sub("", p["Text"]).strip()
        if len(phrase) > 2:
            counts[phrase.lower()] += 1
            first_seen.setdefault(phrase.lower(), phrase)
    return [first_seen[key] for key, _ in counts.most_common(MAX_TAGS)]
