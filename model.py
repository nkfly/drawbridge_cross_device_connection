import csv
import random
import numpy
from math import log10, sqrt
from sklearn.ensemble import RandomForestClassifier
from scipy.spatial.distance import cosine
import operator
import copy

def process_train_device(devTrainBasic):
	handle2vec = {}
	with open(devTrainBasic, 'r') as csvfile:
		spamreader = csv.DictReader(csvfile)
		for row in spamreader:
			handle2vec[row['drawbridge_handle']] = True

	print len(handle2vec)


# id_328334,1,{(ip17920421,1096,179,761,30,7,25),(ip11782479,219,48,156,18,4,14)}

def document_model(idAllIp):
	charsToRemove = ['{', '}', '(', ')']

	cookie2vec = {}
	device2vec = {}
	ip2idf = {}
	with open(idAllIp, 'r') as csvfile:
		csvfile.readline()
		for line in csvfile:
			l = line.translate(None, ''.join(charsToRemove))
			parts = l.strip().split(',')

			for i in range(len(parts)):
				part = parts[i]
				if i == 0:
					identifier = part
				elif i == 1:
					if int(part) == 1:
						isCookie = True
					else:
						isCookie = False
				elif part.startswith('ip'):
					if part not in ip2idf:
						ip2idf[part] = 1
					else:
						ip2idf[part] += 1
					if isCookie:
						if identifier not in cookie2vec:
							cookie2vec[identifier] = {}
						cookie2vec[identifier][part] = int(parts[i+1])

					else:
						if identifier not in device2vec:
							device2vec[identifier] = {}
						device2vec[identifier][part] = int(parts[i+1])


	documentNumber = len(cookie2vec) + len(device2vec)
	for ip in ip2idf:
		ip2idf[ip] = log10(documentNumber/ip2idf[ip])
	# print len(cookie2vec)
	# print len(device2vec)
	for identifier in cookie2vec:
		for ip in cookie2vec[identifier]:
			cookie2vec[identifier][ip] = log10(1 + cookie2vec[identifier][ip]) * ip2idf[ip]

	for identifier in device2vec:
		for ip in device2vec[identifier]:
			device2vec[identifier][ip] = log10(1 + device2vec[identifier][ip]) * ip2idf[ip]

	

	return cookie2vec, device2vec, ip2idf



def cosine_similarity(cookieVec, deviceVec):
	cookieLength = 0
	deviceLength = 0
	dotProduct = 0

	for ip in deviceVec:
		deviceLength += deviceVec[ip] * deviceVec[ip]
		if ip in cookieVec:
			dotProduct += cookieVec[ip] * deviceVec[ip]
	if dotProduct == 0:
		return 0

	for ip in cookieVec:
		cookieLength += cookieVec[ip] * cookieVec[ip]

	return dotProduct / sqrt(cookieLength) * sqrt(deviceLength)











if __name__ == '__main__':
	# process_train_device('./data/dev_train_basic.csv')
	cookie2vec, device2vec, ip2idf = document_model('./data/id_all_ip.csv')
	with open('answer.csv', 'w') as w:
		w.write('device_id,cookie_id\n')
		ii = 0
		with open('data/dev_test_basic.csv', 'r') as csvfile:
			spamreader = csv.DictReader(csvfile)
			for row in spamreader:
				deviceId = row['device_id']
				w.write(deviceId+',')
				if deviceId not in device2vec:
					w.write('\n')
					continue

				cookie2similarity = {}
				for cookie in cookie2vec:
					cosineValue = cosine_similarity(cookie2vec[cookie], device2vec[deviceId])
					if cosineValue == 0:
						continue
					cookie2similarity[cookie] = cosineValue

				coo = sorted(cookie2similarity.items(), key=operator.itemgetter(1), reverse=True)

				index = 0
				while index < len(coo) and index < 10:
					w.write(coo[index][0]+" ")
					index += 1

				w.write('\n')
				print ii
				ii += 1










