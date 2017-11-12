from CommonFunctions import saveSiteDownStatus, formatPAClubVenue
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

def getOutletActivityListing(url, outletId, operator):

	# Make POST request to get actvities for the club specified in outletId
	headers = {'User-Agent': 'Mozilla/5.0'}
	payload = {'idInternalCCRC':outletId, "cdSubj":"0","btnGo.x":"42","btnGo.y":"0"}

	urlResponseObj = requests.post(url, data=payload, headers=headers)

	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get a list of activities by outlet")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;
	
	activityDictionaryList = []

	# Get a stream of activity codes
	activityCodeList = re.finditer(r'javascript:doRedirectToProducts\(\'([0-9]*)\',\'[a-zA-Z]*\',\'[a-zA-Z]*\'\)', urlResponseObj.text)

	# Extract out a list of activity vacancies 
	activityVacancyList = re.finditer(r'<SPAN class=body_boldtext>Vacancies:</SPAN>\s*(\d+|No Vacancy)', urlResponseObj.text)
		
	# Combine activity code and vacancies into dictionary object 
	for activityCode, activityVacancy in zip(activityCodeList, activityVacancyList):
		activityDictionaryList.append({"activity_code": activityCode.group(1), "vacancies": activityVacancy.group(1)})
		
	return activityDictionaryList
		
def filterListOfActivitiesOnVacancies (activityDictionaryList):

	# Iterate through the activities dictionaries. For every activity that has:
	#   1) vacancies 
	# Process their individual course page, and add additional details into the course dictionary 
	# Always returns a filtered List 
	
	# Error Checking - empty list
	if activityDictionaryList is None: 
		return [];
		
	for activityDictionary in activityDictionaryList:
		if ("vacancies" in activityDictionary) and activityDictionary["vacancies"] != "No Vacancy":
			activityDictionary["furtherProcess"] = True
		else:
			activityDictionary["furtherProcess"] = False
	
	return activityDictionaryList
	
def filterListOfActivitiesOnDate (activityDictionaryList):
	# If starting date of event is later than today's date, set the "furtherProcess" flag to False.
	for activityDictionary in activityDictionaryList:
		if ('Dates' in activityDictionary) and datetime.strptime(activityDictionary['Dates'][0:9], '%d-%b-%y').date() > datetime.today().date():
			activityDictionary["futherProcess"] = False
	
	return activityDictionaryList

def sortListOfActivitiesByDate (activityDictionaryList):
	for activityDictionary in activityDictionaryList:
		activityDictionary["dateObj"] = datetime.strptime(activityDictionary['Dates'][0:9], "%d-%b-%y").date()
		
	return sorted(activityDictionaryList, key=lambda k: k['dateObj'])

def processAdditionalActivityDetails(activityDictionary):

	activityDictionary['Dates'] = re.search(r'Day/Time: (.*) No. of Sessions:',activityDictionary["Activity Details"]).group(1)

	# Check if the date format is correct. If not, default to the "Date" field, but only shows the first date (if it is a multi-date activity). Example of Date field: "14-Oct-17 to 30-Oct-17"
	datePatternChecker = re.compile("\d\d-\w\w\w-\d\d")
	if not datePatternChecker.match(activityDictionary['Dates'][0:9]):
		activityDictionary['Dates'] = re.search(r'Date: (.*) Day/Time:',activityDictionary["Activity Details"]).group(1)
	
	activityDictionary['NumSessions'] = re.search(r'No. of Sessions: (\d)+ Venue:',activityDictionary["Activity Details"]).group(1)
	
	activityDictionary['Venue'] = re.search(r'Venue: (.*) Class Size:',activityDictionary["Activity Details"]).group(1)
	
	activityDictionary['Class Size'] = re.search(r'Class Size: (.*) Language:',activityDictionary["Activity Details"]).group(1)
	
	activityDictionary['RegClose'] = re.search(r'Registration Closing Date: (.*)$',activityDictionary["Activity Details"]).group(1)	
	
def getAdditionalActivityDetails(activityDictionary):
	
	# Make individual activity page into a beautiful soup
	url = "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + activityDictionary["activity_code"]
	urlResponseObj = requests.get(url)
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get additional activity details")
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;
	
	activityPageHtml = BeautifulSoup(urlResponseObj.text, "html.parser")
	
	# Extract the activity title (special formatting)
	activityDictionary["title"] = activityPageHtml.find("td",{'class': 'course_title'}).get_text().replace("\t","").replace("\r\n","").strip()
	
	# Extract the additional course details
	courseDetails = activityPageHtml.find_all("h2",{'class': 'title_main2'})
	for item in courseDetails: 
		sectionTitle = " ".join(item.get_text().split()).replace(":","") #https://stackoverflow.com/questions/1546226
		sectionBody = " ".join(item.find_next("p").get_text().split())
		activityDictionary[sectionTitle] = sectionBody.strip()

	return activityDictionary;
	
def formatForGitHubPages(activity_dictionary): 
	fieldCourseCode = "[" + activity_dictionary["title"] + "](https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + activity_dictionary["activity_code"] + ")"
	fieldDates = ""
	fieldDatesTokens = re.findall(r'(\d\d-\w\w\w-\d\d)', activity_dictionary["Dates"])
	
	for eachDate in fieldDatesTokens[:-1]:
		fieldDates += (eachDate + "<br /><br />")
	fieldDates += fieldDatesTokens[-1]
	
	fieldVenue = formatPAClubVenue(activity_dictionary["Venue"])
	fieldVacancy = activity_dictionary["vacancies"]
	fieldRegclose = activity_dictionary["RegClose"]
	return fieldCourseCode + "|" + fieldDates + "|" + fieldVenue + "|" + fieldVacancy + "<br /><br /> _(Register by: " + fieldRegclose + ")_"
	
def processOutletActivities(type, url, outletId, operator): 

	print("Processing " + type)
	
	outletActivityList = getOutletActivityListing(url, outletId, operator)
	
	if not outletActivityList:
		return []
	
	activityWithVacancyList = filterListOfActivitiesOnVacancies(outletActivityList)
	
	# Continue to retrieve and process the additional details if there are vacancies (as indicated by "furtherProcess" flag
	for activityDictionary in activityWithVacancyList: 
		if activityDictionary["furtherProcess"]: 
			getAdditionalActivityDetails(activityDictionary)
			processAdditionalActivityDetails(activityDictionary)
	
	# With the additional details, filter the activities by date 
	activityWithVacancyDateList = filterListOfActivitiesOnDate(activityWithVacancyList)
	
	# Produce output array with only valid activities 
	outputCourseList = []
	for activityDictionary in activityWithVacancyDateList: 
		if activityDictionary["furtherProcess"]:
			outputCourseList.append(activityDictionary)
	
	return outputCourseList
	