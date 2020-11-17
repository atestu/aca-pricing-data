# Affordable Care Act Price data

The goal of this project is to increase pricing transparency in ACA (also known as Obamacare) health insurance plans.

The project currently scrapes healthcare plans from the healthcare.gov websites, so we don't have prices from state-run exchanges.

The data can be found under `data/output/[year]/[plan_type]/[fips\*].json`

## Run it yourself

First run `make setup` (to install the python3 packages, found in [requirements.txt](requirements.txt)), then `make run`.

It will take a long time since there is a 1 second waiting time in between each scrape (we don't want to make the website crash [again](https://en.wikipedia.org/wiki/HealthCare.gov#Issues_during_launch))

## More info

\* The FIPS code represents counties of the US. You can look up counties in data/input/fips.json to find the ones you're interested in.

This project collects data in a machine-readable format. There is a separate project for the website which uses this data to display information about health plans in an easy to digest format for humans (coming soon).

## Thanks

The FIPS/zip code data is available thanks to [@bgruber/zip2fips](https://github.com/bgruber/zip2fips) (which I [forked](https://github.com/atestu/zip2fips) to be able to filter states)