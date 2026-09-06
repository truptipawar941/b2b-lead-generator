import requests
import re
import time


# ==========================================
# OVERPASS SERVERS
# ==========================================

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter"
]


HEADERS = {
    "User-Agent": "B2B-Lead-Generator/1.0"
}


# ==========================================
# BUSINESS CATEGORY TAGS
# ==========================================

CATEGORY_TAGS = {

    "dentist": [
        '["amenity"="dentist"]',
        '["healthcare"="dentist"]',
        '["healthcare"="centre"]["healthcare:speciality"~"dent",i]',
        '["healthcare"="clinic"]["healthcare:speciality"~"dent",i]',
        '["healthcare:speciality"~"dent",i]'
    ],

    "dental": [
        '["amenity"="dentist"]',
        '["healthcare"="dentist"]',
        '["healthcare"="centre"]["healthcare:speciality"~"dent",i]',
        '["healthcare"="clinic"]["healthcare:speciality"~"dent",i]',
        '["healthcare:speciality"~"dent",i]'
    ],

    "doctor": [
        '["amenity"="doctors"]',
        '["healthcare"="doctor"]'
    ],

    "clinic": [
        '["amenity"="clinic"]',
        '["healthcare"="clinic"]'
    ],

    "hospital": [
        '["amenity"="hospital"]',
        '["healthcare"="hospital"]'
    ],

    "pharmacy": [
        '["amenity"="pharmacy"]'
    ],

    "restaurant": [
        '["amenity"="restaurant"]'
    ],

    "cafe": [
        '["amenity"="cafe"]'
    ],

    "hotel": [
        '["tourism"="hotel"]'
    ],

    "school": [
        '["amenity"="school"]'
    ],

    "college": [
        '["amenity"="college"]'
    ],

    "bank": [
        '["amenity"="bank"]'
    ],

    "gym": [
        '["leisure"="fitness_centre"]'
    ],

    "fitness": [
        '["leisure"="fitness_centre"]'
    ],

    "salon": [
        '["shop"="hairdresser"]'
    ],

    "supermarket": [
        '["shop"="supermarket"]'
    ],

    "bakery": [
        '["shop"="bakery"]'
    ],

    "clothing": [
        '["shop"="clothes"]'
    ],

    "electronics": [
        '["shop"="electronics"]'
    ],

    "car dealer": [
        '["shop"="car"]'
    ],

    "automobile": [
        '["shop"="car"]'
    ],

    "real estate": [
        '["office"="estate_agent"]'
    ]
}


# ==========================================
# GET CATEGORY FILTERS
# ==========================================

def get_tag_filters(keyword):

    keyword_lower = keyword.lower().strip()

    # Exact category
    if keyword_lower in CATEGORY_TAGS:

        return CATEGORY_TAGS[keyword_lower]

    # Partial category
    for category, tags in CATEGORY_TAGS.items():

        if category in keyword_lower:

            return tags

    # Generic name search
    safe_keyword = re.escape(keyword)

    return [
        f'["name"~"{safe_keyword}",i]'
    ]


# ==========================================
# GET FIRST AVAILABLE TAG
# ==========================================

def first_tag(tags, keys):

    for key in keys:

        value = tags.get(key)

        if value is not None:

            value = str(value).strip()

            if value:

                return value

    return ""


# ==========================================
# NORMALIZE TEXT
# Used for better deduplication
# ==========================================

def normalize_text(value):

    value = str(value or "").lower().strip()

    # Normalize spaces
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Remove punctuation
    value = re.sub(
        r"[^\w\s]",
        "",
        value
    )

    return value


# ==========================================
# CLEAN PHONE
# ==========================================

def clean_phone(phone):

    if not phone:

        return ""

    phone = str(phone).strip()

    # Normalize whitespace
    phone = re.sub(
        r"\s+",
        " ",
        phone
    )

    # Normalize multiple phone separators
    phone = phone.replace(
        ";",
        " / "
    )

    phone = phone.replace(
        "|",
        " / "
    )

    # Remove unnecessary separators
    phone = phone.strip(
        " /,-"
    )

    return phone


# ==========================================
# BUILD ADDRESS
# ==========================================

def build_address(
    tags,
    city
):

    # ======================================
    # FULL ADDRESS
    # ======================================

    full_address = first_tag(

        tags,

        [
            "addr:full",
            "address",
            "contact:address"
        ]

    )

    if full_address:

        return full_address


    # ======================================
    # ADDRESS PARTS
    # ======================================

    address_parts = [

        first_tag(
            tags,
            [
                "addr:housenumber"
            ]
        ),

        first_tag(
            tags,
            [
                "addr:street",
                "addr:place"
            ]
        ),

        first_tag(
            tags,
            [
                "addr:suburb",
                "addr:neighbourhood"
            ]
        ),

        first_tag(
            tags,
            [
                "addr:district",
                "addr:county"
            ]
        ),

        first_tag(
            tags,
            [
                "addr:city",
                "addr:town",
                "addr:village"
            ]
        ),

        first_tag(
            tags,
            [
                "addr:postcode",
                "postal_code"
            ]
        )

    ]


    # Remove empty values
    address_parts = [

        part.strip()

        for part in address_parts

        if part and part.strip()

    ]


    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_parts = []

    seen_parts = set()

    for part in address_parts:

        key = normalize_text(part)

        if key not in seen_parts:

            unique_parts.append(
                part
            )

            seen_parts.add(
                key
            )


    address = ", ".join(
        unique_parts
    )


    # ======================================
    # ADD CITY
    # ======================================

    if address:

        if city.lower() not in address.lower():

            address = (
                f"{address}, {city}"
            )

    else:

        address = city


    return address


# ==========================================
# PROCESS API RESULTS
# ==========================================

def process_results(
    data,
    keyword,
    city,
    limit=None
):

    leads = []

    seen = set()


    for element in data.get(
        "elements",
        []
    ):

        tags = element.get(
            "tags",
            {}
        )


        # ==================================
        # BUSINESS NAME
        # ==================================

        name = first_tag(

            tags,

            [
                "name",
                "official_name",
                "short_name"
            ]

        )


        # Skip unnamed records
        if not name:

            continue


        name = name.strip()


        # ==================================
        # ADDRESS
        # ==================================

        address = build_address(

            tags,

            city

        )


        # ==================================
        # PHONE
        # ==================================

        phone = clean_phone(

            first_tag(

                tags,

                [
                    "phone",
                    "contact:phone",
                    "phone:mobile",
                    "mobile",
                    "contact:mobile",
                    "contact:phone:mobile",
                    "contact:phone:work",
                    "contact:phone:home",
                    "telephone",
                    "contact:telephone",
                    "phone:office",
                    "contact:phone:office"
                ]

            )

        )


        # ==================================
        # WEBSITE
        # ==================================

        website = first_tag(

            tags,

            [
                "website",
                "contact:website",
                "url"
            ]

        )


        # ==================================
        # EMAIL
        # ==================================

        email = first_tag(

            tags,

            [
                "email",
                "contact:email"
            ]

        )


        # ==================================
        # CITY
        # ==================================

        business_city = first_tag(

            tags,

            [
                "addr:city",
                "addr:town",
                "addr:village",
                "addr:district"
            ]

        )


        if not business_city:

            business_city = city


        # ==================================
        # PINCODE
        # ==================================

        pincode = first_tag(

            tags,

            [
                "addr:postcode",
                "postal_code"
            ]

        )


        # ==================================
        # COORDINATES
        # ==================================

        latitude = element.get(
            "lat"
        )

        longitude = element.get(
            "lon"
        )


        # Way / relation
        if latitude is None:

            center = element.get(
                "center",
                {}
            )

            latitude = center.get(
                "lat"
            )

            longitude = center.get(
                "lon"
            )


        # ==================================
        # DEDUPLICATION
        # ==================================

        unique_key = (

            normalize_text(name),

            normalize_text(address),

            normalize_text(phone)

        )


        if unique_key in seen:

            continue


        seen.add(
            unique_key
        )


        # ==================================
        # CREATE LEAD
        # ==================================

        lead = {

            "business_name":
                name,

            "category":
                keyword,

            "address":
                address,

            "city":
                business_city,

            "pincode":
                pincode,

            "phone":
                phone,

            "website":
                website,

            "email":
                email,

            "rating":
                "",

            "review_count":
                "",

            "google_maps_link":
                "",

            "latitude":
                latitude,

            "longitude":
                longitude

        }


        leads.append(
            lead
        )


        # ==================================
        # LIMIT
        # ==================================

        if limit is not None:

            if len(leads) >= limit:

                break


    return leads


# ==========================================
# EXECUTE OVERPASS
# ==========================================

def execute_overpass(
    query,
    keyword,
    city,
    limit=None
):

    for server in OVERPASS_SERVERS:

        for attempt in range(2):

            try:

                print(
                    f"Trying server: {server}"
                )

                print(
                    f"Attempt: {attempt + 1}"
                )


                response = requests.post(

                    server,

                    data=query,

                    headers=HEADERS,

                    timeout=30

                )


                response.raise_for_status()


                data = response.json()


                leads = process_results(

                    data,

                    keyword,

                    city,

                    limit

                )


                print(

                    f"Found {len(leads)} businesses"

                )


                return leads


            except requests.RequestException as error:

                print(
                    f"Server failed: {server}"
                )

                print(error)


                if attempt == 0:

                    print(
                        "Retrying..."
                    )

                    time.sleep(2)

                else:

                    print(
                        "Trying next server..."
                    )


            except ValueError as error:

                print(
                    "Invalid JSON response:"
                )

                print(error)

                break


    print(
        "All Overpass servers failed."
    )

    return []


# ==========================================
# SEARCH BY BOUNDING BOX
# ==========================================

def search_by_bbox(
    keyword,
    city,
    bbox,
    limit=None
):

    south, west, north, east = bbox


    tag_filters = get_tag_filters(
        keyword
    )


    filters = "\n".join(

        f"nwr{tag}"
        f"({south},{west},{north},{east});"

        for tag in tag_filters

    )


    query = f"""
    [out:json][timeout:30];

    (
        {filters}
    );

    out center tags;
    """


    return execute_overpass(

        query,

        keyword,

        city,

        limit

    )


# ==========================================
# CITY BOUNDING BOXES
# ==========================================

CITY_BBOXES = {

    "pune": (
        18.20,
        73.50,
        18.80,
        74.30
    ),

    "mumbai": (
        18.85,
        72.75,
        19.35,
        73.15
    ),

    "delhi": (
        28.40,
        76.80,
        28.90,
        77.35
    ),

    "solapur": (
        17.55,
        75.70,
        17.85,
        76.10
    ),

    "nashik": (
        19.85,
        73.65,
        20.15,
        74.00
    ),

    "bangalore": (
        12.80,
        77.35,
        13.25,
        77.85
    ),

    "bengaluru": (
        12.80,
        77.35,
        13.25,
        77.85
    ),

    "hyderabad": (
        17.20,
        78.20,
        17.65,
        78.70
    ),

    "chennai": (
        12.80,
        80.00,
        13.25,
        80.40
    ),

    "kolkata": (
        22.35,
        88.20,
        22.80,
        88.60
    ),

    "ahmedabad": (
        22.90,
        72.35,
        23.20,
        72.75
    ),

    "nagpur": (
        20.90,
        78.95,
        21.35,
        79.35
    ),

    "jaipur": (
        26.70,
        75.55,
        27.05,
        76.00
    ),

    "surat": (
        21.05,
        72.65,
        21.35,
        73.05
    ),

    "indore": (
        22.55,
        75.65,
        23.00,
        76.05
    )
}


# ==========================================
# MAIN SEARCH FUNCTION
# ==========================================

def search_businesses(
    keyword,
    city,
    limit=100
):

    keyword = str(
        keyword or ""
    ).strip()


    city = str(
        city or ""
    ).strip()


    if not keyword or not city:

        return []


    # ======================================
    # VALIDATE LIMIT
    # ======================================

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError
    ):

        limit = 100


    if limit <= 0:

        limit = 100


    print(

        f"Searching {keyword} "
        f"in {city} "
        f"(limit={limit})..."

    )


    city_key = city.lower()


    # ======================================
    # KNOWN CITY
    # SINGLE FAST QUERY
    # ======================================

    if city_key in CITY_BBOXES:

        leads = search_by_bbox(

            keyword,

            city,

            CITY_BBOXES[
                city_key
            ],

            limit

        )


        if leads:

            print(

                f"Final search results: "
                f"{len(leads)}"

            )


            return leads


    # ======================================
    # AUTOMATIC CITY SEARCH
    # ======================================

    print(

        f"Trying automatic area search "
        f"for {city}..."

    )


    tag_filters = get_tag_filters(
        keyword
    )


    filters = "\n".join(

        f'nwr{tag}(area.searchArea);'

        for tag in tag_filters

    )


    safe_city = re.escape(
        city
    )


    query = f"""
    [out:json][timeout:30];

    area[
        "name"~"^{safe_city}$",
        i
    ]["boundary"="administrative"]
    ->.searchArea;

    (
        {filters}
    );

    out center tags;
    """


    leads = execute_overpass(

        query,

        keyword,

        city,

        limit

    )


    print(

        f"Final search results: "
        f"{len(leads)}"

    )


    return leads