# Affordable Care Act Prices

The goal of this project is to increase pricing transparency in ACA health insurance plans (also known as Obamacare plans).

The project currently scrapes healthcare plan information from the healthcare.gov website, so we don't have prices from state-run exchanges.

The data can be found under `data/output/[year]/[plan_type]/[fips].json` (more on FIPS below)

## Run it yourself

First run `make setup` (to install the python3 packages, found in [requirements.txt](requirements.txt)), then `make run`.

It will take a long time since there is a 1 second waiting time in between each scrape (we don't want to make the website crash [again](https://en.wikipedia.org/wiki/HealthCare.gov#Issues_during_launch))

## More info

The [FIPS code](https://en.wikipedia.org/wiki/FIPS_county_code) represents counties of the US. You can look up counties by zip code in data/input/zip2fips.json to find the ones you're interested in (there can be multiple counties in one zip code).

This project collects data in a machine-readable format. There is a separate project for the website which uses this data to display information about health plans in an easy to digest format for humans (coming soon).

## Thanks

The FIPS/zip code data is available thanks to [@bgruber/zip2fips](https://github.com/bgruber/zip2fips) (which I [forked](https://github.com/atestu/zip2fips) to be able to filter states)