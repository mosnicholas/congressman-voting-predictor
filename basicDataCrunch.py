
dataFile = "../data/bill_data.csv"

f = open(dataFile, 'r').read().split("\n")

def averageVotesWithParty():
	partyToAvg = {}
	numParty = {}
	for line in f:
		if line:
			line = line.split(",")
			party, votePct = int(line[0]), float(line[1])
			partyToAvg[party] = partyToAvg.get(party, 0) + votePct
			numParty[party] = numParty.get(party, 0) + 1
	return "Repulicans: " + str(partyToAvg[0]/numParty[0]) + ", Democrats: " + str(partyToAvg[1]/numParty[1])