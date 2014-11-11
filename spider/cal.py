import math
def e_distance(x, y, attr): #input bigDict[x], bigDict[y], attr
	result = 0
	outcome=list()
	for a, b in attr.items():
		result += math.pow((x[a]-y[a]), 2)
		outcome.append(math.pow((x[a]-y[a]), 2))
	result=math.sqrt(result)
	return result

def e_distDict(bigDict, data, attr):
	distDict = dict()
	for key1, d1 in enumerate(data):
		distDict[d1.n]=dict()
		for key2, d2 in enumerate(data):
			if(key2<=key1):
				distDict[d1.n][d2.n]=0
				continue
			distDict[d1.n][d2.n] = e_distance(bigDict[d1.n], bigDict[d2.n], attr)
	return distDict

def e_similarity(distDict):
	head=-1
	rear=-1
	similar_list = list()
	dissimilar_list = list()
	for key1, d1 in distDict.items():
		for key2, d2 in distDict[key1].items():
			if(d2 > head or head == -1):
				head = d2
			if((d2 < rear or rear == -1) and d2!=0):
				rear = d2
	q = (head-rear)*0.25
	left = rear+q
	right = rear+3*q

	for key1, d1 in distDict.items():
		for key2, d2 in distDict[key1].items():
			if(d2<left and d2!=0):
				similar_list.append(dict(p1=key1, p2=key2))
			if(d2>right):
				dissimilar_list.append(dict(p1=key1, p2=key2))
	result = dict()
	result['similar']=similar_list
	result['dissimilar']=dissimilar_list
	return result
