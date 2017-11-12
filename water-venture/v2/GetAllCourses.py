from GetPACourses import processCourses
from CommonFunctions import resetSiteDownStatus

print ("Getting Operator Course Dates");	

resetSiteDownStatus()

processCourses("One Star Courses", "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727686", "PA", "out-onestar.txt")

processCourses("Two Star Courses", "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727691", "PA", "out-twostar.txt")

processCourses("Three Star Courses", "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727696", "PA", "out-threestar.txt")

processCourses("Three Star Assessments", "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727554", "PA", "out-threeassess.txt")

processCourses("Level 1 Coaching Courses", "https://one.pa.gov.sg/CRMSPortal/CRMSPortal.portal?_nfpb=true&_st=&_windowLabel=CRMSPortal_1&_urlType=render&_mode=view&wlpCRMSPortal_1_action=CMFShowClasses&_pageLabel=CRMSPortal_page_1&actionIndex=searchClassList&idProduct=727601", "PA", "out-level1coach.txt")

print ("Finished Processing Operator Course Dates");