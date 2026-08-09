def infer_pattern(full_name, observed_emails):
    parts = full_name.lower().split()
    if len(parts) < 2:
        return ""
    first, last = parts[0], parts[-1]
    table = {"first.last": f"{first}.{last}", "firstlast": f"{first}{last}",
             "flast": f"{first[0]}{last}", "firstl": f"{first}{last[0]}", "first": first}
    for em in observed_emails:
        local = em.split("@")[0]
        for method, pat in table.items():
            if local == pat:
                return method
    return ""

def generate_candidates(full_name, domain):
    parts = full_name.lower().split()
    if len(parts) < 2:
        return []
    first, last = parts[0], parts[-1]
    return [("first.last", f"{first}.{last}@{domain}"), ("firstlast", f"{first}{last}@{domain}"),
            ("flast", f"{first[0]}{last}@{domain}"), ("firstl", f"{first}{last[0]}@{domain}"),
            ("first", f"{first}@{domain}")]
