import os
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


GOOGLE_PLACES_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)


def search_google_places(keyword, city, limit=20):

    if not API_KEY:
        raise ValueError(
            "GOOGLE_MAPS_API_KEY is missing in .env"
        )

    keyword = keyword.strip()
    city = city.strip()

    if not keyword or not city:
        return []

    text_query = f"{keyword} in {city}"

    payload = {
        "textQuery": text_query,
        "pageSize": min(limit, 20),
        "languageCode": "en"
    }

    headers = {

        "Content-Type": "application/json",

        "X-Goog-Api-Key": API_KEY,

        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.nationalPhoneNumber,"
            "places.internationalPhoneNumber,"
            "places.websiteUri,"
            "places.rating,"
            "places.userRatingCount,"
            "places.googleMapsUri,"
            "places.location"
        )
    }

    response = requests.post(
        GOOGLE_PLACES_URL,
        json=payload,
        headers=headers,
        timeout=20
    )

    if not response.ok:

        print(
            "Google Places API error:"
        )

        print(response.text)

        response.raise_for_status()

    data = response.json()

    places = data.get(
        "places",
        []
    )

    leads = []

    for place in places:

        display_name = place.get(
            "displayName",
            {}
        )

        business_name = display_name.get(
            "text",
            ""
        )

        location = place.get(
            "location",
            {}
        )

        phone = place.get(
            "nationalPhoneNumber",
            ""
        )

        if not phone:

            phone = place.get(
                "internationalPhoneNumber",
                ""
            )

        lead = {

            "business_name": business_name,

            "category": keyword,

            "address": place.get(
                "formattedAddress",
                ""
            ),

            "city": city,

            "pincode": "",

            "phone": phone,

            "website": place.get(
                "websiteUri",
                ""
            ),

            "email": "",

            "facebook": "",

            "instagram": "",

            "linkedin": "",

            "twitter": "",

            "rating": place.get(
                "rating",
                ""
            ),

            "review_count": place.get(
                "userRatingCount",
                ""
            ),

            "google_maps_link": place.get(
                "googleMapsUri",
                ""
            ),

            "latitude": location.get(
                "latitude"
            ),

            "longitude": location.get(
                "longitude"
            ),

            "place_id": place.get(
                "id",
                ""
            )
        }

        leads.append(lead)

    print(
        f"Google Places found: {len(leads)}"
    )

    return leads