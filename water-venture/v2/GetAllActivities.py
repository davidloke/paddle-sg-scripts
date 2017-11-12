from CommonFunctions import resetSiteDownStatus, isSiteDown
from GetPAOutletActivities import processOutletActivities, formatForGitHubPages, sortListOfActivitiesByDate

resetSiteDownStatus()

url = "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=action&wlpCRMSPortal_1_action=CMFCategoryActivitySelection&_pageLabel=CRMSPortal_page_1"
operator = "PA"

allOutletActivityList = []
allOutletActivityList += processOutletActivities ("Bedok Reservoir", url, "1395630", operator)
allOutletActivityList += processOutletActivities ("Changi", url, "1395610", operator)
allOutletActivityList += processOutletActivities ("East Coast", url, "1395614", operator)
allOutletActivityList += processOutletActivities ("Jurong Lake", url, "1395633", operator)
allOutletActivityList += processOutletActivities ("Kallang", url, "1395618", operator)
allOutletActivityList += processOutletActivities ("Pasir Ris", url, "1395622", operator)
allOutletActivityList += processOutletActivities ("Sembawang", url, "11166460", operator)
allOutletActivityList += processOutletActivities ("Water Venture Section", url, "1397375", operator)
allOutletActivityList += processOutletActivities ("Lower Seletar", url, "11021193", operator)
sortedAllOutletActivityList = sortListOfActivitiesByDate(allOutletActivityList)

# Filter the activities to separate into 4 Star, Expeditions, and other types of activities 
activityFormattedString = ""
expeditionFormattedString = ""
fourstarFormattedString = ""

for activity in sortedAllOutletActivityList:
	
	formattedOutput = formatForGitHubPages(activity)
	
	if (("expedition" in formattedOutput.lower()) or ("discovery series" in formattedOutput.lower())):
		expeditionFormattedString += formattedOutput + "\n"
	elif ("4 star" in formattedOutput.lower()):
		fourstarFormattedString += formattedOutput + "\n"
	else:
		activityFormattedString += formattedOutput + "\n"

# Code to handle no records found
if activityFormattedString == "":	
	activityFormattedString = "No upcoming activities yet|-|-|- \n"

if expeditionFormattedString == "":	
	expeditionFormattedString = "No upcoming expeditions yet|-|-|- \n"

if fourstarFormattedString == "":	
	fourstarFormattedString = "No upcoming courses yet|-|-|- \n"

# If the operator site is not down, write to file
if not isSiteDown(): 	
	f = open('./out-activity.txt', 'w')
	f.write(activityFormattedString)
	f.close()

	f = open('./out-expedition.txt', 'w')
	f.write(expeditionFormattedString)
	f.close()

	f = open('./out-fourstar.txt', 'w')
	f.write(fourstarFormattedString)
	f.close()
	
	print("Output file has been saved successfully")
else: 
	print("Not overwritting output files as operator site is down")