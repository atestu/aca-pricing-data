# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project scrapes ACA (Affordable Care Act / Obamacare) health insurance plan data from healthcare.gov to increase pricing transparency. It only collects data from the federally-run marketplace, not state-run exchanges.

## Development Commands

### Setup
```bash
make setup
```
Installs Python dependencies from requirements.txt.

### Run the scraper
```bash
make run
```
Executes the main scraper script. Note: This takes a long time due to a 0.33 second courtesy delay between API requests to avoid overloading the government website.

### Direct Python execution
```bash
python3 main.py
```

## Architecture

### Core Components

- **main.py**: Entry point that instantiates `ScrapeHealthcareGov` and calls `grab_plans()`
- **scrape_healthcare_gov.py**: Contains the `ScrapeHealthcareGov` class which handles all scraping logic

### Scraping Logic Flow

The `ScrapeHealthcareGov` class uses recursive iteration to scrape data:

1. **FIPS initialization**: If no FIPS codes provided, loads from `data/input/zip2fips.json` and filters for states using the federally-run marketplace (healthcare.gov). Hardcoded list includes MT, WY, UT, AZ, AK, TX, OK, KS, NE, SD, ND, WI, MO, LA, MS, AL, TN, IN, OH, FL, SC, NC, HI (23 states). **Note**: VA and GA were removed as of 2025 after moving to state-run exchanges (VA in early 2025, GA Access launched November 2024).

2. **Years initialization**: Automatically determines enrollment years from 2016 to current enrollment year (calculated as current date + 2 months).

3. **Plan types**: Scrapes three household types:
   - `individual`: Single person age 27
   - `couple`: Two people age 27
   - `family`: Two adults age 27, two children age 2 and 7

4. **API scraping**: Makes POST requests to `https://marketplace-int.api.healthcare.gov/api/v1/plans/search` with pagination (offset parameter increments by 10 for each page).

5. **Rate limiting**: 0.33 second sleep between requests (scrape_healthcare_gov.py:50)

### Data Storage

**Raw JSON Files:**

Output structure: `data/output/[year]/[plan_type]/[fips].json`

- Each file contains an array of plan objects for a specific county (FIPS), year, and household type
- Files are only created if plans are available for that location/year/type combination
- Uses FIPS county codes as identifiers (can look up counties by zip code in `data/input/zip2fips.json`)

**SQLite Database:**

The project includes SQLite database tools for easier querying and analysis of the scraped data. The database provides a normalized schema that makes it easier to analyze premiums across states, compare insurance companies, and track price trends.

Database location: `data/plans.db`

Schema:
- **plans**: Main table with plan details (premium, metal level, type, etc.)
  - Contains plan pricing, features (HSA eligible, national network, etc.)
  - Quality ratings (global, clinical, enrollee experience)
  - Links to benefits URLs, brochures, formularies, and provider networks
  - Foreign keys to issuers and counties
  - Unique constraint on (plan_json_id, year, household_type, fips_code)

- **issuers**: Insurance companies
  - Company name, state, contact information (toll-free, TTY)
  - Physical address and URLs for individual/SHOP plans

- **counties**: FIPS code to county name mapping
  - Links ZIP codes to FIPS codes and state abbreviations

- **deductibles**: Plan deductibles (individual/family, by network tier)
  - Separate rows for different deductible types and network tiers

- **moops**: Maximum out-of-pocket costs (individual/family, by network tier)
  - Separate rows for different MOOP types and network tiers

Database commands:

```bash
# Create database schema
python3 create_database.py

# Import all years of data
python3 import_to_sqlite.py

# Import specific year only
python3 import_to_sqlite.py --year 2025

# Custom database path
python3 import_to_sqlite.py --db /path/to/custom.db
```

Example queries:

```sql
-- Average premiums by state for Bronze plans
SELECT state, household_type, AVG(premium) as avg_premium
FROM plans
WHERE year = 2025 AND metal_level = 'Bronze'
GROUP BY state, household_type;

-- Compare specific insurance company across states
SELECT p.state, AVG(p.premium) as avg_premium
FROM plans p
JOIN issuers i ON p.issuer_id = i.id
WHERE i.name LIKE '%Blue%' AND p.year = 2025
GROUP BY p.state;

-- Find cheapest plans by county
SELECT c.county_name, c.state, p.name, p.premium, i.name as issuer
FROM plans p
JOIN counties c ON p.fips_code = c.fips
JOIN issuers i ON p.issuer_id = i.id
WHERE p.year = 2025 AND p.household_type = 'individual'
ORDER BY p.premium ASC
LIMIT 10;
```

The import script processes JSON files from `data/output/` and:
- Imports issuer data with deduplication
- Maps county information from zip2fips.json
- Normalizes plan data with foreign key relationships
- Extracts deductibles and MOOPs into separate tables
- Shows progress every 10 files for long imports

### Important Implementation Details

- The scraper skips FIPS codes that already have output files (scrape_healthcare_gov.py:44-47), so delete specific output files to re-scrape them
- Pagination is handled recursively - if total plans > 10, it fetches next page and concatenates results (scrape_healthcare_gov.py:58-71)
- Failed requests (no plans returned) result in the output file being deleted (scrape_healthcare_gov.py:66)
- **State list maintenance**: As states move between federal and state-run exchanges, the hardcoded state list must be updated (scrape_healthcare_gov.py:18). API returns error code 1003 "state is not a valid marketplace state" for non-federal states.
