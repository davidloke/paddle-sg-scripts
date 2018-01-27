from CommonFunctions import saveSiteDownStatus
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import json

expeditionUrlPrefix = "https://www.onepa.sg/event/details/"

def filterExpeditionListing(allExpeditionListing):

	# Iterate through the list. For every item that is:
	#   1) a class, 
	#   2) has vacancies, and 
	#   2) start date is later than today
	# save their URL into a new list 
	
	# Error Checking - empty list
	if allExpeditionListing is None: 
		return [];

	allFilteredExpeditionListing = []
	for expedition in allExpeditionListing:
		if expedition.labelname.string == "Event" and datetime.strptime(expedition.startdate.string, "%d %b %Y").date() > datetime.today().date() and expedition.maxvacancy.string != "Full":
			allFilteredExpeditionListing.append(expedition.code.string.lower())

	return allFilteredExpeditionListing


def processFilteredExpeditions (allFilteredExpeditionUrl): 
	
	# Error Checking - empty list
	if allFilteredExpeditionUrl is None: 
		return [];
	
	allExpeditionDetails = []
	
	for expeditionUrl in allFilteredExpeditionUrl: 

		expeditionBeautifulSoup = getIndividualExpeditionPage(expeditionUrlPrefix + expeditionUrl)
		
		allExpeditionDetails.append(extractInfoFromExpeditionPage(expeditionBeautifulSoup))
		
	return allExpeditionDetails


def getIndividualExpeditionPage (individualExpeditionUrl):
	
	if individualExpeditionUrl is None or individualExpeditionUrl == "":
		return BeautifulSoup("", "html.parser")

	# Get Expedition Listing based on URL argument 
	urlResponseObj = requests.get(individualExpeditionUrl)
	
	# Check if site is unavailable
	if (urlResponseObj.status_code != 200):
		print ("Operator site is unavailable")
		print ("    Step: Get a list of expeditions")
		print ("    Operator: " + operator)
		print ("    URL: " + url)
		saveSiteDownStatus(True)
		return BeautifulSoup("", "html.parser")
	
	# Construct a BeautifulSoup Object 
	return BeautifulSoup(urlResponseObj.text, "html.parser")
	
	
def extractInfoFromExpeditionPage (individualExpeditionSoup):
	
	extractedInfo = {}
	
	extractedInfo["expeditionRefCode"] = individualExpeditionSoup.find("div",{'class': 'detailUniqueCode'}).get_text()

	extractedInfo["title"] = individualExpeditionSoup.find("div",{"id": "divContentTitle"}).get_text()
	
	extractedInfo["expeditionUrl"] = individualExpeditionSoup.find("div",{'class': 'fb-share-button'})["data-href"]
	
	extractedInfo["classType"] = individualExpeditionSoup.find("div",{"id": "divContentTitle"}).get_text()
	
	# Get Expedition Details. List follows this order: [0]date/time, [1]num sessions, [2]class schedule, [3]location, [4]venue, [5]regClose, [6]vacancy
	expeditionDetails = individualExpeditionSoup.find_all("div", {'class': 'detailGridItem'})
	
	extractedInfo["dates"] = expeditionDetails[0].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["startDate"] = expeditionDetails[0].find("span",{'id': 'content_0_ltlEventStartDate'}).get_text()
	
	extractedInfo["venue"] = expeditionDetails[3].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["regClose"] = expeditionDetails[4].find("div",{'class': 'detailDescContent'}).get_text()
	
	extractedInfo["vacancy"] = expeditionDetails[5].find("div",{'class': 'vacancy'}).get_text() #for some reason, this is diferent
	
	return extractedInfo


def formatExpeditionsForHosting (allExpeditionDetails): 

	expeditionOutput = ""

	for c in allExpeditionDetails: 
		formatted = formatExpeditionForGitHub(c)
		
		if ("EXPEDITION" in c["classType"].upper()): 
			expeditionOutput +=  formatted + "\n"
			
	outputList = [expeditionOutput]
	
	# Special cleanup for empty expedition outputs
	while ("" in outputList): 
		outputList[outputList.index("")] = "No upcoming expeditions yet|-|-|-\n"
	
	return outputList


def formatExpeditionForGitHub (expeditionDictionary): 
	
	# Clean up the values 
	for key, value in expeditionDictionary.items():
		expeditionDictionary[key] = str(value).replace("\r\n","").replace("\n","").replace("\t","").strip()
	
	# Special clean up for dates 
	expeditionDictionary["dates"] = expeditionDictionary["dates"].replace("From", "").replace("To", "<br/><br/>to<br/><br/>")
	
	return expeditionDictionary["title"] + "<br />[" + expeditionDictionary["expeditionRefCode"] + "](" + expeditionDictionary["expeditionUrl"] + ")|" + expeditionDictionary["dates"] + "|" + expeditionDictionary["venue"].upper() + "|" + expeditionDictionary["vacancy"]# + "<br /><br /> _(Register by: " + expeditionDictionary["regClose"] + ")_"


def sortExpeditionsByDate (activityDictionaryList):
	for activityDictionary in activityDictionaryList:
		activityDictionary["startDateObj"] = datetime.strptime(activityDictionary['startDate'], "%d %b %Y").date()
		
	return sorted(activityDictionaryList, key=lambda k: k['startDateObj'])
