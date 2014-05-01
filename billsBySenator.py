import json
import csv
from getData import *
from urllib import urlopen
from time import sleep

senatorInfo = json.loads(open("../data/memberBios.json", "r").read())
subjectMapping = json.loads(open("../data/subjectMapping.json", "r").read().replace("\n", "").replace("\t", ""))
apiKeys = json.loads(open("api_keys.json", "r").read().replace("\n", "").replace("\t", ""))
congressApiKey = apiKeys["keys"]["Congress"]

billUrlNY = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/members/{0}/votes.json?api-key=" + congressApiKey
fileLoc = "../data/list_of_legislators.csv"
memberBioFileLoc = "../data/memberBios.json"
outputFile = "../data/bill_data.csv"

# this maps subject to value to be able to use it as a point to split on in decision trees.
mapping = {"agriculture and food":0,"animals":1,"armed forces and national security":2,"arts, culture, religion":3,"civil rights and liberties, minority issues":4,"commerce":5,"congress":6,"crime and law enforcement":7,"economics and public finance":8,"education":9,"emergency management":10,"energy":11,"environmental protection":12,"families":13,"finance and financial sector":14,"foreign trade and international finance":15,"government operations and politics":16,"health":17,"housing and community development":18,"immigration":19,"international affairs":20,"labor and employment":21,"law":22,"native americans":23,"private legislation":24,"public lands and natural resources":25,"science, technology, communications":26,"social sciences and history":27,"social welfare":28,"sports and recreation":29,"taxation":30,"transportation and public works":31,"water resources development":32}

def getBillsBySenator(memberID):
	sleep(1) # we are limited by NyTimes' 2 queries per second. fml.
	memberURL = billUrlNY.format(memberID)
	apiReply = urlopen(memberURL).read()
	try:
		return json.loads(apiReply)
	except:
		print "FAILED MEMBER DATA CALL FOR MEMBER @ URL: " + memberURL
		# print apiReply
		return

def constructData():
	"""
		This will return a csv file of a list of data points with a row of the format:
		yes / no are binary encoded
		bill number is stripped of spaces

		["bill number", "yes/no", "memberID", "bill Description", "subjects", "election_year", "house/Senate"]
	"""
	billSavedDescriptions = {}
	billList = []
	for memberID in senatorInfo.keys():
		voteData = getBillsBySenator(memberID)
		if voteData:
			print "grabbing bills for senator: " + str(memberID)
			for i in xrange(int(voteData["results"][0]["total_votes"])):
				newEntry = []
				newEntry.append(changePartyToBinary(senatorInfo[memberID]["party"]))
				newEntry.append(senatorInfo[memberID]["votes_with_party_pct"])
				newEntry.append(senatorInfo[memberID]["state"])
				billInfo = voteData["results"][0]["votes"][i]
				if billInfo["bill"]:
					number = formatConvert(billInfo["bill"]["number"])
					if number in billSavedDescriptions.keys():
						billDescription = billSavedDescriptions[number]
					else:
						billDescription = getBillInfo(changeURL(billInfo["bill"]["bill_uri"]))
						billSavedDescriptions[number] = billDescription

					newEntry.append(changeAnswerToBinary(billInfo["position"]))
					
					if billDescription:
						newEntry = newEntry + billDescription
						billList.append(newEntry)
		else:
			print memberID
			continue
	print "ready to write to file"
	with open(outputFile, "w") as csvfile:
		features = csv.writer(csvfile, delimiter='\t')
 		for bill in billList:
 			features.writerow(bill)

def getBillDataAPI(billURL):
	sleep(1) # we are limited by NyTimes' 2 queries per second. fml.
	apiReply = urlopen(billURL).read()
	try:
		return json.loads(apiReply)
	except:
		print "FAILED BILL FOR BILL @: " + billURL
		# print apiReply
		return

def findHeadTopic(subject):
	for k, v in subjectMapping.iteritems():
		if (subject in v) or (subject == k):
			return k
	return None

def getSubjectsBill(subjectList):
	generalSubjects = []
	for subject in subjectList:
		subjectName = subject["name"].lower().replace("&#x27;", "'")
		headTopic = findHeadTopic(subjectName)
		if headTopic:	headTopic = subjectToInt(headTopic)
		if headTopic and (headTopic not in generalSubjects):
			generalSubjects.append(headTopic)
	return generalSubjects

def getBillInfo(billURL):
	"""
		Given the bill URL (that constructData() will feed in), this function will return a response of the following format:
		["bill_id", "party_of_writer", {"subjects"}], where subjects will be a list of binary numbers in alphabetical order of possible subjects. 
	"""
	billAPIReply = getBillDataAPI(billURL)
	if billAPIReply:
		try:
			print "getting bill info for bill @ url: " + billURL
			data = billAPIReply["results"][0]
			party_of_writer = changePartyToBinary(senatorInfo[data["sponsor_id"]]["party"])
			title = data["title"]
			congress_number = data["congress"]
			committee_number = makeCommitteeList(data["committees"])
			subjects = getSubjectsBill(data["subjects"])
			return [title, party_of_writer, congress_number, committee_number] + subjects
		except:
			print "FAILED AT GETBILLINFO: " + billURL
			return None
	else:
		return None

def subjectToInt(subject):
	return mapping[subject]

def makeCommitteeList(description):
	description = str(description).lower()
	if ("agriculture" in description) or ("nutrition" in description) or ("forestry" in description):
		return 0
	elif "appropriations" in description:
		return 1
	elif "armed" in description:
		return 2
	elif "banking" in description or "housing" in description or "urban" in description:
		return 3
	elif "budget" in description:
		return 4
	elif "commerce" in description or "science" in description or "transportation" in description:
		return 5
	elif "energy" in description or "natural" in description:
		return 6
	elif "environment" in description:
		return 7
	elif "finance" in description:
		return 8
	elif "foreign" in description:
		return 9
	elif "health" in description:
		return 10
	elif "homeland" in description:
		return 11
	elif "judiciary" in description:
		return 12
	elif "rules" in description:
		return 13
	elif "business" in description:
		return 14
	elif "veterans" in description:
		return 15
	elif "indians" in description:
		return 16
	elif "ethics" in description:
		return 17
	elif "intelligence" in description:
		return 18
	else:
		return -1

# Helper functions
def formatConvert(billNum):
	return billNum.lower().replace(" ", "").replace(".", "")

def changeURL(url):
	return url.replace(".json", "/subjects.json?api-key=" + congressApiKey)

def changeAnswerToBinary(yes_no):
	if str(yes_no.lower()) == "no":
		return 0
	return 1

def changePartyToBinary(red_blue):
	if str(red_blue) == "D":
		return 1
	return 0

def filterIrrelevantFeats(memberBio):
 	irrelevantFeats = ["twitter_account", "thomas_id", "dw_nominate", "next_election", "url", "facebook_id", "domain", "seniority", "ideal_point", "facebook_account", "district", "middle_name", "rss_url"]
 	for f in irrelevantFeats:
 		memberBio.pop(f, None)

# To be called once - constructs json of members -> member info
def constructMemberIDList(congressNumber, chamber):
	listOfMembers = getMemberList(congressNumber, chamber)
	membersToBio = {}
	for member in listOfMembers["results"][0]["members"]:
		filterIrrelevantFeats(member)
		membersToBio[member["id"]] = member

	f = open(memberBioFileLoc.replace(".json", chamber + ".json"), 'w')
	print >> f, membersToBio
	f.close()
	
	return membersToBio
