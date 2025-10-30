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

1. **FIPS initialization**: If no FIPS codes provided, loads from `data/input/zip2fips.json` and filters for states using the federally-run marketplace (healthcare.gov). Hardcoded list includes MT, WY, UT, AZ, AK, TX, OK, KS, NE, SD, ND, WI, MO, LA, MS, AL, GA, TN, IN, OH, FL, SC, NC, HI. **Note**: VA was removed as of 2025 after moving to a state-run exchange.

2. **Years initialization**: Automatically determines enrollment years from 2016 to current enrollment year (calculated as current date + 2 months).

3. **Plan types**: Scrapes three household types:
   - `individual`: Single person age 27
   - `couple`: Two people age 27
   - `family`: Two adults age 27, two children age 2 and 7

4. **API scraping**: Makes POST requests to `https://marketplace-int.api.healthcare.gov/api/v1/plans/search` with pagination (offset parameter increments by 10 for each page).

5. **Rate limiting**: 0.33 second sleep between requests (scrape_healthcare_gov.py:50)

### Data Storage

Output structure: `data/output/[year]/[plan_type]/[fips].json`

- Each file contains an array of plan objects for a specific county (FIPS), year, and household type
- Files are only created if plans are available for that location/year/type combination
- Uses FIPS county codes as identifiers (can look up counties by zip code in `data/input/zip2fips.json`)

### Important Implementation Details

- The scraper skips FIPS codes that already have output files (scrape_healthcare_gov.py:44-47), so delete specific output files to re-scrape them
- Pagination is handled recursively - if total plans > 10, it fetches next page and concatenates results (scrape_healthcare_gov.py:58-71)
- Failed requests (no plans returned) result in the output file being deleted (scrape_healthcare_gov.py:66)
- **State list maintenance**: As states move between federal and state-run exchanges, the hardcoded state list must be updated (scrape_healthcare_gov.py:18). API returns error code 1003 "state is not a valid marketplace state" for non-federal states.
