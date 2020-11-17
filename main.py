#!/usr/bin/env python3
from scrape_healthcare_gov import ScrapeHealthcareGov

def main():
	scrape = ScrapeHealthcareGov()
	scrape.grab_plans()

if __name__ == '__main__':
	main()
