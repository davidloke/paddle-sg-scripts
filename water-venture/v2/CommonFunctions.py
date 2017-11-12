def saveSiteDownStatus(status):
	f = open('./info-sitedown.out', 'w')
	f.write(str(status))
	f.close()
	
def resetSiteDownStatus():
	f = open('./info-sitedown.out', 'w')
	f.write("False")
	f.close()
	
def isSiteDown():
	sitedown_file = open('./info-sitedown.out', 'r')
	output_status = False
	if sitedown_file.read() == "True":
		output_status = True
	sitedown_file.close()
	return output_status
	
def formatPAClubVenue(course_venue):
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