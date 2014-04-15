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
# The {0} will be used as a string formatting to change the congress number

# @param chamber is senate | house - this is the chamber we are interested in finding out more about
# Example calls: getMemberList(102, 'house') will return the house representatives for the 102nd congress
def getMemberList(congressNumber, chamber):
	# This api call returns a json object
	apiURL = baseMemberListURL.format(str(congressNumber), chamber)
	memberList = urlopen(apiURL).read()
	return json.loads(memberList)


# The following are functions to retrieve general data about members of congress
def getMemberBio(memberID):
	# This api call returns a json object
	apiURL = baseMemberDataURL.format(str(memberID), "")
	senatorData = urlopen(apiURL).read()
	return json.loads(senatorData)

def getMemberVotingHistory(memberID):
	# This api call returns a json object
	apiURL = baseMemberDataURL.format(str(memberID), "/votes")
	senatorData = urlopen(apiURL).read()
	return json.loads(senatorData)

