import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "leads.db"


def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                place_id TEXT,

                business_name TEXT,

                category TEXT,

                address TEXT,

                city TEXT,

                pincode TEXT,

                phone TEXT,

                website TEXT,

                email TEXT,

                facebook TEXT,

                instagram TEXT,

                linkedin TEXT,

                twitter TEXT,

                rating REAL,

                review_count INTEGER,

                google_maps_link TEXT,

                latitude REAL,

                longitude REAL,

                website_reachable INTEGER DEFAULT 0,

                reliability_score INTEGER DEFAULT 0,

                reliability_status TEXT DEFAULT 'LOW',

                missing_information TEXT DEFAULT 'None'

            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS download_history (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                keyword TEXT,

                city TEXT,

                lead_count INTEGER,

                file_type TEXT,

                downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP

            )
        """)

        cursor.execute(
            "PRAGMA table_info(leads)"
        )

        existing_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        new_columns = {

            "website_reachable":
                "INTEGER DEFAULT 0",

            "reliability_score":
                "INTEGER DEFAULT 0",

            "reliability_status":
                "TEXT DEFAULT 'LOW'",

            "missing_information":
                "TEXT DEFAULT 'None'"

        }

        for column_name, column_type in new_columns.items():

            if column_name not in existing_columns:

                cursor.execute(
                    f"""
                    ALTER TABLE leads
                    ADD COLUMN {column_name}
                    {column_type}
                    """
                )

        connection.commit()

    print(
        "Database initialized successfully."
    )


def save_leads(leads):

    if not leads:

        print(
            "No leads to save."
        )

        return

    inserted = 0
    updated = 0
    skipped = 0

    with get_connection() as connection:

        cursor = connection.cursor()

        for lead in leads:

            place_id = str(
                lead.get(
                    "place_id",
                    ""
                )
            ).strip()

            business_name = str(
                lead.get(
                    "business_name",
                    ""
                )
            ).strip()

            address = str(
                lead.get(
                    "address",
                    ""
                )
            ).strip()

            existing = None

            if place_id:

                cursor.execute(
                    """
                    SELECT id
                    FROM leads
                    WHERE place_id = ?
                    LIMIT 1
                    """,
                    (place_id,)
                )

                existing = cursor.fetchone()

            if not existing and business_name:

                cursor.execute(
                    """
                    SELECT id
                    FROM leads
                    WHERE business_name = ?
                    AND address = ?
                    LIMIT 1
                    """,
                    (
                        business_name,
                        address
                    )
                )

                existing = cursor.fetchone()

            values = (

                place_id,

                business_name,

                lead.get(
                    "category",
                    ""
                ),

                address,

                lead.get(
                    "city",
                    ""
                ),

                lead.get(
                    "pincode",
                    ""
                ),

                lead.get(
                    "phone",
                    ""
                ),

                lead.get(
                    "website",
                    ""
                ),

                lead.get(
                    "email",
                    ""
                ),

                lead.get(
                    "facebook",
                    ""
                ),

                lead.get(
                    "instagram",
                    ""
                ),

                lead.get(
                    "linkedin",
                    ""
                ),

                lead.get(
                    "twitter",
                    ""
                ),

                lead.get(
                    "rating"
                ),

                lead.get(
                    "review_count"
                ),

                lead.get(
                    "google_maps_link",
                    ""
                ),

                lead.get(
                    "latitude"
                ),

                lead.get(
                    "longitude"
                ),

                1 if lead.get(
                    "website_reachable",
                    False
                ) else 0,

                lead.get(
                    "reliability_score",
                    0
                ),

                lead.get(
                    "reliability_status",
                    "LOW"
                ),

                lead.get(
                    "missing_information",
                    "None"
                )

            )

            if existing:

                cursor.execute(
                    """
                    UPDATE leads
                    SET

                        place_id = ?,
                        business_name = ?,
                        category = ?,
                        address = ?,
                        city = ?,
                        pincode = ?,
                        phone = ?,
                        website = ?,
                        email = ?,
                        facebook = ?,
                        instagram = ?,
                        linkedin = ?,
                        twitter = ?,
                        rating = ?,
                        review_count = ?,
                        google_maps_link = ?,
                        latitude = ?,
                        longitude = ?,
                        website_reachable = ?,
                        reliability_score = ?,
                        reliability_status = ?,
                        missing_information = ?

                    WHERE id = ?

                    """,

                    values + (
                        existing["id"],
                    )

                )

                updated += 1

            else:

                cursor.execute(
                    """
                    INSERT INTO leads (

                        place_id,
                        business_name,
                        category,
                        address,
                        city,
                        pincode,
                        phone,
                        website,
                        email,
                        facebook,
                        instagram,
                        linkedin,
                        twitter,
                        rating,
                        review_count,
                        google_maps_link,
                        latitude,
                        longitude,
                        website_reachable,
                        reliability_score,
                        reliability_status,
                        missing_information

                    )

                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?
                    )
                    """,

                    values

                )

                inserted += 1

        connection.commit()

    skipped = len(leads) - (
        inserted + updated
    )

    print(
        f"Database: "
        f"{inserted} inserted, "
        f"{updated} updated, "
        f"{skipped} skipped."
    )


def get_all_leads():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM leads
            ORDER BY id DESC
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


def save_download_history(
    keyword,
    city,
    lead_count,
    file_type
):

    downloaded_at = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO download_history (
                keyword,
                city,
                lead_count,
                file_type,
                downloaded_at
            )

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                keyword,
                city,
                lead_count,
                file_type,
                downloaded_at
            )

        )

        connection.commit()

    print(
        f"Download history saved: "
        f"{keyword} - {city} - "
        f"{lead_count} leads - {file_type}"
    )


def get_download_history():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                keyword,
                city,
                lead_count,
                file_type,
                downloaded_at
            FROM download_history
            ORDER BY id DESC
            LIMIT 50
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]