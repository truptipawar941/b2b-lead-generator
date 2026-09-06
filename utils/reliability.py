# ==========================================
# LEAD RELIABILITY SCORE
# ==========================================

def calculate_reliability(lead):

    score = 0


    # --------------------------------------
    # Business information
    # --------------------------------------

    if lead.get("business_name"):
        score += 20


    # --------------------------------------
    # Phone
    # --------------------------------------

    if lead.get("phone"):
        score += 20


    # --------------------------------------
    # Website
    # --------------------------------------

    if lead.get("website"):
        score += 15


    # --------------------------------------
    # Email
    # --------------------------------------

    if lead.get("email"):
        score += 15


    # --------------------------------------
    # Social media
    # --------------------------------------

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


    # --------------------------------------
    # Rating / Reviews
    # --------------------------------------

    if (
        lead.get("rating")
        or lead.get("review_count")
    ):
        score += 5


    # --------------------------------------
    # Google Maps
    # --------------------------------------

    if (
        lead.get("google_maps_link")
        or lead.get("maps_search_link")
    ):
        score += 5


    # --------------------------------------
    # Website reachable
    #
    # This will be updated later
    # by the enrichment system.
    # --------------------------------------

    if lead.get("website_reachable"):
        score += 15


    # --------------------------------------
    # Reliability label
    # --------------------------------------

    if score >= 80:

        status = "HIGH"

    elif score >= 50:

        status = "MEDIUM"

    else:

        status = "LOW"


    # --------------------------------------
    # Missing information
    # --------------------------------------

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