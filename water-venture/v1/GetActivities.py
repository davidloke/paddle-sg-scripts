print ("Getting Kayak Activities")

import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

maintenance_code = "-1"

isOperatorSiteDown = 0

def formatClubVenue(course_venue):
	changi_address = ("changi", "nicoll")
	
	prefix = "PA Water-Venture "
	if "bedok" in course_venue.lower():
		return prefix + "(Bedok Reservoir)"
	elif any(s in course_venue.lower() for s in changi_address):
		return prefix + "(Changi)"
	elif "east" in course_venue.lower():
		return prefix + "(East Coast)"
	elif "jurong" in course_venue.lower():
		return prefix + "(Jurong Lake)"
	elif "kallang" in course_venue.lower():
		return prefix + "(Kallang)"
	elif "pasir" in course_venue.lower():
		return prefix + "(Pasir Ris)"
	elif "sembawang" in course_venue.lower():
		return prefix + "(Sembawang)"
	elif "lower" in course_venue.lower():
		return prefix + "(Lower Seletar Reservoir)"
	else: 
		return prefix

# Note: Unlike course codes, activity codes do not come with the prefix "A", due to data collection method. Therefore we do not need to substring it in the first line
def formatForGitHubPages(activity_dictionary): 
	field_coursecode = "[" + activity_dictionary["title"] + "](https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + activity_dictionary["activity_code"] + ")"
	field_dates = ""
	field_dates_tokens = re.findall(r'(\d\d-\w\w\w-\d\d)', activity_dictionary["Dates"])
	
	for each_date in field_dates_tokens[:-1]:
		field_dates += (each_date + "<br /><br />")
	field_dates += field_dates_tokens[-1]
	
	field_venue = formatClubVenue(activity_dictionary["Venue"])
	field_vacancy = activity_dictionary["Vacancies"]
	field_regclose = activity_dictionary["RegClose"]
	return field_coursecode + "|" + field_dates + "|" + field_venue + "|" + field_vacancy + "<br /><br /> _(Register by: " + field_regclose + ")_"
	
	
def formatContent(activity_dictionary):

	activity_dictionary['Dates'] = re.search(r'Day/Time: (.*) No. of Sessions:',activity_dictionary["Activity Details"]).group(1)

	# Check if the date format is correct. If not, default to the "Date" field, but only shows the first date (if it is a multi-date activity). Example of Date field: "14-Oct-17 to 30-Oct-17"
	datePatternChecker = re.compile("\d\d-\w\w\w-\d\d")
	if not datePatternChecker.match(activity_dictionary['Dates'][0:9]):
		activity_dictionary['Dates'] = re.search(r'Date: (.*) Day/Time:',activity_dictionary["Activity Details"]).group(1)
	
	activity_dictionary['NumSessions'] = re.search(r'No. of Sessions: (\d)+ Venue:',activity_dictionary["Activity Details"]).group(1)
	
	activity_dictionary['Venue'] = re.search(r'Venue: (.*) Class Size:',activity_dictionary["Activity Details"]).group(1)
	
	activity_dictionary['Class Size'] = re.search(r'Class Size: (.*) Language:',activity_dictionary["Activity Details"]).group(1)
	
	activity_dictionary['RegClose'] = re.search(r'Registration Closing Date: (.*)$',activity_dictionary["Activity Details"]).group(1)	

	
def processIndividualActivity(activity_dictionary):
	
	# Make individual activity page into a beautiful soup
	ind_activity_page = requests.get("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + activity_dictionary["activity_code"])
	activity_page_html = BeautifulSoup(ind_activity_page.text, "html.parser")
	
	# Extract the activity title
	activity_dictionary["title"] = activity_page_html.find("td",{'class': 'course_title'}).get_text().replace("\t","").replace("\r\n","").strip()
	
	# Extract the course details
	course_details = activity_page_html.find_all("h2",{'class': 'title_main2'})
	for item in course_details: 
		section_title = " ".join(item.get_text().split()).replace(":","") #https://stackoverflow.com/questions/1546226
		section_body = " ".join(item.find_next("p").get_text().split())
		activity_dictionary[section_title] = section_body.strip()
		
	
def getClubActivityList(outlet_id):
	# Make POST request to get actvities for the club specified in outlet_id
	headers = {'User-Agent': 'Mozilla/5.0'}
	payload = {'idInternalCCRC':outlet_id, "cdSubj":"0","btnGo.x":"42","btnGo.y":"0"}

	response = requests.post("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=action&wlpCRMSPortal_1_action=CMFCategoryActivitySelection&_pageLabel=CRMSPortal_page_1", data=payload, headers=headers)

	# Check if page is under maintenance
	if "We wish to inform that the website is under a routine maintenance." in response.text:
		print("Operator site is under maintenace")
		return maintenance_code

	activity_list = []
	vacancy_list  = []
	activity_dictionary_list = []

	# Extract out a list of activity codes
	for m in re.finditer(r'javascript:doRedirectToProducts\(\'([0-9]*)\',\'[a-zA-Z]*\',\'[a-zA-Z]*\'\)', response.text):
		activity_list.append(m.group(1))

	# Extract out a list of activity vacancies 
	for a in re.finditer(r'<SPAN class=body_boldtext>Vacancies:</SPAN>\s*(\d+|No Vacancy)', response.text):
		vacancy_list.append(a.group(1))
		
	# Combine activity code and vacancies into dictionary object 
	for i in range(0,len(activity_list)):
		activity_dictionary_list.append({"activity_code": activity_list[i], "Vacancies": vacancy_list[i]})
		
	return activity_dictionary_list

def sortActivitiesByDate(all_activities):
	for activity in all_activities:
		activity["dateObj"] = datetime.strptime(activity['Dates'][0:9], "%d-%b-%y").date()
		
	return sorted(all_activities, key=lambda k: k['dateObj'])

	
def getOutletActivity(outlet_id):

	global isOperatorSiteDown
	outlet_activity_list = getClubActivityList(outlet_id)

	if (outlet_activity_list == maintenance_code):
		isOperatorSiteDown = 1
		print("Maintenance mode - returning empty")
		return []

	vacancy_outlet_activity_list = []
	for activity in outlet_activity_list:
		if activity["Vacancies"] != "No Vacancy":
			processIndividualActivity(activity)			
			formatContent(activity)
			if (datetime.strptime(activity['Dates'][0:9], '%d-%b-%y').date() > datetime.today().date()):
				vacancy_outlet_activity_list.append(activity)
	
	return vacancy_outlet_activity_list

all_outlet_activity_list = []
all_outlet_activity_list += getOutletActivity("1395630") # Bedok Reservoir
all_outlet_activity_list += getOutletActivity("1395610") # Changi
all_outlet_activity_list += getOutletActivity("1395614") # East Coast
all_outlet_activity_list += getOutletActivity("1395633") # Jurong Lake
all_outlet_activity_list += getOutletActivity("1395618") # Kallang
all_outlet_activity_list += getOutletActivity("1395622") # Pasir Ris
all_outlet_activity_list += getOutletActivity("11166460") # Sembawang
all_outlet_activity_list += getOutletActivity("1397375") # Water Venture Section
all_outlet_activity_list += getOutletActivity("11021193") # Lower Seletar

f = open('./info-sitedown.out', 'w')
if isOperatorSiteDown == 0:
	f.write("false")
else: 
	f.write("true")
f.close()

if isOperatorSiteDown != 0:
	print("GetActivities.py - operator site down. not saving")
	exit()


sorted_all_outlet_activity_list = sortActivitiesByDate(all_outlet_activity_list)
activity_formatted_string = ""
expedition_formatted_string = ""
fourstar_formatted_string = ""

for activity in sorted_all_outlet_activity_list:
	formatted_output = formatForGitHubPages(activity)
	if (("expedition" in formatted_output.lower()) or ("discovery series" in formatted_output.lower())):
		expedition_formatted_string += formatted_output + "\n"
	elif ("4 star" in formatted_output.lower()):
		fourstar_formatted_string += formatted_output + "\n"
	else:
		activity_formatted_string += formatted_output + "\n"


# Code to handle no records found
if activity_formatted_string == "":	
	activity_formatted_string = "No upcoming activities yet|-|-|- \n"

if expedition_formatted_string == "":	
	expedition_formatted_string = "No upcoming expeditions yet|-|-|- \n"

if fourstar_formatted_string == "":	
	fourstar_formatted_string = "No upcoming courses yet|-|-|- \n"
	

f = open('./out-activity.txt', 'w')
f.write(activity_formatted_string)
f.close()

f = open('./out-expedition.txt', 'w')
f.write(expedition_formatted_string)
f.close()

f = open('./out-fourstar.txt', 'w')
f.write(fourstar_formatted_string)
f.close()

print ("Finished Processing Kayak Activities")