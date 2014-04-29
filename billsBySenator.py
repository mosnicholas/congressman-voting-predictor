import json
import csv
from getData import *
from urllib import urlopen
from time import sleep

apiKeys = json.loads(open("api_keys.json", "r").read().replace("\n", "").replace("\t", ""))
congressApiKey = apiKeys["keys"]["Congress"]

billUrlNY = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/members/{0}/votes.json?api-key=" + congressApiKey
fileLoc = "../data/list_of_legislators.csv"
memberBioFileLoc = "../data/memberBios.json"
outputFile = "../data/bill_data.csv"
senatorInfo = json.loads(open("../data/memberBios.json", "r").read())

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
					newEntry = newEntry + billDescription
				else:
					newEntry += ["", "", "", "", ""]
				newEntry.append(changeAnswerToBinary(billInfo["position"]))
				billList.append(newEntry)
		else:
			print memberID
			continue
	print "ready to write to file"
	with open(outputFile, "w") as csvfile:
		features = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
 		for bill in billList:
 			features.writerow(bill)

def getBillSubjects(billURL):
	sleep(1) # we are limited by NyTimes' 2 queries per second. fml.
	apiReply = urlopen(billURL).read()
	try:
		return json.loads(apiReply)
	except:
		print "FAILED BILL FOR BILL @: " + billURL
		# print apiReply
		return

def getBillInfo(billURL):
	"""
		Given the bill URL (that constructData() will feed in), this function will return a response of the following format:
		["bill_id", "party_of_writer", {"subjects"}], where subjects will be a list of binary numbers in alphabetical order of possible subjects. 
	"""
	billAPIReply = getBillSubjects(billURL)
	if billAPIReply:
		try:
			print "getting bill info for bill @ url: " + billURL
			data = billAPIReply["results"][0]
			party_of_writer = changePartyToBinary(senatorInfo[data["sponsor_id"]]["party"])
			title = data["title"]
			congress_number = data["congress"]
			committee_number = makeCommitteeList(data["committees"])
			return [title, party_of_writer, congress_number, committee_number]
		except:
			print "FAILED AT GETBILLINFO: " + billURL
			return ["", "", "", "", ""]	
	else:
		return ["", "", "", "", ""]

def makeCommitteeList(description):
	description = str(description)
	if ("Agriculture" in description) or ("Nutrition" in description) or ("Forestry" in description):
		return 0
	elif "Appropriations" in description:
		return 1
	elif "Armed" in description:
		return 2
	elif "Banking" in description or "Housing" in description or "Urban" in description:
		return 3
	elif "Budget" in description:
		return 4
	elif "Commerce" in description or "Science" in description or "Transportation" in description:
		return 5
	elif "Energy" in description or "Natural" in description:
		return 6
	elif "Environment" in description:
		return 7
	elif "Finance" in description:
		return 8
	elif "Foreign" in description:
		return 9
	elif "Health" in description:
		return 10
	elif "Homeland" in description:
		return 11
	elif "Judiciary" in description:
		return 12
	elif "Rules" in description:
		return 13
	elif "Rules" in description:
		return 14
	elif "Business" in description:
		return 15
	elif "Veterans" in description:
		return 16
	elif "Indians" in description:
		return 17
	elif "Ethics" in description:
		return 18
	elif "Intelligence" in description:
		return 19
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