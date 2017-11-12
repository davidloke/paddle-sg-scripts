from CommonFunctions import saveSiteDownStatus, isSiteDown, formatPAClubVenue
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re


def getCourseListing(url, operator):
	
	# Get Course Listing based on URL argument 
	urlResponseObj = requests.get(url)
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get a list of courses")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;
	
	# Construct a BeautifulSoup Object 
	soupHtml = BeautifulSoup(urlResponseObj.text, "html.parser")		

	# Extract out the list of courses
	allCoursesRaw = soupHtml.find("table",{'class': 'sub_table'})
	allCoursesTags = allCoursesRaw.find_all("td")
	
	# For every line that contains a course code, create a dictionary object with the fields, and save that dictionary object into a list
	courseTableFields = ["Course Code", "Organizing", "Venue", "Date", "Time", "Fee", "Vacancies", "Action"]
	allCourseDictionary = []
	courseDictionary = {}
	
	isCourse = False
	courseTableIndex = 1
	
	for rawLine in allCoursesTags:
		
		# Pre-processing of rawLine
		line = rawLine.get_text().replace("\t","").replace("\r\n","");
		
		if len(line.strip()) != 0:
			
			if re.search('^(C\d+)', line) is not None:	
				
				# Add the existing courseDictionary to the allCourseDictionary
				if bool(courseDictionary): #Dictionary that has keys will return True
					allCourseDictionary.append(courseDictionary)
					
				# Reinitialize the variables 
				courseDictionary = {}
				courseTableIndex = 1
				
				# A new course line item. Save previous course item to course code list 
				courseDictionary["course_code"] = line
				isCourse = True
			
			elif isCourse and courseTableIndex < len(courseTableFields):
				# Save the line with the right table index
				courseDictionary[courseTableFields[courseTableIndex]] = line
				courseTableIndex += 1
	
	# To add the last course into the allCourseDictionary list
	if bool(courseDictionary):
		allCourseDictionary.append(courseDictionary)

	return allCourseDictionary


def filterListOfCourses (listOfAllCourseDictionaries):

	# Iterate through the course dictionaries. For every course that has:
	#   1) vacancies, and 
	#   2) its first day later than today 
	# Process their individual course page, and add additional details into the course dictionary 
	# Always returns a filtered List 
	
	# Error Checking - empty list
	if listOfAllCourseDictionaries is None: 
		return [];
	
	for courseDictionary in listOfAllCourseDictionaries: 
		if ("Vacancies" in courseDictionary) and (courseDictionary["Vacancies"] != "No Vacancy") and (datetime.strptime(courseDictionary['Date'][0:9], '%d-%b-%y').date() > datetime.today().date()):
			courseDictionary["furtherProcess"] = True
		else: 
			courseDictionary["furtherProcess"] = False
				
	return listOfAllCourseDictionaries


def processAdditionalCourseDetails(courseDictionary): 

	# Format Class Content Section - separate Aim and Prerequisite
	class_content_tokens = courseDictionary["Class Content"].split(". ")
	
	# Format Class Requirements and Remarks Section - put into bullet form 
	courseDictionary["Class Requirements and Remarks"] = re.sub(r'\d\. ','\n- ',courseDictionary["Class Requirements and Remarks"]).replace(". PERSONAL","\n- PERSONAL").strip()
	
	# No processing required for Trainer and Trainer Qualifications Section 
	
	# Processing Class Details Section - only interested in Day/Time, Language, Online Registration Closing Date 
	courseDictionary['Dates'] = re.search(r'Day/Time: (.*) No. of Sessions:',courseDictionary["Class Details"]).group(1)
	courseDictionary['NumSessions'] = re.search(r'No. of Sessions: (\d)+ Venue:',courseDictionary["Class Details"]).group(1)
	courseDictionary['Class Size'] = re.search(r'Class Size: (.*) Language:',courseDictionary["Class Details"]).group(1)
	courseDictionary['Language'] = re.search(r'Language: (.*) Certification',courseDictionary["Class Details"]).group(1)
	courseDictionary['Language'] = re.search(r'Language: (.*) Certification',courseDictionary["Class Details"]).group(1)
	courseDictionary['RegClose'] = re.search(r'Registration Closing Date: (.*)$',courseDictionary["Class Details"]).group(1)	
	
	# Separate the dates up
	courseDictionary['Dates'] = re.sub(r'([AM|PM]) (\d\d)',r'\1\n\2',courseDictionary['Dates'])


def getAdditionalCourseDetails (courseDictionary):

	url = "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + courseDictionary["course_code"][1:] # Sliced to remove the preceeding 'C' of the course_code
	
	# Get Course Listing based on URL argument 
	urlResponseObj = requests.get(url)
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get more information on a specific course")
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;
		
	soupHtml = BeautifulSoup(urlResponseObj.text, "html.parser")
	courseDetails = soupHtml.find_all("h2",{'class': 'title_main2'})

	# Iterate through additional course details and add them to the course dictionary 
	for item in courseDetails:
		
		sectionTitle = " ".join(item.get_text().split()).replace(":","") #https://stackoverflow.com/questions/1546226
		sectionBody = " ".join(item.find_next("p").get_text().split())
		courseDictionary[sectionTitle] = sectionBody.strip()
	
	return processAdditionalCourseDetails(courseDictionary)


def formatForGitHubPages(courseDictionary): 
	fieldCourseCode = "[" + courseDictionary["course_code"] + "](https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + courseDictionary["course_code"][1:] + ")"
	
	fieldDates = ""
	
	fieldDatesTokens = courseDictionary["Dates"].split("\n")
	
	for i in range(0,len(fieldDatesTokens)):
		fieldDates += fieldDatesTokens[i][0:9] 
		if i < len(fieldDatesTokens)-1:
			fieldDates += "<br /><br />"
			
	fieldVenue = formatPAClubVenue(courseDictionary["Venue"])
	
	fieldVacancy = courseDictionary["Vacancies"]
	
	fieldRegclose = courseDictionary["RegClose"]
	
	return fieldCourseCode + "|" + fieldDates + "|" + fieldVenue + "|" + fieldVacancy + "<br /><br /> _(Register by: " + fieldRegclose + ")_"


def processCourses (type, url, operator, outputFile):
	print("Processing " + type)
	outputText = ""

	listOfAllCourses = getCourseListing(url, operator)
	filteredCourses = filterListOfCourses(listOfAllCourses)
	
	if not filteredCourses:
		outputText = "No upcoming courses yet|-|-|-\n"
	else: 
		for courseDictionary in filteredCourses:
			if courseDictionary["furtherProcess"]:
				getAdditionalCourseDetails(courseDictionary) # need this to get specific dates, regClose date 
				outputText += formatForGitHubPages(courseDictionary) + "\n"

	# Failsafe
	if outputText == "":
		outputText = "No upcoming courses yet|-|-|-\n"
	
	if not isSiteDown(): 
		f = open(outputFile, 'w')
		f.write(outputText)
		f.close()	
		print("Output file has been saved successfully")
	else: 
		print("Not overwritting output file " + outputFile + " as operator site is down")
		
	print("Finished " + type + "\n\n")
