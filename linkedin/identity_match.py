import re

TITLE_WORDS = ["ceo", "owner", "founder", "president", "managing director", "principal"]
STOP = {"llc", "inc", "ltd", "co", "company", "corp", "corporation", "pllc", "llp", "of", "the", "and",
        "tx", "texas", "dallas", "fort", "worth", "dfw", "services", "solutions"}

def _norm(s):
    return re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower())

def _tokens(name):
    return [t for t in _norm(name).split() if t not in STOP and len(t) > 2]

def score_candidate(company_name, domain, person_name, snippet, url):
    s, u = _norm(snippet), _norm(url)
    score, evidence = 0, []

    if person_name:
        if _norm(person_name) in s or _norm(person_name) in u:
            score += 25
            evidence.append("Name_Match")
        else:
            return 0, ["REJECTED_Name_Mismatch"], False

    toks, dom_root = _tokens(company_name), domain.split(".")[0]
    hits = [t for t in toks if t in s or t in u]
    if toks and len(hits) >= max(1, len(toks) // 2):
        score += 40
        evidence.append("Company_Match")
    elif dom_root in s or dom_root in u:
        score += 40
        evidence.append("Domain_Match")
    else:
        return score, evidence, False

    if any(t in s for t in TITLE_WORDS):
        score += 15
        evidence.append("Title_Match")
    if any(l in s for l in ["dallas", "fort worth", "dfw", "texas"]):
        score += 10
        evidence.append("Location_Match")

    return score, evidence, score >= 75
