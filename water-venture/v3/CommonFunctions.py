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