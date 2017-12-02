from CommonFunctions import saveSiteDownStatus
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json

courseUrlPrefix = "https://www.onepa.sg/class/details/"

def getAllCourseListing(url, operator):
	
	cookieResponseObj = requests.post("https://www.onepa.sg/cat/kayaking")

	# Check if site is unavailable
	if (cookieResponseObj.status_code != 200 or "unavailable" in cookieResponseObj.text):
		print ("Operator site is unavailable")
		print ("    Step: Get cookie from site")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;


	payload = {"cat":"kayaking", "subcat":"", "sort":"", "filter":"[filter]", "cp":"[cp]"}
	headers_custom = {"Content-Type":"application/json; charset=UTF-8"}
	
	# Get Course Listing based on URL argument 
	urlResponseObj = requests.post(url, data = json.dumps(payload), headers = headers_custom, cookies = cookieResponseObj.cookies )
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get a list of courses")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return;
	
	# Extract the course listing in the Json key "d"
	urlResponseJson = json.loads(urlResponseObj.text)
	
	# Construct a BeautifulSoup Object 
	soupHtml = BeautifulSoup(urlResponseJson["d"], "html.parser")
	
	# Extract out an array of courses
	allCourseListing = soupHtml.find_all("table1")
	
	return allCourseListing


def filterCourseListing (allCourseListing):

	# Iterate through the list. For every item that is:
	#   1) a class, 
	#   2) has vacancies, and 
	#   2) start date is later than today
	# save their URL into a new list 
	
	# Error Checking - empty list
	if allCourseListing is None: 
		return [];
	
	allFilteredCourseListing = []
	for course in allCourseListing: 
		if course.labelname.string == "Class" and datetime.strptime(course.startdate.string, "%d %b %Y").date() > datetime.today().date() and course.maxvacancy.string != "Full":
			allFilteredCourseListing.append(course.code.string.lower())
			
	return allFilteredCourseListing


def processFilteredCourses (allFilteredCourseUrl): 
	
	# Error Checking - empty list
	if allFilteredCourseUrl is None: 
		return [];
	
	allCourseDetails = []
	
	for courseUrl in allFilteredCourseUrl: 
		
		courseBeautifulSoup = getIndividualCoursePage(courseUrlPrefix + courseUrl)
		
		allCourseDetails.append(extractInfoFromCoursePage(courseBeautifulSoup))
		
	return allCourseDetails


def getIndividualCoursePage (individualCourseUrl):
	
	if individualCourseUrl is None or individualCourseUrl == "":
		return BeautifulSoup("", "html.parser")

	# Get Course Listing based on URL argument 
	urlResponseObj = requests.get(individualCourseUrl)
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get a list of courses")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return BeautifulSoup("", "html.parser")
	
	# Construct a BeautifulSoup Object 
	return BeautifulSoup(urlResponseObj.text, "html.parser")
	
	
def extractInfoFromCoursePage (individualCourseSoup):
	
	extractedInfo = {}
	
	extractedInfo["courseRefCode"] = individualCourseSoup.find("div",{'class': 'detailUniqueCode'}).get_text()

	extractedInfo["title"] = individualCourseSoup.find("div",{"id": "divContentTitle"}).get_text()
	
	extractedInfo["courseUrl"] = individualCourseSoup.find("div",{'class': 'fb-share-button'})["data-href"]
	
	extractedInfo["classType"] = individualCourseSoup.find("div",{"id": "divContentTitle"}).get_text()
	
	# Get Course Details. List follows this order: [0]date/time, [1]num sessions, [2]class schedule, [3]location, [4]venue, [5]regClose, [6]vacancy
	courseDetails = individualCourseSoup.find_all("div", {'class': 'detailGridItem'})
	
	extractedInfo["dates"] = courseDetails[0].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["startDate"] = courseDetails[0].find("span",{'id': 'content_0_ltlCourseStartDate'}).get_text()
	
	extractedInfo["venue"] = courseDetails[3].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["regClose"] = courseDetails[5].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["vacancy"] = courseDetails[6].find("div",{'class': 'vacancy'}).get_text() #for some reason, this is diferent
	
	return extractedInfo


def formatInfoForHosting (allCourseDetails): 

	oneStarOutput = ""
	twoStarOutput = ""
	threeStarOutput = ""
	threeStarAssessmentOutput = ""
	fourStarOutput = ""
	levelOneOutput = ""
	activityOutput = ""

	for c in allCourseDetails: 
		formatted = formatCourseForGitHub(c)
		
		if (c["classType"].upper() == "KAYAKING 1 STAR AWARD"): 
			oneStarOutput +=  formatted + "\n"
		elif (c["classType"].upper() == "KAYAKING 2 STAR AWARD"): 
			twoStarOutput +=  formatted + "\n"
		elif (c["classType"].upper() == "KAYAKING 3 STAR AWARD"): 
			threeStarOutput +=  formatted + "\n"
		elif (c["classType"].upper() == "KAYAKING 3 STAR ASSESSMENT"): 
			threeStarAssessmentOutput +=  formatted + "\n"
		elif (c["classType"].upper() == "KAYAKING 4 STAR AWARD"): 
			fourStarOutput +=  formatted + "\n"
		elif (c["classType"].upper() == "KAYAKING LEVEL 1 COACH TRAINING COURSE"): 
			levelOneOutput +=  formatted + "\n"
		else: 
			activityOutput += "[" + c["title"] + " " + formatted[1:] + "\n"
	
	outputList = [oneStarOutput, twoStarOutput, threeStarOutput, threeStarAssessmentOutput, fourStarOutput, levelOneOutput, activityOutput]
	
	# Special cleanup for empty course outputs
	while ("" in outputList): 
		outputList[outputList.index("")] = "No upcoming courses yet|-|-|-\n"
	
	return outputList


def formatCourseForGitHub (courseDictionary): 
	
	# Clean up the values 
	for key, value in courseDictionary.items():
		courseDictionary[key] = str(value).replace("\r\n","").replace("\n","").replace("\t","").strip()
	
	# Special clean up for dates 
	courseDictionary["dates"] = courseDictionary["dates"].replace("From", "").replace("To", "<br/><br/>to<br/><br/>")
	
	return "[" + courseDictionary["courseRefCode"] + "](" + courseDictionary["courseUrl"] + ")|" + courseDictionary["dates"] + "|" + courseDictionary["venue"] + "|" + courseDictionary["vacancy"]# + "<br /><br /> _(Register by: " + courseDictionary["regClose"] + ")_"


def sortCoursesByDate (activityDictionaryList):
	for activityDictionary in activityDictionaryList:
		activityDictionary["startDateObj"] = datetime.strptime(activityDictionary['startDate'], "%d %b %Y").date()
		
	return sorted(activityDictionaryList, key=lambda k: k['startDateObj'])