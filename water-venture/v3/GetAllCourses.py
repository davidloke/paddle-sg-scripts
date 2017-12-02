from GetPACourses import getAllCourseListing, filterCourseListing, processFilteredCourses, formatInfoForHosting, sortCoursesByDate
from CommonFunctions import resetSiteDownStatus, isSiteDown

print ("Getting Operator Course Dates");	

resetSiteDownStatus()

# Get all listed courses URLs from the site 
allCourseListing = getAllCourseListing ("https://www.onepa.sg/sitecore/shell/WebService/Card.asmx/GetCategoryCard", "PA")

# Filter to remove courses URLs based on criteria (vacancy and date)
filteredCourses = filterCourseListing(allCourseListing)

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
	print("Not overwritting output file as operator site is down")


print ("Finished Processing Operator Course Dates");