#!/usr/bin/env python3
from scrape_healthcare_gov import ScrapeHealthcareGov

def main():
	# Test with 2025 only
	scrape = ScrapeHealthcareGov(years=[2025])
	scrape.grab_plans()

if __name__ == '__main__':
	main()
