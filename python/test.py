# this script takes a json file in classifier format and uses it to test how well a classifier performs against it
# it produces an output indicating accuracy and recall@5
#command : python test.py testfile classifier id bm_username bm_password
#example : python test.py test.json FD87F2-nlc-82 dge726egfg83728 gh26w7gd

import urllib2
import csv
import base64
import json
import io

import argparse


def test(inputfile, classifierid, username, password, dumpresultfile):
	response_with_truth = []
	f = open(inputfile, 'r+')
	test_data = csv.reader(f, delimiter=',')
	total = 0
	correct = 0
	top_5 = 0

	classifier_url = "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/" + classifierid + "/classify"

	base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
	headers = {'Content-type': 'application/json', 'Accept': 'application/json',
	       'Authorization': 'Basic %s' % base64string}
	print classifier_url

	for entry in test_data:
		data = json.dumps({'text': entry[0]})
		request = urllib2.Request(classifier_url, data=data, headers=headers)
		response = urllib2.urlopen(request)
		total += 1
		json_response = json.loads(response.read())

		json_response["actual_classes"] = entry[1]

		topClassMatch = False
		top5Match = False

		if json_response['top_class'].encode('utf-8') == entry[1]:
		    correct = correct + 1
		    topClassMatch = True
		for top_classes in json_response['classes'][0:5]:
		    if top_classes['class_name'] in entry[1]:
			top_5 = top_5 + 1
			top5Match = True
			break

		json_response['top_class_match'] = topClassMatch
		json_response['top5_classes_match'] = top5Match

		response_with_truth.append(json_response)

	#print 'currently got ' + str(correct) + ' correct, ' + str(top_5) + ' in top5, ',
	#print 'out of ' + str(total) + '. -- ' + str(correct * 100 / total) + '%'

	print "******final results*********"
	print "correct: " + str(correct) + " (percentage: " + str(correct * 100 / total) + "%)"
	print "num of times in top 5: " + str(top_5) + " (percentage: " + str(top_5 * 100 / total) + "%)"
	print "total: " + str(total)

	if dumpresultfile != None:
            print dumpresultfile
	    with io.open(dumpresultfile, 'w', encoding='utf-8') as f:
		f.write(unicode(
		    json.dumps(response_with_truth, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))))
	    with io.open(dumpresultfile + '.csv', 'w', encoding='utf-8') as f:
		f.write("\"%s\",%s,%s,%s\n" % (u'TEXT', u'TOP_CLASS_MATCH', u'TOP5_CLASSES_MATCH', u'TOP_CLASS_NAME'))
		for entry in response_with_truth:
		    f.write("\"%s\",%s,%s,%s\n" % (
		        entry['text'], entry['top_class_match'], entry['top5_classes_match'], entry['top_class']))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("testfile", help="A file containing the test set in classifier json format")
	parser.add_argument("classifier_id", help="The id of the classifier that is to be tested")
	parser.add_argument("bm_username", help="The bluemix username")
	parser.add_argument("bm_password", help="The bluemix password")
	parser.add_argument("resultsfile", help="produces a json dump of the test results to the file specified, this 'dump' is used by other utilities")
	args = parser.parse_args()
	test(args.testfile, args.classifier_id, args.bm_username, args.bm_password, args.resultsfile)

