import re

import requests

import time

from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse, quote_plus


HEADERS = {

    "User-Agent": (

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "

        "AppleWebKit/537.36 (KHTML, like Gecko) "

        "Chrome/131.0.0.0 Safari/537.36"

    )

}

TIMEOUT = 8


def normalize_url(url):

    if not url:

        return ""

    url = url.strip()

    if not url:

        return ""

    if not url.startswith(("http://", "https://")):

        url = "https://" + url

    return url


def clean_email(email):

    if not email:

        return ""

    email = email.strip().lower()

    email = email.rstrip(".,;:)]}")

    return email


def extract_emails(text):

    if not text:

        return []

    pattern = (

        r"[A-Za-z0-9._%+-]+"

        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    )

    emails = re.findall(pattern, text)

    cleaned = []

    for email in emails:

        email = clean_email(email)

        if email and email not in cleaned:

            cleaned.append(email)

    return cleaned


def normalize_phone(phone):

    if not phone:

        return ""

    phone = phone.strip()

    phone = phone.strip(".,;:()[]{}")

    return phone


def extract_phones(text):

    if not text:

        return []

    patterns = [

        r"(?:\+91[\s\-\.]?)?[6-9]\d{9}",

        r"(?:\+91[\s\-\.]?)?[6-9]\d{4}[\s\-\.]?\d{5}",

        r"(?:\+91[\s\-\.]?)?\(?0\d{2,4}\)?[\s\-\.]?\d{6,8}"

    ]

    phones = []

    for pattern in patterns:

        matches = re.findall(pattern, text)

        for phone in matches:

            phone = normalize_phone(phone)

            if phone and phone not in phones:

                phones.append(phone)

    return phones


def extract_social_links(soup):

    social = {

        "instagram": "",

        "facebook": "",

        "linkedin": "",

        "twitter": ""

    }

    if not soup:

        return social

    for link in soup.find_all("a", href=True):

        href = link.get("href", "").strip()

        if not href:

            continue

        lower_href = href.lower()

        if "instagram.com" in lower_href:

            social["instagram"] = href

        elif "facebook.com" in lower_href:

            social["facebook"] = href

        elif "linkedin.com" in lower_href:

            social["linkedin"] = href

        elif (

            "twitter.com" in lower_href

            or "x.com" in lower_href

        ):

            social["twitter"] = href

    return social


def extract_contact_links(soup, base_url):

    if not soup:

        return []

    contact_links = []

    base_domain = urlparse(base_url).netloc

    keywords = [

        "contact",

        "contact-us",

        "contactus",

        "about",

        "reach-us",

        "reachus"

    ]

    for link in soup.find_all("a", href=True):

        href = link.get("href", "").strip()

        if not href:

            continue

        full_url = urljoin(base_url, href)

        parsed = urlparse(full_url)

        if parsed.netloc != base_domain:

            continue

        combined_text = (

            link.get_text(" ", strip=True)

            + " "

            + href

        ).lower()

        if any(

            keyword in combined_text

            for keyword in keywords

        ):

            if full_url not in contact_links:

                contact_links.append(full_url)

        if len(contact_links) >= 5:

            break

    return contact_links


def extract_direct_contact_links(soup):

    emails = []

    phones = []

    if not soup:

        return emails, phones

    for link in soup.find_all("a", href=True):

        href = link.get("href", "").strip()

        lower_href = href.lower()

        if lower_href.startswith("mailto:"):

            email = href[7:].split("?")[0]

            email = clean_email(email)

            if email and email not in emails:

                emails.append(email)

        elif lower_href.startswith("tel:"):

            phone = href[4:].split("?")[0]

            phone = normalize_phone(phone)

            if phone and phone not in phones:

                phones.append(phone)

    return emails, phones


def scrape_page(url):

    result = {

        "email": "",

        "phone": "",

        "instagram": "",

        "facebook": "",

        "linkedin": "",

        "twitter": ""

    }

    url = normalize_url(url)

    if not url:

        return result

    visited_pages = []

    pages_to_visit = [url]

    try:

        while pages_to_visit and len(visited_pages) < 6:

            current_url = pages_to_visit.pop(0)

            if current_url in visited_pages:

                continue

            visited_pages.append(current_url)

            try:

                response = requests.get(

                    current_url,

                    headers=HEADERS,

                    timeout=TIMEOUT

                )

                if response.status_code != 200:

                    continue

                soup = BeautifulSoup(

                    response.text,

                    "html.parser"

                )

                text = soup.get_text(

                    " ",

                    strip=True

                )

                if not result["email"]:

                    emails = extract_emails(text)

                    if emails:

                        result["email"] = emails[0]

                if not result["phone"]:

                    phones = extract_phones(text)

                    if phones:

                        result["phone"] = phones[0]

                direct_emails, direct_phones = (

                    extract_direct_contact_links(soup)

                )

                if (

                    not result["email"]

                    and direct_emails

                ):

                    result["email"] = direct_emails[0]

                if (

                    not result["phone"]

                    and direct_phones

                ):

                    result["phone"] = direct_phones[0]

                social = extract_social_links(soup)

                for key in result:

                    if key in social:

                        if not result[key]:

                            result[key] = social[key]

                if current_url == url:

                    contact_links = extract_contact_links(

                        soup,

                        url

                    )

                    for contact_url in contact_links:

                        if contact_url not in visited_pages:

                            pages_to_visit.append(

                                contact_url

                            )

            except Exception:

                continue

    except Exception:

        pass

    return result


EXCLUDED_DOMAINS = [

    "google.com",

    "google.co.in",

    "googleusercontent.com",

    "facebook.com",

    "instagram.com",

    "linkedin.com",

    "twitter.com",

    "x.com",

    "youtube.com",

    "justdial.com",

    "sulekha.com",

    "practo.com",

    "lybrate.com",

    "nearby.com",

    "yelp.com",

    "tripadvisor.com",

    "mappls.com",

    "apneareamein.com",

    "magicpin.in",

    "asklaila.com",

    "indiamart.com",

    "urbanpro.com",

    "yellowpages.in",

    "tradeindia.com"

]


def is_excluded_domain(url):

    try:

        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        for excluded in EXCLUDED_DOMAINS:

            if (

                domain == excluded

                or domain.endswith("." + excluded)

            ):

                return True

    except Exception:

        return True

    return False


def score_website_candidate(

    url,

    business_name,

    city="",

    phone=""

):

    try:

        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        if domain.startswith("www."):

            domain = domain[4:]

        path = parsed.path.lower()

        full_text = domain + " " + path

        score = 0

        business_words = re.findall(

            r"[a-zA-Z0-9]+",

            business_name.lower()

        )

        important_words = [

            word

            for word in business_words

            if len(word) >= 4

        ]

        for word in important_words:

            if word in full_text:

                score += 1

        if city:

            city_clean = re.sub(

                r"[^a-zA-Z0-9]",

                "",

                city.lower()

            )

            domain_clean = re.sub(

                r"[^a-zA-Z0-9]",

                "",

                full_text

            )

            if (

                city_clean

                and city_clean in domain_clean

            ):

                score += 1

        if phone:

            phone_digits = re.sub(

                r"\D",

                "",

                phone

            )

            url_digits = re.sub(

                r"\D",

                "",

                url

            )

            if (

                phone_digits

                and len(phone_digits) >= 6

                and phone_digits in url_digits

            ):

                score += 2

        return score

    except Exception:

        return 0


def discover_website(

    business_name,

    city="",

    phone="",

    address=""

):

    print(

        f"Discovering website: "

        f"{business_name} - {city}"

    )

    queries = [

        f'"{business_name}" {city} website',

        f'"{business_name}" {phone}',

        f'"{business_name}" {address}',

        f'"{business_name}" website'

    ]

    candidates = []

    for query in queries:

        try:

            search_url = (

                "https://html.duckduckgo.com/html/?q="

                + quote_plus(query)

            )

            response = requests.get(

                search_url,

                headers=HEADERS,

                timeout=TIMEOUT

            )

            if response.status_code != 200:

                continue

            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )

            for result in soup.select(".result__a"):

                href = result.get(

                    "href",

                    ""

                ).strip()

                if not href:

                    continue

                href = normalize_url(href)

                if not href:

                    continue

                if is_excluded_domain(href):

                    continue

                if href not in candidates:

                    candidates.append(href)

            time.sleep(0.5)

        except Exception:

            continue

    best_url = ""

    best_score = 0

    for candidate in candidates:

        score = score_website_candidate(

            candidate,

            business_name,

            city,

            phone

        )

        if score > best_score:

            best_score = score

            best_url = candidate

    if best_url and best_score >= 2:

        print(

            f"Website found: {best_url}"

        )

        return best_url

    print(

        f"No website found: {business_name}"

    )

    return ""


def discover_contact_info(

    business_name,

    city="",

    phone="",

    address=""

):

    result = {

        "phone": "",

        "email": ""

    }

    queries = [

        f'"{business_name}" {city} phone',

        f'"{business_name}" {city} contact',

        f'"{business_name}" {city} email',

        f'"{business_name}" {address} phone'

    ]

    for query in queries:

        try:

            search_url = (

                "https://html.duckduckgo.com/html/?q="

                + quote_plus(query)

            )

            response = requests.get(

                search_url,

                headers=HEADERS,

                timeout=TIMEOUT

            )

            if response.status_code != 200:

                continue

            soup = BeautifulSoup(

                response.text,

                "html.parser"

            )

            result_blocks = soup.select(".result")

            text_parts = []

            for block in result_blocks:

                block_text = block.get_text(

                    " ",

                    strip=True

                )

                if block_text:

                    text_parts.append(

                        block_text

                    )

            text = " ".join(text_parts)

            if not result["phone"]:

                phones = extract_phones(text)

                if phones:

                    for p in phones:

                        digits = re.sub(

                            r"\D",

                            "",

                            p

                        )

                        if (

                            len(digits) == 10

                            and digits[0] in "6789"

                        ):

                            result["phone"] = p

                            break

                    if not result["phone"]:

                        result["phone"] = phones[0]

            if not result["email"]:

                emails = extract_emails(text)

                if emails:

                    for email in emails:

                        if not any(

                            bad in email

                            for bad in [

                                "example.com",

                                "domain.com",

                                "email.com"

                            ]

                        ):

                            result["email"] = email

                            break

            if (

                result["phone"]

                and result["email"]

            ):

                break

            time.sleep(0.5)

        except Exception:

            continue

    return result


def enrich_website(url):

    if not url:

        return {

            "email": "",

            "phone": "",

            "instagram": "",

            "facebook": "",

            "linkedin": "",

            "twitter": ""

        }

    print(

        f"Enriching website: {url}"

    )

    data = scrape_page(url)

    print(

        f"Enrichment completed: {url}"

    )

    return data