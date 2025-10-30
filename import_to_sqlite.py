#!/usr/bin/env python3
"""
Import ACA plan data from JSON files into SQLite database.

Usage:
    python3 import_to_sqlite.py [--year YEAR] [--db PATH]

If no year specified, imports all available years.
"""
import sqlite3
import json
import os
import glob
import argparse
from pathlib import Path

def import_counties(cursor):
	"""Import county data from zip2fips.json."""
	print("Importing counties from zip2fips.json...")

	with open('data/input/zip2fips.json') as f:
		zip2fips = json.load(f)

	counties_added = set()
	for zipcode, fips_data in zip2fips.items():
		fips = fips_data['fips']
		if fips not in counties_added:
			cursor.execute('''
				INSERT OR REPLACE INTO counties (fips, county_name, state, zipcode)
				VALUES (?, ?, ?, ?)
			''', (fips, fips_data.get('county'), fips_data['state'], zipcode))
			counties_added.add(fips)

	print(f"  Imported {len(counties_added)} counties")

def import_issuer(cursor, issuer_data):
	"""Import issuer data into database."""
	cursor.execute('''
		INSERT OR REPLACE INTO issuers (
			id, name, state, toll_free, tty,
			address_street1, address_city, address_state, address_zipcode,
			individual_url, shop_url
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	''', (
		issuer_data['id'],
		issuer_data['name'],
		issuer_data['state'],
		issuer_data.get('toll_free'),
		issuer_data.get('tty'),
		issuer_data.get('address', {}).get('street1'),
		issuer_data.get('address', {}).get('city'),
		issuer_data.get('address', {}).get('state'),
		issuer_data.get('address', {}).get('zipcode'),
		issuer_data.get('individual_url'),
		issuer_data.get('shop_url')
	))

def import_plan(cursor, plan_data, year, household_type, fips, json_path):
	"""Import a single plan and its related data."""

	# Import issuer first
	import_issuer(cursor, plan_data['issuer'])

	# Import plan
	quality = plan_data.get('quality_rating', {})

	cursor.execute('''
		INSERT OR REPLACE INTO plans (
			plan_json_id, name, issuer_id, year, household_type, fips_code,
			premium, premium_w_credit, ehb_premium, pediatric_ehb_premium,
			metal_level, type, state, market,
			hsa_eligible, has_national_network, specialist_referral_required, rx_3mo_mail_order,
			quality_global_rating, quality_clinical_rating, quality_enrollee_rating,
			benefits_url, brochure_url, formulary_url, network_url,
			json_path
		) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	''', (
		plan_data['id'],
		plan_data['name'],
		plan_data['issuer']['id'],
		year,
		household_type,
		fips,
		plan_data['premium'],
		plan_data.get('premium_w_credit'),
		plan_data.get('ehb_premium'),
		plan_data.get('pediatric_ehb_premium'),
		plan_data.get('metal_level'),
		plan_data.get('type'),
		plan_data['state'],
		plan_data.get('market'),
		plan_data.get('hsa_eligible'),
		plan_data.get('has_national_network'),
		plan_data.get('specialist_referral_required'),
		plan_data.get('rx_3mo_mail_order'),
		quality.get('global_rating'),
		quality.get('clinical_quality_management_rating'),
		quality.get('enrollee_experience_rating'),
		plan_data.get('benefits_url'),
		plan_data.get('brochure_url'),
		plan_data.get('formulary_url'),
		plan_data.get('network_url'),
		json_path
	))

	# Get the plan ID that was just inserted
	plan_id = cursor.lastrowid

	# Import deductibles
	for deductible in plan_data.get('deductibles', []):
		cursor.execute('''
			INSERT INTO deductibles (
				plan_id, type, amount, network_tier, family_cost, is_individual, is_family
			) VALUES (?, ?, ?, ?, ?, ?, ?)
		''', (
			plan_id,
			deductible.get('type'),
			deductible.get('amount'),
			deductible.get('network_tier'),
			deductible.get('family_cost'),
			deductible.get('individual'),
			deductible.get('family')
		))

	# Import MOOPs
	for moop in plan_data.get('moops', []):
		cursor.execute('''
			INSERT INTO moops (
				plan_id, type, amount, network_tier, family_cost, is_individual, is_family
			) VALUES (?, ?, ?, ?, ?, ?, ?)
		''', (
			plan_id,
			moop.get('type'),
			moop.get('amount'),
			moop.get('network_tier'),
			moop.get('family_cost'),
			moop.get('individual'),
			moop.get('family')
		))

def import_json_file(cursor, filepath):
	"""Import a single JSON file containing plans."""
	# Extract metadata from filepath
	# Format: data/output/{year}/{household_type}/{fips}.json
	parts = Path(filepath).parts
	year = int(parts[2])
	household_type = parts[3]
	fips = parts[4].replace('.json', '')

	with open(filepath) as f:
		plans = json.load(f)

	for plan in plans:
		import_plan(cursor, plan, year, household_type, fips, filepath)

	return len(plans)

def import_data(db_path='data/plans.db', year_filter=None):
	"""Import all JSON files into the database."""

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Enable foreign keys
	cursor.execute('PRAGMA foreign_keys = ON')

	# Import counties first
	import_counties(cursor)
	conn.commit()

	# Find all JSON files
	pattern = 'data/output/*/*/*.json'
	if year_filter:
		pattern = f'data/output/{year_filter}/*/*.json'

	json_files = sorted(glob.glob(pattern))

	if not json_files:
		print(f"No JSON files found matching pattern: {pattern}")
		return

	print(f"\nFound {len(json_files)} JSON files to import")

	# Import plans
	total_plans = 0
	for i, filepath in enumerate(json_files, 1):
		try:
			plans_count = import_json_file(cursor, filepath)
			total_plans += plans_count

			# Commit every 10 files for better performance
			if i % 10 == 0:
				conn.commit()
				print(f"  Processed {i}/{len(json_files)} files ({total_plans} plans)...")
		except Exception as e:
			print(f"  Error processing {filepath}: {e}")
			continue

	# Final commit
	conn.commit()

	# Print summary
	print(f"\nImport complete!")
	print(f"  Total files processed: {len(json_files)}")
	print(f"  Total plans imported: {total_plans}")

	# Print database statistics
	cursor.execute('SELECT COUNT(*) FROM issuers')
	print(f"  Issuers in database: {cursor.fetchone()[0]}")

	cursor.execute('SELECT COUNT(*) FROM counties')
	print(f"  Counties in database: {cursor.fetchone()[0]}")

	cursor.execute('SELECT COUNT(*) FROM plans')
	print(f"  Plans in database: {cursor.fetchone()[0]}")

	cursor.execute('SELECT COUNT(*) FROM deductibles')
	print(f"  Deductibles in database: {cursor.fetchone()[0]}")

	cursor.execute('SELECT COUNT(*) FROM moops')
	print(f"  MOOPs in database: {cursor.fetchone()[0]}")

	conn.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Import ACA plan data to SQLite')
	parser.add_argument('--year', type=int, help='Only import specific year')
	parser.add_argument('--db', default='data/plans.db', help='Database path')
	args = parser.parse_args()

	import_data(args.db, args.year)
