#!/usr/bin/env python3
"""
Create the SQLite database schema for ACA plan data.
"""
import sqlite3
import os

def create_database(db_path='data/plans.db'):
	"""Create the database schema."""

	# Ensure data directory exists
	os.makedirs(os.path.dirname(db_path), exist_ok=True)

	# Connect to database (creates if doesn't exist)
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Enable foreign keys
	cursor.execute('PRAGMA foreign_keys = ON')

	# 1. Insurance companies (issuers)
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS issuers (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			state TEXT NOT NULL,
			toll_free TEXT,
			tty TEXT,
			address_street1 TEXT,
			address_city TEXT,
			address_state TEXT,
			address_zipcode TEXT,
			individual_url TEXT,
			shop_url TEXT
		)
	''')

	# 2. Counties (FIPS codes)
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS counties (
			fips TEXT PRIMARY KEY,
			county_name TEXT,
			state TEXT NOT NULL,
			zipcode TEXT
		)
	''')

	# 3. Plans (main table)
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS plans (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			plan_json_id TEXT NOT NULL,
			name TEXT NOT NULL,
			issuer_id TEXT NOT NULL,
			year INTEGER NOT NULL,
			household_type TEXT NOT NULL,
			fips_code TEXT NOT NULL,

			-- Pricing
			premium REAL NOT NULL,
			premium_w_credit REAL,
			ehb_premium REAL,
			pediatric_ehb_premium REAL,

			-- Plan characteristics
			metal_level TEXT,
			type TEXT,
			state TEXT NOT NULL,
			market TEXT,

			-- Features
			hsa_eligible BOOLEAN,
			has_national_network BOOLEAN,
			specialist_referral_required BOOLEAN,
			rx_3mo_mail_order BOOLEAN,

			-- Quality
			quality_global_rating INTEGER,
			quality_clinical_rating INTEGER,
			quality_enrollee_rating INTEGER,

			-- URLs
			benefits_url TEXT,
			brochure_url TEXT,
			formulary_url TEXT,
			network_url TEXT,

			-- Audit trail
			json_path TEXT,

			-- Constraints
			FOREIGN KEY (issuer_id) REFERENCES issuers(id),
			FOREIGN KEY (fips_code) REFERENCES counties(fips),
			UNIQUE(plan_json_id, year, household_type, fips_code)
		)
	''')

	# 4. Deductibles
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS deductibles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			plan_id INTEGER NOT NULL,
			type TEXT NOT NULL,
			amount REAL NOT NULL,
			network_tier TEXT,
			family_cost TEXT,
			is_individual BOOLEAN,
			is_family BOOLEAN,

			FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
		)
	''')

	# 5. Max Out of Pocket
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS moops (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			plan_id INTEGER NOT NULL,
			type TEXT NOT NULL,
			amount REAL NOT NULL,
			network_tier TEXT,
			family_cost TEXT,
			is_individual BOOLEAN,
			is_family BOOLEAN,

			FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
		)
	''')

	# Create indexes for performance
	indexes = [
		'CREATE INDEX IF NOT EXISTS idx_plans_state ON plans(state)',
		'CREATE INDEX IF NOT EXISTS idx_plans_year ON plans(year)',
		'CREATE INDEX IF NOT EXISTS idx_plans_issuer ON plans(issuer_id)',
		'CREATE INDEX IF NOT EXISTS idx_plans_metal_level ON plans(metal_level)',
		'CREATE INDEX IF NOT EXISTS idx_plans_household ON plans(household_type)',
		'CREATE INDEX IF NOT EXISTS idx_plans_state_year ON plans(state, year)',
		'CREATE INDEX IF NOT EXISTS idx_plans_issuer_state ON plans(issuer_id, state)',
		'CREATE INDEX IF NOT EXISTS idx_plans_premium ON plans(premium)',
		'CREATE INDEX IF NOT EXISTS idx_deductibles_amount ON deductibles(amount)',
		'CREATE INDEX IF NOT EXISTS idx_moops_amount ON moops(amount)',
	]

	for index_sql in indexes:
		cursor.execute(index_sql)

	conn.commit()
	conn.close()

	print(f"Database created successfully at: {db_path}")

if __name__ == '__main__':
	create_database()
