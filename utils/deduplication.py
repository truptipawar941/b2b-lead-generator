import re


def normalize_text(value):

    if not value:
        return ""

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = re.sub(
        r"[^\w\s]",
        "",
        value
    )

    return value


def normalize_phone(phone):

    if not phone:
        return ""

    return re.sub(
        r"\D",
        "",
        str(phone)
    )


def deduplicate_leads(leads):

    unique_leads = []

    seen_place_ids = set()
    seen_businesses = set()
    seen_phone_numbers = set()

    for lead in leads:

        place_id = str(
            lead.get("place_id", "")
        ).strip()

        business_name = normalize_text(
            lead.get("business_name", "")
        )

        address = normalize_text(
            lead.get("address", "")
        )

        phone = normalize_phone(
            lead.get("phone", "")
        )

        if place_id:

            if place_id in seen_place_ids:
                continue

            seen_place_ids.add(
                place_id
            )

        business_key = (
            business_name,
            address
        )

        if business_name and address:

            if business_key in seen_businesses:
                continue

            seen_businesses.add(
                business_key
            )

        if phone:

            if phone in seen_phone_numbers:
                continue

            seen_phone_numbers.add(
                phone
            )

        unique_leads.append(
            lead
        )

    print(
        f"Before deduplication: {len(leads)}"
    )

    print(
        f"After deduplication: {len(unique_leads)}"
    )

    return unique_leads