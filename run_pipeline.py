import argparse, csv, logging, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

from models.lead import CandidateLead
from crawler.spider import crawl_website
from decision_maker.entity_extractor import extract_decision_makers
from linkedin.search import find_linkedin_candidates
from linkedin.identity_match import score_candidate
from emailing.extractor import extract_emails
from emailing.pattern_generator import infer_pattern, generate_candidates
from scoring.confidence import check_mx, classify_email, final_confidence

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
JUNK_DOMAINS = {"schema.org", "linktr.ee", "brand.site", "webnode.com", "localo.site", "wixsite.com", "godaddysites.com"}
_lock = threading.Lock()

def domain_of(url):
    return url.split("//")[-1].split("/")[0].lower().replace("www.", "").strip()

def load_input(path):
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", sep=None, engine="python")
    df.columns = [str(c).strip().lower() for c in df.columns]
    nc = "name" if "name" in df.columns else df.columns[0]
    wc = "website" if "website" in df.columns else df.columns[1]
    return df[[nc, wc]].rename(columns={nc: "name", wc: "website"})

def process_site(name, website):
    lead = CandidateLead(business_name=name, website=website, domain=domain_of(website))
    try:
        pages = crawl_website(website)
        lead.crawl_ok = bool(pages)
        observed = extract_emails(pages)
        lead.mx_valid = check_mx(lead.domain)

        # শুধু টাইটেল-সহ ব্যক্তিই বিশ্বাসযোগ্য (ভুয়া নাম বাদ)
        people = extract_decision_makers(pages)
        person = next((p for p in people if p["title"] != "unknown"), None)
        if person:
            lead.person_name, lead.person_title = person["name"], person["title"]

        # LinkedIn: ৭৫+ = qualified, ৬৫+ = NEEDS_REVIEW (ম্যানুয়াল চেক)
        best, review = None, None
        for cand in find_linkedin_candidates(name, lead.domain):
            sc, ev, ok = score_candidate(name, lead.domain, lead.person_name, cand["snippet"], cand["url"])
            if ok and (best is None or sc > best[0]):
                best = (sc, ev, cand["url"])
            elif not ok and sc >= 65 and (review is None or sc > review[0]):
                review = (sc, ev + ["NEEDS_REVIEW"], cand["url"])
        if best:
            lead.linkedin_match_score, lead.linkedin_match_evidence, lead.linkedin_url = best
        elif review:
            lead.linkedin_match_score, lead.linkedin_match_evidence, lead.linkedin_url = review

        # ইমেইল: আগে সাইট থেকে পাওয়া নিজস্ব মেইল, নাহলে pattern (শুধু trusted person-এর জন্য)
        own = [e for e in observed if e.endswith("@" + lead.domain)]
        if own:
            lead.email, lead.email_source, lead.email_candidates = own[0], "website_scrape", own
        elif lead.person_name:
            cands = generate_candidates(lead.person_name, lead.domain)
            method = infer_pattern(lead.person_name, observed)
            if method:
                cands = [(m, e) for m, e in cands if m == method] + cands
            lead.email_candidates = [e for _, e in cands]
            if lead.email_candidates:
                lead.email, lead.email_source = lead.email_candidates[0], "pattern_generated"
                lead.email_generation_method = cands[0][0]

        lead.email_status = classify_email(lead.email, lead.email_source, lead.mx_valid)
        lead.email_confidence = final_confidence(lead.linkedin_match_score, lead.email_status, lead.email_source)
    except Exception as e:
        logger.error(f"{name}: {e}")
        lead.error = str(e)
    return lead

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="input/pilot_50.csv")
    ap.add_argument("--output", default="output/candidates.csv")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    df = load_input(args.input)
    tasks, seen = [], set()
    for _, row in df.iterrows():
        web = str(row["website"]).strip()
        if not web or web == "nan":
            continue
        if not web.startswith("http"):
            web = "https://" + web
        dom = domain_of(web)
        if dom in seen or dom in JUNK_DOMAINS:
            continue
        seen.add(dom)
        tasks.append((str(row["name"]).strip(), web))

    Path("output").mkdir(exist_ok=True)
    fields = list(CandidateLead.model_fields.keys())
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields).writeheader()

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for fut in as_completed([ex.submit(process_site, n, w) for n, w in tasks]):
            lead = fut.result()
            row = lead.model_dump(mode="json")
            row["linkedin_match_evidence"] = ",".join(row["linkedin_match_evidence"])
            row["email_candidates"] = ";".join(row["email_candidates"])
            with _lock:
                with open(args.output, "a", newline="", encoding="utf-8") as f:
                    csv.DictWriter(f, fieldnames=fields).writerow(row)
            done += 1
            logger.info(f"[{done}/{len(tasks)}] {lead.business_name} | li={lead.linkedin_match_score} | {lead.email_status.value} | {lead.email_confidence.value}")
    logger.info(f"Done -> {args.output}")

if __name__ == "__main__":
    main()
