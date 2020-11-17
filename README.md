# Affordable Care Act Price data

The goal of this project is to increase pricing transparency in ACA (also known as Obamacare) health insurance plans.

The project currently scrapes healthcare plans from the healthcare.gov websites, so we don't have prices from state-run exchanges.

The data can be found under data/output/[year]/[plan_type]/[fips].json

The FIPS code represents counties of the US. You can look up counties in data/input/fips.json to find the ones you're interested in.

This project only collects data. There is a separate project for the website which uses this data to display information about health plans in an easy to digest format (coming soon).