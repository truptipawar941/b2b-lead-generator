from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file
)

from scraper.business_search import search_businesses

from scraper.website_enricher import (
    enrich_website,
    discover_website,
    discover_contact_info
)

from utils.deduplication import deduplicate_leads
from utils.reliability import calculate_reliability

from database.database import (
    init_database,
    save_leads,
    get_all_leads,
    save_download_history,
    get_download_history
)

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from urllib.parse import quote_plus

import pandas as pd
import io
import uuid
import threading


app = Flask(__name__)


background_executor = ThreadPoolExecutor(
    max_workers=5
)

enrichment_jobs = {}

enrichment_lock = threading.Lock()


@app.route("/")
def home():
    return render_template(
        "index.html"
    )


@app.route("/saved-leads")
def saved_leads_page():
    return render_template(
        "saved_leads.html"
    )


@app.route("/analytics")
def analytics_page():
    return render_template(
        "analytics.html"
    )


@app.route("/download-history")
def download_history_page():
    return render_template(
        "download_history.html"
    )


@app.route("/settings")
def settings_page():
    return render_template(
        "settings.html"
    )


@app.route(
    "/download-history-data",
    methods=["GET"]
)
def download_history_data():

    try:
        history = get_download_history()

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as error:

        print(
            "Download history error:",
            error
        )

        return jsonify({
            "success": False,
            "history": [],
            "message":
                "Unable to load download history."
        }), 500


def build_maps_link(lead):

    business_name = str(
        lead.get(
            "business_name",
            ""
        ) or ""
    ).strip()

    address = str(
        lead.get(
            "address",
            ""
        ) or ""
    ).strip()

    city_name = str(
        lead.get(
            "city",
            ""
        ) or ""
    ).strip()

    search_text = ", ".join(
        part
        for part in [
            business_name,
            address,
            city_name
        ]
        if part
    )

    if not search_text:
        return ""

    return (
        "https://www.google.com/maps/"
        "search/?api=1&query="
        + quote_plus(search_text)
    )


def prepare_lead(lead):

    lead["website_reachable"] = bool(
        lead.get(
            "website_reachable",
            False
        )
    )

    reliability = calculate_reliability(
        lead
    )

    lead["reliability_score"] = (
        reliability["score"]
    )

    lead["reliability_status"] = (
        reliability["status"]
    )

    lead["missing_information"] = (
        ", ".join(
            reliability["missing"]
        )
        if reliability["missing"]
        else "None"
    )

    if not lead.get(
        "google_maps_link"
    ):

        lead["google_maps_link"] = (
            build_maps_link(
                lead
            )
        )

    lead["maps_search_link"] = (
        lead.get(
            "google_maps_link",
            ""
        )
        or build_maps_link(
            lead
        )
    )

    return lead


@app.route(
    "/leads",
    methods=["GET"]
)
def get_saved_leads():

    try:

        leads = get_all_leads()

        keyword_filter = request.args.get(
            "keyword",
            ""
        ).strip().lower()

        city_filter = request.args.get(
            "city",
            ""
        ).strip().lower()

        filtered_leads = []

        for lead in leads:

            business_name = str(
                lead.get(
                    "business_name",
                    ""
                ) or ""
            ).lower()

            category = str(
                lead.get(
                    "category",
                    ""
                ) or ""
            ).lower()

            lead_city = str(
                lead.get(
                    "city",
                    ""
                ) or ""
            ).lower()

            if keyword_filter:

                if (
                    keyword_filter not in business_name
                    and
                    keyword_filter not in category
                ):
                    continue

            if city_filter:

                if city_filter not in lead_city:
                    continue

            filtered_leads.append(
                prepare_lead(
                    lead
                )
            )

        return jsonify({
            "success": True,
            "count": len(
                filtered_leads
            ),
            "leads":
                filtered_leads
        })

    except Exception as error:

        print(
            "Database read error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to load saved leads."
        }), 500


@app.route(
    "/analytics-data",
    methods=["GET"]
)
def analytics_data():

    try:

        leads = get_all_leads()

        total = len(
            leads
        )

        websites = sum(
            1
            for lead in leads
            if str(
                lead.get(
                    "website",
                    ""
                ) or ""
            ).strip()
        )

        emails = sum(
            1
            for lead in leads
            if str(
                lead.get(
                    "email",
                    ""
                ) or ""
            ).strip()
        )

        phones = sum(
            1
            for lead in leads
            if str(
                lead.get(
                    "phone",
                    ""
                ) or ""
            ).strip()
        )

        social = sum(
            1
            for lead in leads
            if (
                lead.get("facebook")
                or
                lead.get("instagram")
                or
                lead.get("linkedin")
                or
                lead.get("twitter")
            )
        )

        ratings = sum(
            1
            for lead in leads
            if lead.get(
                "rating"
            ) not in (
                None,
                "",
                "-"
            )
        )

        reviews = sum(
            1
            for lead in leads
            if lead.get(
                "review_count"
            ) not in (
                None,
                "",
                "-"
            )
        )

        high = 0
        medium = 0
        low = 0

        scores = []

        for lead in leads:

            reliability = calculate_reliability(
                lead
            )

            score = reliability["score"]
            status = reliability["status"]

            scores.append(
                score
            )

            if status == "HIGH":
                high += 1

            elif status == "MEDIUM":
                medium += 1

            else:
                low += 1

        average_reliability = (
            round(
                sum(scores)
                /
                len(scores),
                1
            )
            if scores
            else 0
        )

        return jsonify({
            "success": True,
            "total": total,
            "websites": websites,
            "emails": emails,
            "phones": phones,
            "social": social,
            "ratings": ratings,
            "reviews": reviews,
            "high": high,
            "medium": medium,
            "low": low,
            "average_reliability":
                average_reliability
        })

    except Exception as error:

        print(
            "Analytics error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to load analytics."
        }), 500


def enrich_single_lead(lead):

    website = str(
        lead.get(
            "website",
            ""
        ) or ""
    ).strip()

    business_name = str(
        lead.get(
            "business_name",
            ""
        ) or ""
    ).strip()

    city = str(
        lead.get(
            "city",
            ""
        ) or ""
    ).strip()

    result = {
        "website":
            website,

        "email":
            lead.get(
                "email",
                ""
            ) or "",

        "phone":
            lead.get(
                "phone",
                ""
            ) or "",

        "facebook": "",
        "instagram": "",
        "linkedin": "",
        "twitter": "",

        "website_reachable":
            False
    }

    if not website and business_name:

        try:

            print(
                f"Discovering website: "
                f"{business_name} - {city}"
            )

            discovered_website = (
                discover_website(
                    business_name,
                    city
                )
            )

            if discovered_website:

                website = discovered_website

                result["website"] = (
                    discovered_website
                )

                print(
                    f"Website found: "
                    f"{discovered_website}"
                )

        except Exception as error:

            print(
                "Website discovery error:",
                error
            )

    if not website:

        print(
            f"No website found: "
            f"{business_name}"
        )

        return result

    try:

        print(
            f"Enriching website: "
            f"{website}"
        )

        enrichment = enrich_website(
            website
        )

        if not result["email"]:

            result["email"] = (
                enrichment.get(
                    "email",
                    ""
                ) or ""
            )

        if not result["phone"]:

            result["phone"] = (
                enrichment.get(
                    "phone",
                    ""
                ) or ""
            )

        result["facebook"] = (
            enrichment.get(
                "facebook",
                ""
            ) or ""
        )

        result["instagram"] = (
            enrichment.get(
                "instagram",
                ""
            ) or ""
        )

        result["linkedin"] = (
            enrichment.get(
                "linkedin",
                ""
            ) or ""
        )

        result["twitter"] = (
            enrichment.get(
                "twitter",
                ""
            ) or ""
        )

        result["website_reachable"] = bool(
            enrichment.get(
                "website_reachable",
                False
            )
        )

        print(
            f"Enrichment completed: "
            f"{website}"
        )

    except Exception as error:

        print(
            "Website enrichment error:",
            error
        )

    if (
        (not result["phone"] or not result["email"])
        and business_name
    ):

        try:

            print(
                f"Contact fallback: "
                f"{business_name} - {city}"
            )

            contact_info = discover_contact_info(
                business_name,
                city,
                lead.get("address", ""),
                lead.get("phone", "")
            )

            if not result["phone"]:

                result["phone"] = (
                    contact_info.get(
                        "phone",
                        ""
                    ) or ""
                )

            if not result["email"]:

                result["email"] = (
                    contact_info.get(
                        "email",
                        ""
                    ) or ""
                )

        except Exception as error:

            print(
                "Contact discovery error:",
                error
            )

    return result


def run_enrichment_job(
    job_id,
    leads
):

    total = len(
        leads
    )

    with enrichment_lock:

        enrichment_jobs[job_id] = {
            "status":
                "running",

            "total":
                total,

            "completed":
                0,

            "leads":
                leads
        }

    try:

        with ThreadPoolExecutor(
            max_workers=5
        ) as executor:

            future_map = {
                executor.submit(
                    enrich_single_lead,
                    lead
                ):
                    lead
                for lead in leads
            }

            for future in as_completed(
                future_map
            ):

                lead = future_map[
                    future
                ]

                try:

                    enrichment = (
                        future.result()
                    )

                    if enrichment.get(
                        "website"
                    ):

                        lead["website"] = (
                            enrichment[
                                "website"
                            ]
                        )

                    if not lead.get(
                        "email"
                    ):

                        lead["email"] = (
                            enrichment.get(
                                "email",
                                ""
                            ) or ""
                        )

                    if not lead.get(
                        "phone"
                    ):

                        lead["phone"] = (
                            enrichment.get(
                                "phone",
                                ""
                            ) or ""
                        )

                    if enrichment.get(
                        "facebook"
                    ):

                        lead["facebook"] = (
                            enrichment[
                                "facebook"
                            ]
                        )

                    if enrichment.get(
                        "instagram"
                    ):

                        lead["instagram"] = (
                            enrichment[
                                "instagram"
                            ]
                        )

                    if enrichment.get(
                        "linkedin"
                    ):

                        lead["linkedin"] = (
                            enrichment[
                                "linkedin"
                            ]
                        )

                    if enrichment.get(
                        "twitter"
                    ):

                        lead["twitter"] = (
                            enrichment[
                                "twitter"
                            ]
                        )

                    lead["website_reachable"] = (
                        enrichment.get(
                            "website_reachable",
                            False
                        )
                    )

                except Exception as error:

                    print(
                        "Background enrichment error:",
                        error
                    )

                prepare_lead(
                    lead
                )

                with enrichment_lock:

                    enrichment_jobs[
                        job_id
                    ][
                        "completed"
                    ] += 1

        save_leads(
            leads
        )

        with enrichment_lock:

            enrichment_jobs[
                job_id
            ][
                "status"
            ] = "completed"

    except Exception as error:

        print(
            "Enrichment job failed:",
            error
        )

        with enrichment_lock:

            enrichment_jobs[
                job_id
            ][
                "status"
            ] = "failed"


@app.route(
    "/enrichment-status/<job_id>",
    methods=["GET"]
)
def enrichment_status(
    job_id
):

    with enrichment_lock:

        job = enrichment_jobs.get(
            job_id
        )

        if not job:

            return jsonify({
                "success": False,
                "message":
                    "Enrichment job not found."
            }), 404

        return jsonify({
            "success": True,
            "status":
                job["status"],
            "total":
                job["total"],
            "completed":
                job["completed"],
            "leads":
                job["leads"]
        })


@app.route(
    "/search",
    methods=["POST"]
)
def search():

    data = request.get_json() or {}

    keyword = str(
        data.get(
            "keyword",
            ""
        ) or ""
    ).strip()

    city = str(
        data.get(
            "city",
            ""
        ) or ""
    ).strip()

    if not keyword or not city:

        return jsonify({
            "success": False,
            "message":
                "Please enter both keyword and city."
        })

    try:

        leads = search_businesses(
            keyword,
            city,
            limit=130
        )

        print(
            f"Businesses received: "
            f"{len(leads)}"
        )

        if not leads:

            return jsonify({
                "success": True,
                "count": 0,
                "leads": [],
                "message":
                    "No businesses found. "
                    "Please try another "
                    "keyword or city."
            })

        print(
            f"Before deduplication: "
            f"{len(leads)}"
        )

        leads = deduplicate_leads(
            leads
        )

        print(
            f"After deduplication: "
            f"{len(leads)}"
        )

        leads = leads[:100]

        print(
            f"Final unique leads kept: "
            f"{len(leads)}"
        )

        for lead in leads:

            lead["facebook"] = (
                lead.get(
                    "facebook",
                    ""
                ) or ""
            )

            lead["instagram"] = (
                lead.get(
                    "instagram",
                    ""
                ) or ""
            )

            lead["linkedin"] = (
                lead.get(
                    "linkedin",
                    ""
                ) or ""
            )

            lead["twitter"] = (
                lead.get(
                    "twitter",
                    ""
                ) or ""
            )

            lead["website_reachable"] = bool(
                lead.get(
                    "website_reachable",
                    False
                )
            )

            lead["rating"] = (
                lead.get(
                    "rating",
                    ""
                ) or ""
            )

            lead["review_count"] = (
                lead.get(
                    "review_count",
                    ""
                ) or ""
            )

            lead["maps_search_link"] = ""

        for lead in leads:

            prepare_lead(
                lead
            )

        save_leads(
            leads
        )

        job_id = str(
            uuid.uuid4()
        )

        with enrichment_lock:

            enrichment_jobs[
                job_id
            ] = {
                "status":
                    "queued",

                "total":
                    len(leads),

                "completed":
                    0,

                "leads":
                    leads
            }

        background_executor.submit(
            run_enrichment_job,
            job_id,
            leads
        )

        print(
            f"Final leads returned immediately: "
            f"{len(leads)}"
        )

        return jsonify({
            "success": True,
            "count":
                len(leads),
            "leads":
                leads,
            "job_id":
                job_id,
            "enrichment_pending":
                True
        })

    except Exception as error:

        print(
            "Search error:"
        )

        print(
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to generate leads. "
                "Please try again."
        }), 500


@app.route(
    "/export/csv",
    methods=["POST"]
)
def export_csv():

    data = request.get_json() or {}

    leads = data.get(
        "leads",
        []
    )

    keyword = str(
        data.get(
            "keyword",
            ""
        ) or ""
    ).strip()

    city = str(
        data.get(
            "city",
            ""
        ) or ""
    ).strip()

    if not leads:

        return jsonify({
            "success": False,
            "message":
                "No leads available for export."
        })

    try:

        df = pd.DataFrame(
            leads
        )

        output = io.StringIO()

        df.to_csv(
            output,
            index=False
        )

        output.seek(0)

        save_download_history(
            keyword,
            city,
            len(leads),
            "CSV"
        )

        return send_file(
            io.BytesIO(
                output
                .getvalue()
                .encode(
                    "utf-8-sig"
                )
            ),
            mimetype="text/csv",
            as_attachment=True,
            download_name=
                "b2b_leads.csv"
        )

    except Exception as error:

        print(
            "CSV export error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "CSV export failed."
        }), 500


@app.route(
    "/export/excel",
    methods=["POST"]
)
def export_excel():

    data = request.get_json() or {}

    leads = data.get(
        "leads",
        []
    )

    keyword = str(
        data.get(
            "keyword",
            ""
        ) or ""
    ).strip()

    city = str(
        data.get(
            "city",
            ""
        ) or ""
    ).strip()

    if not leads:

        return jsonify({
            "success": False,
            "message":
                "No leads available for export."
        })

    try:

        columns = [
            "business_name",
            "category",
            "address",
            "city",
            "pincode",
            "phone",
            "website",
            "email",
            "instagram",
            "facebook",
            "linkedin",
            "twitter",
            "rating",
            "review_count",
            "reliability_score",
            "reliability_status",
            "missing_information",
            "google_maps_link",
            "latitude",
            "longitude"
        ]

        df = pd.DataFrame(
            leads
        )

        for column in columns:

            if column not in df.columns:

                df[column] = ""

        df = df[
            columns
        ]

        df.columns = [
            "Business Name",
            "Category",
            "Address",
            "City",
            "Pincode",
            "Phone",
            "Website",
            "Email",
            "Instagram",
            "Facebook",
            "LinkedIn",
            "Twitter / X",
            "Rating",
            "Reviews",
            "Reliability Score",
            "Reliability Status",
            "Missing Information",
            "Google Maps",
            "Latitude",
            "Longitude"
        ]

        output = io.BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Leads"
            )

        output.seek(0)

        save_download_history(
            keyword,
            city,
            len(leads),
            "Excel"
        )

        return send_file(
            output,
            mimetype=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            ),
            as_attachment=True,
            download_name=
                "b2b_leads.xlsx"
        )

    except Exception as error:

        print(
            "Excel export error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Excel export failed."
        }), 500


if __name__ == "__main__":

    init_database()

    app.run(
        debug=True,
        use_reloader=False
    )