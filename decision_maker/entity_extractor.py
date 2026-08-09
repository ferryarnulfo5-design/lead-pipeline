import logging
import spacy

logger = logging.getLogger(__name__)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spacy model missing")
    nlp = None

TITLES = ["CEO", "Chief Executive Officer", "Founder", "Co-Founder", "Owner",
          "President", "Managing Director", "General Manager", "Principal"]

def extract_decision_makers(pages: list, max_people: int = 5) -> list:
    if nlp is None:
        return []
    people = {}
    for page in pages:
        text = page.get("text", "")
        if not text:
            continue
        for ent in nlp(text).ents:
            if ent.label_ != "PERSON" or len(ent.text.split()) < 2:
                continue
            name = " ".join(ent.text.split())
            window = text[max(0, ent.start_char - 60): ent.end_char + 60].lower()
            title = next((t for t in TITLES if t.lower() in window), None)
            if name not in people:
                people[name] = {"name": name, "title": title or "unknown", "source_url": page.get("url")}
            elif title and people[name]["title"] == "unknown":
                people[name]["title"] = title
    return list(people.values())[:max_people]
