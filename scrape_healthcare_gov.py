import os
import json
import time
import requests
from datetime import date
from dateutil import relativedelta

class ScrapeHealthcareGov():
	def __init__(self, fips=[], years=[]):
		self.fips = fips
		if len(self.fips) == 0:
			with open('data/input/zip2fips.json') as fips_zips_json:
				fips_zips = json.load(fips_zips_json)
				for (zipcode, fips_details) in fips_zips.items():
					# only scrape states that use the federally-run marketplace (healthcare.gov)
					if fips_details['state'] in ['MT','WY','UT','AZ','AK','TX','OK','KS','NE','SD','ND','WI','MO','LA','MS','AL','GA','TN','IN','OH','FL','SC','NC','VA','HI']:
						fips_details['zipcode'] = zipcode
						self.fips.append(fips_details)

		self.years = []
		if len(self.years) == 0:
			adjusted_date = date.today() + relativedelta.relativedelta(months=2)
			current_enrollment_year = adjusted_date.year
			self.years = range(2016, current_enrollment_year+1)

	def grab_plans(self, fips=None, year=None, plan_type=None, offset=0):
		if fips is None:
			for f in self.fips:
				self.grab_plans(fips=f, offset=0)
		if year is None:
			for year in self.years:
				if not os.path.isdir(f"data/output/{year}"):
					os.mkdir(f"data/output/{year}")
				self.grab_plans(fips, year)
		if plan_type is None:
			for plan_type in [
					('individual',	[{"age":27}]),
					('couple',		[{"age":27},{"age":27}]),
					('family',		[{"age":27},{"age":27},{"age":2},{"age":7}])
				]:
				(plan_type_name, people) = plan_type
				if not os.path.isdir(f"data/output/{year}/{plan_type_name}"):
					os.mkdir(f"data/output/{year}/{plan_type_name}")
				try:
					f = open(f"data/output/{year}/{plan_type_name}/{fips['fips']}.json")
					f.close()
				except IOError:
					self.grab_plans(fips, year, plan_type)
		else:
			time.sleep(.33) # don't hammer the government website
			(plan_type_name, people) = plan_type
			api_request = requests.post(f"https://marketplace-int.api.healthcare.gov/api/v1/plans/search", json={"household":{"income":-1,"people":people,"has_married_couple":(len(people) > 1)},"market":"Individual","place":{"countyfips":fips['fips'],"state":fips['state'],"zipcode":fips['zipcode']},"year":year,"filter":{"division":"HealthCare"},"limit":10,"offset":offset,"order":"asc","suppressed_plan_ids":[],"sort":"premium","aptc_override":None})
			plans_json = api_request.json()

			if offset == 0:
				with open(f"data/output/{year}/{plan_type_name}/{fips['fips']}.json", 'w') as outfile:
					if 'plans' in plans_json and len(plans_json['plans']) > 0:
						if plans_json['total'] <= 10:
							json.dump(plans_json['plans'], outfile)
						else:
							json.dump(plans_json['plans'] + self.grab_plans(fips, year, plan_type, offset+10), outfile)
						outfile.close()
					else:
						outfile.close()
						os.remove(f"data/output/{year}/{plan_type_name}/{fips['fips']}.json")
			else:
				if plans_json['total'] <= offset+10:
					return plans_json['plans']
				else:
					return plans_json['plans'] + self.grab_plans(fips, year, plan_type, offset+10)
