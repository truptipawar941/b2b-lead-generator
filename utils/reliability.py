def calculate_reliability(lead):

    score = 0

    if lead.get("business_name"):
        score += 20

    if lead.get("phone"):
        score += 20

    if lead.get("website"):
        score += 15

    if lead.get("email"):
        score += 15

    social_profiles = 0

    if lead.get("facebook"):
        social_profiles += 1

    if lead.get("instagram"):
        social_profiles += 1

    if lead.get("linkedin"):
        social_profiles += 1

    if lead.get("twitter"):
        social_profiles += 1

    if social_profiles > 0:
        score += 5

    if (
        lead.get("rating")
        or lead.get("review_count")
    ):
        score += 5

    if (
        lead.get("google_maps_link")
        or lead.get("maps_search_link")
    ):
        score += 5

    if lead.get("website_reachable"):
        score += 15

    if score >= 80:

        status = "HIGH"

    elif score >= 50:

        status = "MEDIUM"

    else:

        status = "LOW"

    missing = []

    if not lead.get("phone"):
        missing.append("Phone")

    if not lead.get("website"):
        missing.append("Website")

    if not lead.get("email"):
        missing.append("Email")

    if not (
        lead.get("facebook")
        or lead.get("instagram")
        or lead.get("linkedin")
        or lead.get("twitter")
    ):
        missing.append("Social")

    return {
        "score": score,
        "status": status,
        "missing": missing
    }