# -*- coding: utf-8 -*-
import json
from urllib import urlopen

"""
api_keys.json looks like:

{	"Application": "Congress Voting Predictor",
 	"keys": {
 		"Campaign Finance": "b816c374bd62130058804b508a0ec74e:12:67745626",
  		"Congress": "1d0c81540e364e97c86675e6f2e3167e:18:67745626"
  	}
}


resources for data:
https://www.govtrack.us/developers/data

http://developer.nytimes.com/docs/congress_api
"""

apiKeys = json.loads(open("api_keys.json", "r").read().replace("\n", "").replace("\t", ""))
congressApiKey = apiKeys["keys"]["Congress"]

baseMemberListURL = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/{0}/{1}/members.json?api-key=" + congressApiKey
baseMemberDataURL = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/members/{0}{1}.json?api-key=" + congressApiKey
baseRollCallURL = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/{0}/{1}/sessions/{2}/votes/{3}.json?api-key=" + congressApiKey
baseVotingDataURL = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/{0}/{1}/votes/{2}.json?api-key=" + congressApiKey
baseBillsDataURL = "http://api.nytimes.com/svc/politics/v3/us/legislative/congress/{0}{1}/bills/{2}.json?api-key=" + congressApiKey
	# if {1} is specified, this it refers to the above {1} (house | senate) & {2} refers to the following:
		# The {2} signifies what type of bill – introduced | updated | passed | major --> straightforward except major - this is deemed by NyTimes to be important bills
		# For more info, look here: http://developer.nytimes.com/docs/congress_api#h3-bills
	# if {1} is not specified, we are looking at bill details.
		# The {2} signifies the bill-id
		# For more info, look here: http://developer.nytimes.com/docs/congress_api#h3-bill-details

def helperURLGet(apiURL):
	data = urlopen(apiURL).read()
	return json.loads(data)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param chamber is (senate | house) - this is the chamber we are interested in finding out more about
# Example calls: getMemberList(102, 'house') will return the house representatives for the 102nd congress
def getMemberList(congressNumber, chamber):
	apiURL = baseMemberListURL.format(str(congressNumber), chamber)
	return helperURLGet(apiURL)

# The following are functions to retrieve general data about members of congress

# @param memberID is the ID for the member of congress who is of interest
def getMemberBio(memberID):
	apiURL = baseMemberDataURL.format(str(memberID), "")
	return helperURLGet(apiURL)

# @param memberID is the ID for the member of congress who is of interest
def getMemberVotingHistory(memberID):
	apiURL = baseMemberDataURL.format(str(memberID), "/votes")
	return helperURLGet(apiURL)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param chamber is (senate | house) - this is the chamber we are interested in finding out more about
# @param sessionNumber is the _
# @param rollCallNumber is the _
def getRollCallVotes(congressNumber, chamber, sessionNumber, rollCallNumber):
	apiURL = baseRollCallURL.format(str(congressNumber), chamber, str(sessionNumber), str(rollCallNumber))
	return helperURLGet(apiURL)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param chamber is (senate | house) - this is the chamber we are interested in finding out more about
# @param voteType is the type of the vote - (party | missed | loneno | perfect) --> corresponding to voting w/ party, voting attendance, only no vote, the members who voted only yes/no on every vote
	# For more info, look here: http://developer.nytimes.com/docs/congress_api#h3-votes-by-type
def getVotingData(congressNumber, chamber, voteType):
	apiURL = baseVotingDataURL.format(str(congressNumber), chamber, voteType)
	return helperURLGet(apiURL)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param chamber is (senate | house) - this is the chamber we are interested in finding out more about
# @param voteType is the type of the vote - (party | missed | loneno | perfect) --> corresponding to voting w/ party, voting attendance, only no vote, the members who voted only yes/no on every vote
	# For more info, look here: http://developer.nytimes.com/docs/congress_api#h3-votes-by-type
def getBillsData(congressNumber, chamber, voteType):
	apiURL = baseBillsDataURL.format(str(congressNumber), "/" + chamber, voteType)
	return helperURLGet(apiURL)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param billID is the ID of the bill we are interested in - e.g. hr2004
def getBillsDetails(congressNumber, billID):
	apiURL = baseBillsDataURL.format(str(congressNumber), "", billID)
	return helperURLGet(apiURL)

# @param congressNumber is the number of the congress we are interested in (e.g. the 105th congress)
# @param billID is the ID of the bill we are interested in - e.g. hr2012
def getBillsSubjectTerms(congressNumber, billID, resource):
	apiURL = baseBillsDataURL.format(str(congressNumber), "", billID + "/" + resource)
	return helperURLGet(apiURL)
