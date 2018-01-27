from GetPACourses import getAllCourseListing, filterCourseListing, processFilteredCourses, formatInfoForHosting, sortCoursesByDate
from GetPAExpeditions import filterExpeditionListing, processFilteredExpeditions, formatExpeditionsForHosting, sortExpeditionsByDate

from CommonFunctions import resetSiteDownStatus, isSiteDown

print ("Getting Operator Course Dates");	

resetSiteDownStatus()

# Get all listed items (i.e. Courses/Events) from the site 
allListings = getAllCourseListing ("https://www.onepa.sg/sitecore/shell/WebService/Card.asmx/GetCategoryCard", "PA")

#### FOR PA COURSES ####
# Filter to remove courses URLs based on criteria (vacancy and date)
filteredCourses = filterCourseListing(allListings)

# Extract more information about the course from their individual course pages 
processedCourses = processFilteredCourses(filteredCourses)

# Sort the courses 
sortedCourses = sortCoursesByDate(processedCourses)

# Format the courses for hosting on Github Pages 
formattedCourses = formatInfoForHosting (sortedCourses)
outputFileList = ["out-onestar.txt", "out-twostar.txt", "out-threestar.txt", "out-threeassess.txt","out-fourstar.txt", "out-level1coach.txt", "out-activity.txt"]

if not isSiteDown(): 

	for formattedOutput, fileName in zip(formattedCourses, outputFileList):
		f = open(fileName, 'w')
		f.write(formattedOutput)
		f.close()	
	
else: 
	print("Not overwritting Course output file as operator site is down")


print ("Finished Processing Operator Course Dates");

#### FOR PA EXPEDITIONS  ####

print ("Getting Operator Expedition Dates");

# Filter to remove Expedition URLs based on criteria (vacancy and date)
filteredExpeditions = filterExpeditionListing(allListings)

# Extract more information about the expedition from their individual event pages 
processedExpeditions = processFilteredExpeditions(filteredExpeditions)

# Sort the expeditions
sortedExpeditions = sortExpeditionsByDate(processedExpeditions)

# Format the expeditionsfor hosting on Github Pages 
formattedExpeditions = formatExpeditionsForHosting (sortedExpeditions)
outputFileList = ["out-expedition.txt"]

if not isSiteDown(): 

	for formattedOutput, fileName in zip(formattedExpeditions, outputFileList):
		f = open(fileName, 'w')
		f.write(formattedOutput)
		f.close()	
	
else: 
	print("Not overwritting Course output file as operator site is down")


print ("Finished Processing Operator Expeditions");