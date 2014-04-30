from bs4 import BeautifulSoup as bs
import json
from re import sub

subjectMaps = "../data/subjectMappings.html"
outputFile = "../data/subjectMapping.json"

f = open(subjectMaps, 'r').read()

def getSubjectHeads(soup):
	listOfTitles = []
	titles = soup.find_all("p", attrs={"class": "subheaderblack"})
	index = 0
	for t in titles:
		listOfTitles.append(cleanTitle(t.text))
		index += 1
	return listOfTitles

def cleanTitle(text):
	return ' '.join(text.replace("\n", "").split()).lower()

def cleanSubTitle(text):
	text = sub(r" \(added \d{1,2}/\d{1,2}/\d{2}\)", "", text)
	text = sub(r" \(changed \d{1,2}/\d{1,2}/\d{2}\)", "", text)
	return cleanTitle(text)

def makeMapping():
	soup = bs(f)
	titles = getSubjectHeads(soup)
	subjectToFan = {}

	for t in titles:
		subjectToFan[t] = []

	indexCounter = 0
	paragraphs = soup.find_all("p", attrs={"class":""})
	for p in paragraphs:
		p = p.contents
		headTitle = titles[indexCounter]
		
		if headTitle == "private legislation": # Private Legislation has no subtopics, need special case for this guy
			indexCounter += 1
			headTitle = titles[indexCounter]

		for subTopic in p:
			subTopic = cleanSubTitle(str(subTopic))
			if subTopic != "<br/>":
				subjectToFan[headTitle].append(subTopic)
		indexCounter += 1

	with open(outputFile, 'wb') as of:
		json.dump(subjectToFan, of)
	return subjectToFan