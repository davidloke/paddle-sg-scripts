print ("Getting Kayak Course Dates")

from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup

maintenance_code = "-1"

def formatContent(course_dictionary): 
	# Format Class Content Section - separate Aim and Prerequisite
	class_content_tokens = course_dictionary["Class Content"].split(". ")
	
	# Format Class Requirements and Remarks Section - put into bullet form 
	course_dictionary["Class Requirements and Remarks"] = re.sub(r'\d\. ','\n- ',course_dictionary["Class Requirements and Remarks"]).replace(". PERSONAL","\n- PERSONAL").strip()
	
	# No processing required for Trainer and Trainer Qualifications Section 
	
	# Processing Class Details Section - only interested in Day/Time, Language, Online Registration Closing Date 
	course_dictionary['Dates'] = re.search(r'Day/Time: (.*) No. of Sessions:',course_dictionary["Class Details"]).group(1)
	course_dictionary['NumSessions'] = re.search(r'No. of Sessions: (\d)+ Venue:',course_dictionary["Class Details"]).group(1)
	course_dictionary['Class Size'] = re.search(r'Class Size: (.*) Language:',course_dictionary["Class Details"]).group(1)
	course_dictionary['Language'] = re.search(r'Language: (.*) Certification',course_dictionary["Class Details"]).group(1)
	course_dictionary['Language'] = re.search(r'Language: (.*) Certification',course_dictionary["Class Details"]).group(1)
	course_dictionary['RegClose'] = re.search(r'Registration Closing Date: (.*)$',course_dictionary["Class Details"]).group(1)	
	
	# Separate the dates up
	course_dictionary['Dates'] = re.sub(r'([AM|PM]) (\d\d)',r'\1\n\2',course_dictionary['Dates'])
	
def outputCourseDetails(course_dictionary):
	print("\nCourse Code:\n" + course_dictionary["course_code"])
	print("\nClass Details:\n" + course_dictionary["Class Content"])
	print("\nClass Requirements and Remarks:\n" + course_dictionary["Class Requirements and Remarks"])
	print("\nTrainer:\n" + course_dictionary["Trainer"])
	print("\nDates:\n" + course_dictionary["Dates"])
	print("\nSessions:\n" + course_dictionary["NumSessions"])
	print("\nLanguage:\n" + course_dictionary["Language"])
	print("\nRegistration Close Date:\n" + course_dictionary["RegClose"])
	print("-----------------------------------------------------------------")

def formatClubVenue(course_venue):
	prefix = "PA Water-Venture "
	if "bedok" in course_venue.lower():
		return prefix + "(Bedok Reservoir)"
	elif "changi" in course_venue.lower():
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

def formatForGitHubPages(course_dictionary): 
	field_coursecode = "[" + course_dictionary["course_code"] + "](https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + course_dictionary["course_code"][1:] + ")"
	field_dates = ""
	field_dates_tokens = course_dictionary["Dates"].split("\n")
	for i in range(0,len(field_dates_tokens)):
		field_dates += field_dates_tokens[i][0:9] 
		if i < len(field_dates_tokens)-1:
			field_dates += "<br /><br />"
	field_venue = formatClubVenue(course_dictionary["Venue"])
	field_vacancy = course_dictionary["Vacancies"]
	field_regclose = course_dictionary["RegClose"]
	return field_coursecode + "|" + field_dates + "|" + field_venue + "|" + field_vacancy + "<br /><br /> _(Register by: " + field_regclose + ")_"



def processIndividualCourse(course_dictionary):
	
	# Make individual course page into a beautiful soup
	ind_course_page = requests.get("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=ACMParticipantMaintain&_pageLabel=CRMSPortal_page_1&IdProdInst=" + course_dictionary["course_code"][1:])
	course_page_html = BeautifulSoup(ind_course_page.text, "html.parser")
	
	course_details = course_page_html.find_all("h2",{'class': 'title_main2'})
	
	for item in course_details: 
		section_title = " ".join(item.get_text().split()).replace(":","") #https://stackoverflow.com/questions/1546226
		section_body = " ".join(item.find_next("p").get_text().split())
		course_dictionary[section_title] = section_body.strip()
		
	formatContent(course_dictionary)
	
	return formatForGitHubPages(course_dictionary)
	
	
def getCourseListing(url, output_file):
	
	##########
	# Part 1 - Data Ingestion
	##########

	all_course_page = requests.get(url)
	pagehtml = BeautifulSoup(all_course_page.text, "html.parser")

	# Check if page is under maintenance
	if "We wish to inform that the website is under a routine maintenance." in str(pagehtml):
		print("Operator site is under maintenace")
		return maintenance_code

	# Extract out the list of courses
	allcourses = pagehtml.find("table",{'class': 'sub_table'})
	allcourses_td = allcourses.find_all("td")
	
	##########
	# Part 2 - Data Extraction
	##########

	#Check if the line is a course code. If yes, save the course details
	course_table_fields = ["Course Code", "Organizing", "Venue", "Date", "Time", "Fee", "Vacancies", "Action"]
	all_course_dictionary = []
	course_dictionary = {}
	
	isCourse = False
	course_table_index = 1
	
	for raw_line in allcourses_td:
		
		# Pre-process
		line = raw_line.get_text().replace("\t","").replace("\r\n","");
		
		if len(line.strip()) != 0:
			
			if re.search('^(C\d+)', line) is not None:	
				# Add the existing course_dictionary to the all_course_dictionary
				if "course_code" in course_dictionary:
					all_course_dictionary.append(course_dictionary)
				course_dictionary = {}
				course_table_index = 1
				
				# A new course line item. Save previous course item to course code list 
				course_dictionary["course_code"] = line
				isCourse = True
			
			elif isCourse and course_table_index < len(course_table_fields):
				course_dictionary[course_table_fields[course_table_index]] = line
				course_table_index += 1
	
	all_course_dictionary.append(course_dictionary)

	##########
	# Part 3 - Data Extraction and Cleansing for each course
	##########

	# For each course code, go to the individual course page and extract the details 
	output_string = ""
	for course in all_course_dictionary: 
		if bool(course): #prevent this from running if no courses in that one.pa.gov.sg page
			if ("Vacancies" in course) and (course["Vacancies"] != "No Vacancy") and (datetime.strptime(course['Date'][0:9], '%d-%b-%y').date() > datetime.today().date()):
				# Course must have vacancy, and the start date must not have passed the current date, before we go query more details
				output_string += processIndividualCourse(course) + "\n"

	if output_string != "":	
		return output_string
	else:
		return "No upcoming courses yet|-|-|-\n"
			
# Get 1 Star Course Dates
print("Processing 1star courses")
onestar_formatted_string = getCourseListing("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727686", "1s-dates.txt")

# Get 2 Star Course Dates
print("Processing 2star courses")
twostar_formatted_string = getCourseListing("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727691", "2s-dates.txt")

# Get 3 Star Course Dates 
print("Processing 3star courses")
threestar_formatted_string = getCourseListing("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727696", "3s-dates.txt")

# Get 3 Star Assessment Dates
print("Processing 3star assessment")
threestarassess_formatted_string = getCourseListing("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727554", "3sa-dates.txt")

# Get L1 Coach Course Dates
print("Processing level 1 coaching courses")
level1coach_formatted_string = getCourseListing("https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727601", "l1-dates.txt")

isOperatorSiteDown = 0

# Save the course formats
if onestar_formatted_string != maintenance_code:
	f = open('./out-onestar.txt', 'w')
	f.write(onestar_formatted_string)
	f.close()
else: 
	isOperatorSiteDown = 1
	print("Not saving out-onestar.txt course output")

if twostar_formatted_string != maintenance_code:
	f = open('./out-twostar.txt', 'w')
	f.write(twostar_formatted_string)
	f.close()
else: 
	isOperatorSiteDown = 1
	print("Not saving out-twostar.txt course output")

if threestar_formatted_string != maintenance_code:
	f = open('./out-threestar.txt', 'w')
	f.write(threestar_formatted_string)
	f.close()
else: 
	isOperatorSiteDown = 1
	print("Not saving out-threestar.txt course output")

if threestarassess_formatted_string != maintenance_code:
	f = open('./out-threeassess.txt', 'w')
	f.write(threestarassess_formatted_string)
	f.close()
else:
	isOperatorSiteDown = 1
	print("Not saving out-threeassess.txt course output")

if level1coach_formatted_string != maintenance_code:
	f = open('./out-level1coach.txt', 'w')
	f.write(level1coach_formatted_string)
	f.close()
else:
	isOperatorSiteDown = 1
	print("Not saving out-level1coach.txt course output")

f = open('./info-sitedown.out', 'w')
if isOperatorSiteDown == 0:
	f.write("false")
else: 
	f.write("true")
f.close()

print ("Finished Processing Kayak Course Dates")