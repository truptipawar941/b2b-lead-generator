# Automated B2B Business Lead Generation Tool

## Project Overview

The Automated B2B Business Lead Generation Tool is a Python-based web application that helps users discover local businesses using a business keyword and city.

The tool collects publicly available business information, enriches available contact details, removes duplicate records, stores leads in a local database, and allows users to export the results in CSV and Excel formats.

## Key Features

- Search local businesses using keyword and city
- Collect business name and address
- Collect available phone numbers
- Discover business websites where possible
- Extract publicly available emails and social profiles
- Remove duplicate business records
- Store leads using SQLite
- View saved leads
- View lead availability and reliability analytics
- Generate Google Maps search links
- Export leads to CSV
- Export leads to Excel
- Handle searches with no matching results
- Background enrichment for discovered leads

## Technology Stack

### Backend

- Python
- Flask

### Data Collection & Enrichment

- OpenStreetMap / Overpass API
- Requests
- BeautifulSoup

### Data Processing

- Pandas
- Regular Expressions

### Database

- SQLite

### Export

- CSV
- Excel
- OpenPyXL

### Frontend

- HTML
- CSS
- JavaScript

## How It Works

1. User enters a business keyword and city.
2. The application searches OpenStreetMap data through the Overpass API.
3. Business records are collected and normalized.
4. Duplicate records are removed.
5. Available business information is stored in the SQLite database.
6. Website discovery and contact enrichment are performed where possible.
7. The application calculates lead reliability based on available information.
8. Users can view, analyze, and export the collected leads.

## Installation

Clone or download the project and open the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

Run:

```bash
python app.py
```

Open the application in a browser:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
b2b-lead-generator/
│
├── app.py
├── scraper/
│   ├── __init__.py
│   ├── business_search.py
│   └── website_enricher.py
│
├── templates/
│   ├── index.html
│   ├── saved_leads.html
│   ├── analytics.html
│   ├── download_history.html
│   └── settings.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── leads.db
│
├── utils/
│   ├── __init__.py
│   ├── deduplication.py
│   └── reliability.py
│
├── requirements.txt
└── README.md
```

## Data Source

Business discovery is performed using publicly available OpenStreetMap data through the Overpass API.

Website and contact enrichment uses publicly accessible website information where available.

Google Maps links are generated as search/location links for convenient verification. The project does **not** use the paid Google Places API.

## Lead Data

Depending on public availability, a lead may contain:

- Business Name
- Address
- Phone
- Website
- Email
- Social Profiles
- Google Maps Link
- Reliability Status

Unavailable information is left blank rather than being fabricated.

## Export

The application supports:

### CSV Export

Leads can be exported as a `.csv` file for use in spreadsheets and CRM workflows.

### Excel Export

Leads can be exported as an `.xlsx` file for further analysis and business use.

## Analytics

The Analytics page provides an overview of:

- Total Leads
- Available Websites
- Available Emails
- Available Phone Numbers
- Available Social Profiles
- Lead Reliability

## Duplicate Handling

Duplicate businesses are removed using normalized business information such as:

- Business name
- Address
- Phone number

This helps keep the final lead list cleaner and more useful.

## Reliability

Lead reliability is based on the availability of useful business information.

Records with more complete contact information receive a higher reliability level, while records with limited information receive a lower reliability level.

## Limitations

- Business information depends on publicly available OpenStreetMap data.
- Not every business has a phone number, website, or email listed publicly.
- Website and contact discovery may not work for every business.
- Search results can vary depending on OpenStreetMap coverage.
- Public data sources may have rate limits or temporary availability issues.

## Project Status

The application has been tested for:

- Business search
- Lead data display
- Duplicate handling
- Database storage
- CSV export
- Excel export
- Analytics
- Google Maps links
- Application pages
- No-result/error handling

## Future Improvements

Possible future improvements include:

- More business data sources
- Advanced lead scoring
- Improved email verification
- CRM integrations
- More detailed analytics
- Scheduled lead generation

## License

This project is developed as an educational/placement project using free and open-source technologies.
