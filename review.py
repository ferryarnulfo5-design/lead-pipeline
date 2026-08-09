import pandas as pd

df = pd.read_csv("output/candidates.csv")
print("=" * 50)
print("PILOT FUNNEL")
print("=" * 50)
print("total rows:         ", len(df))
print("crawl_ok:           ", f"{df.crawl_ok.mean()*100:.0f}%")
print("person found:       ", f"{df.person_name.notna().mean()*100:.0f}%")
print("linkedin score>=75: ", f"{(df.linkedin_match_score>=75).mean()*100:.0f}%")
print("mx_valid:           ", f"{df.mx_valid.mean()*100:.0f}%")
print("email found:        ", f"{df.email.notna().mean()*100:.0f}%")
print("\nemail_status:\n", df.email_status.value_counts().to_string())
print("\nemail_confidence:\n", df.email_confidence.value_counts().to_string())
