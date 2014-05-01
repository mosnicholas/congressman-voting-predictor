
dataFile = "../data/bill_data.csv"

f = open(dataFile, 'r').read().split("\n")

def averageVotesWithParty():
	partyToAvg = {}
	numParty = {}
	for line in f:
		if line:
			line = line.split("\t")
			party, votePct = int(line[0]), float(line[1])
			partyToAvg[party] = partyToAvg.get(party, 0) + votePct
			numParty[party] = numParty.get(party, 0) + 1
	return "Repulicans: " + str(partyToAvg[0]/numParty[0]) + ", Democrats: " + str(partyToAvg[1]/numParty[1])

def countNumSubjects():
	subjectCounts = {}
	for line in f:
		if line:
			line = line.split("\t")
			for subject in line[8:]:
				subject = subject.replace("\r", "")
				subjectCounts[subject] = subjectCounts.get(subject, 0) + 1
	return subjectCounts

def mapSubjectRepDem():
	subjectRepDemMap = {}
	for line in f:
		if line:
			line = line.split("\t")
			party = int(line[0])
			for subject in line[8:]:
				subject = subject.replace("\r", "")
				if subject not in subjectRepDemMap:
					subjectRepDemMap[subject] = {}
				subjectRepDemMap[subject][party] = subjectRepDemMap[subject].get(party, 0) + 1

	return subjectRepDemMap



