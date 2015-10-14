__author__ = 'vdowling'

# Standard imports
import json
import sys
import argparse

# 3rd party imports
import requests

# Local imports


class NaturalLanguageClassifierInstance(object):
    """
        Class that wraps the functionality associated with a single NLC instance. You can use this instead of command line POSTs to interact with the NLC
	There are three things that this make it very easy to do
		-Train a classifier
		-View information about what classifiers you have (and their statuses)
    """

    def __init__(self, username, password, url):
        if type(username) is not str or username == "":
            raise ValueError("Username provided is none or is not of proper type")
        elif type(password) is not str or password == "":
            raise ValueError("Password provided is none or is not of proper type")
        elif type(url) is not str or url == "":
            raise ValueError("Url provided is none or is not of proper type")
        else:
            self.username_ = username
            self.password_ = password
            self.url_ = url
            self.classifiers_ = list()
            resp = requests.get("%s/v1/classifiers" % self.url_, headers={"Content-Type": "application/json"}, auth=(self.username_, self.password_))
            if resp.ok:
                for classifier in resp.json().get('classifiers') if 'classifiers' in resp.json().keys() else []:
                    classifier_url = classifier.get('url')
                    classifier_obj = NaturalLanguageClassifier(self.username_, self.password_,
                                                               classifier_url=classifier_url)
                    self.classifiers_.append(classifier_obj)

    def train_classifier(self, classifier_name="CLASSIFIER", training_data=[], language='en', training_file=None):

        files = {'training_data': ('train-set.csv', open(training_file, 'rb'),'text/csv'), \
                 'training_metadata': (json.dumps({'language': 'en', 'name': classifier_name}))}
        resp = requests.post("%s/v1/classifiers" % self.url_,files=files, auth=(self.get_username(), self.get_password()))
        if resp.ok:
           classifier_url = resp.json().get('url')
           classifier_obj = NaturalLanguageClassifier(self.get_username(), self.get_password(), classifier_url=classifier_url)
           self.classifiers_.append(classifier_obj)
           print "Classifier created with ID " + classifier_obj.get_id()
           return classifier_obj
        else:
            raise resp.raise_for_status()


    def get_classifier_by_id(self, classifier_id=None):
        for cls in self.get_classifiers():
            if cls.get_id() == classifier_id:
                return cls
        return None


    def get_classifiers(self):
        return self.classifiers_


    def get_url(self):
        return self.url_


    def get_username(self):
        return self.username_


    def get_password(self):
        return self.password_


class NaturalLanguageClassifier(object):
    """
        Class that wraps the functionality for a single Natural Language Classifier
        This class assumes that the classifier has already been trained
    """

    def __init__(self, username, password, classifier_id=None, classifier_url=None):
        if type(username) is not str or username == "":
            raise ValueError("Username provided is none or is not of proper type")
        elif type(password) is not str or password == "":
            raise ValueError("Password provided is none or is not of proper type")
        elif classifier_id is None and classifier_url is None:
            raise ValueError("Both the classifier id and the url is None. At least one of these must be provided")
        elif classifier_url is not None:
            resp = requests.get(classifier_url, headers={"Content-Type": "application/json"}, auth=(username, password))
            if resp.ok:
                json_obj = resp.json()
                self.username_ = username
                self.password_ = password
                self.classifier_url_ = classifier_url
                self.classifier_id_ = json_obj.get('classifier_id')
                self.classifier_name_ = json_obj.get('name')
                self.created_ = json_obj.get('created')
            else:
                raise resp.raise_for_status()
        else:
            self.username_ = username
            self.password_ = password
            gateway_url = 'https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'
            resp = requests.get(gateway_url, headers={"Content-Type": "application/json"}, auth=(username, password))
            if resp.ok:
                classifier = [cls for cls in resp.json().get('classifiers') if
                              cls.get('classifier_id') == classifier_id]
                if len(classifier) == 0:
                    raise ValueError("No classifiers found with the id %r" % classifier_id)
                elif len(classifier) == 1:
                    cls = classifier[0]
                    self.classifier_url_ = cls.get('url')
                    self.classifier_name_ = cls.get('name')
                    self.created_ = cls.get('created')
                    self.classifier_id_ = classifier_id
            else:
                raise resp.raise_for_status()

    def get_id(self):
        return self.classifier_id_

    def get_name(self):
        return self.classifier_name_

    def get_created_date(self):
        return self.created_

    def get_url(self):
        return self.classifier_url_

    def get_status(self):
        resp = requests.get(self.get_url(), headers={"Content-Type": "application/json"},
                            auth=(self.username_, self.password_))
        if resp.ok:
            return resp.json().get('status')
        else:
            raise ValueError("Unable to get classifier status")

    def get_status_description(self):
        resp = requests.get(self.get_url(), headers={"Content-Type": "application/json"},
                            auth=(self.username_, self.password_))
        if resp.ok:
            return resp.json().get('status_description')
        else:
            raise ValueError("Unable to get classifier status")

    def classify(self, text):
        if type(text) is not str or text == "":
            raise ValueError("Provided text is not of proper type or is empty")
        else:
            json_data = {"text": text}
            resp = requests.post(self.get_url(), data=json.dumps(json_data),
                                 headers={"Content-Type": "application/json"}, auth=(self.username_, self.password_))
            if resp.ok:
                return resp.json()
            else:
                raise resp.raise_for_status()


if __name__ == "__main__":
    sample_url = 'https://gateway.watsonplatform.net/natural-language-classifier/api'
    user = ''
    pw = ''

    # Pass this as arguments (Example : Python nlc.py <usernamer> <password>)
    parser = argparse.ArgumentParser()
    parser.add_argument("user", help="User Name")
    parser.add_argument("pw", help="Password")
    parser.add_argument("csvfile", help="CSV file that will be used to generate the classifier (probably the training file generated from split.py)")
    parser.add_argument("classifiername", help="Name of the classifier")
    args = parser.parse_args()

    # 1. Get classifiers information for a given user
    nlc_instance = NaturalLanguageClassifierInstance(args.user, args.pw, sample_url)
    print "Listing all classifiers : Total No. : %d" % len(nlc_instance.get_classifiers())
    for nlInstance in nlc_instance.get_classifiers():
        print nlInstance.get_id() + ' ' + nlInstance.get_name() + ' ' + nlInstance.get_created_date() + ' ' + nlInstance.get_status()

    # 2. Train a classifier
    #moidfy the args to accept a csv file
    #nlc_instance.train_classifier(args.classifiername,training_file=args.csvfile)


    # 3. Get information on a specific classifier
    #classifierId = '{CLASSIFER_ID_FROM_STEP_1}'
    #print(' ')
   #print "Displaying classifier information for " + classifierId
   # nl_classifier = nlc_instance.get_classifier_by_id(classifierId)
    #print "Name : " + nl_classifier.get_name() + " Created on " + nl_classifier.get_created_date() + "Status: " + nlInstance.get_status()

    sys.exit(0)
