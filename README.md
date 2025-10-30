# "Affordable Care Act" Health Insurance Plans Data

The goal of this project is to increase pricing transparency in ACA health insurance plans (also known as Obamacare plans).

This project scrapes health plan information from the healthcare.gov API (federally-run marketplace only, not state-run exchanges). As of 2025, this includes: MT, WY, UT, AZ, AK, TX, OK, KS, NE, SD, ND, WI, MO, LA, MS, AL, TN, IN, OH, FL, SC, NC, HI.

**Note**: Virginia and Georgia moved to state-run exchanges and are no longer included (VA transitioned before 2024 enrollment, GA Access launched November 2024). Historical data for VA (2022-2023) and GA (2022-2024) is included.

## Getting the Data

### Option 1: SQLite Database (Recommended)

The easiest way to analyze the data is using the SQLite database included in this repository:

```bash
git clone https://github.com/atestu/aca-pricing-data.git
cd aca-pricing-data
sqlite3 data/plans.db
```

Example queries:
```sql
-- Average premiums by state for Bronze plans
SELECT state, household_type, AVG(premium) as avg_premium
FROM plans
WHERE year = 2025 AND metal_level = 'Bronze'
GROUP BY state, household_type;

-- Compare insurance companies across states
SELECT p.state, AVG(p.premium) as avg_premium
FROM plans p
JOIN issuers i ON p.issuer_id = i.id
WHERE i.name LIKE '%Blue%' AND p.year = 2025
GROUP BY p.state;
```

### Option 2: Raw JSON Data

Download compressed archives from [GitHub Releases](https://github.com/atestu/aca-pricing-data/releases):
- 2025 plans: See latest release
- Additional years: Check releases page

File structure: `data/output/[year]/[plan_type]/[fips].json`

### Option 3: Run the Scraper Yourself

First run `make setup` (to install Python packages), then `make run`.

**Warning**: This takes ~20 hours due to rate limiting (0.33s between requests to avoid overloading healthcare.gov)

## Database Schema

The SQLite database contains the following tables:

- **plans**: Main table with plan details (premium, metal level, type, etc.)
- **issuers**: Insurance companies (name, contact info, state)
- **counties**: FIPS code to county name mapping
- **deductibles**: Plan deductibles (individual, family, network tiers)
- **moops**: Maximum out-of-pocket costs

To rebuild or import data into the database:
```bash
python3 create_database.py          # Creates schema
python3 import_to_sqlite.py         # Imports all years
python3 import_to_sqlite.py --year 2025  # Import specific year
```

## More Info

The [FIPS code](https://en.wikipedia.org/wiki/FIPS_county_code) represents counties of the US. You can look up counties by zip code in data/input/zip2fips.json to find the ones you're interested in (there can be multiple counties in one zip code).

**Website**: This project collects data in a machine-readable format. There is a companion website project that displays the data in a human-friendly interface: [aca-prices-website](https://github.com/atestu/aca-prices-website)

## Thanks

The FIPS/zip code data is available thanks to [@bgruber/zip2fips](https://github.com/bgruber/zip2fips) (which I [forked](https://github.com/atestu/zip2fips) to be able to filter states)