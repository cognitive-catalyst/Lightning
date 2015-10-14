# Copyright IBM

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

#Takes a NLC style csv with an optional 3rd field. This extra
#parameter is used to define a classifier name. The csv is then broken
#up into much smaller CSVs and those are used to train a new NLC
#for any which need to be updated

#Usage: nlcTreebuilder.py -i csvName

#TODO: add more options for whether to deploy, train, etc
#TODO: Integrate other lightening scripts instead of calling nlc independently.

import csv
import sys
import os
import shutil
import filecmp
import getopt
import nlc
import requests

#set credentials
username = ""
password = ""
defaultTreeName = "default"
inputcsv = ""
url = "https://gateway.watsonplatform.net/natural-language-classifier/api"


options, args = getopt.getopt(sys.argv[1:], 'i:u:p:')

for opts in options:
    if '-i' in opts[0]:
        inputcsv = opts[1]
    if '-u' in opts[0]:
        username = opts[1]
    if '-p' in opts[0]:
        password = opts[1]

if  not inputcsv or not username or not password:
    print("usage: nlcTreeBuilder.py -i csvInputFile -u username -p password")
    exit(2)

if __name__ == "__main__":
    if not os.path.exists("constructedFiles/tmp"):
        os.makedirs("constructedFiles/tmp")

    with open(inputcsv) as csvfile:
        fileList = [];
        treeFile = csv.reader(csvfile, delimiter=',', quotechar='"')
        newcsvFiles = [];
        outputFileList = [];

        #Read each row in input csv and break into csvs for each tree
        for row in treeFile:
            if len(row) > 2:
                if row[2] == "":
                    row[2] = defaultTreeName
                if row[2] in fileList:
                    newcsvFiles[fileList.index(row[2])].writerow([row[0], row[1]])
                else:
                    fileList.append(row[2])
                    outputFileList.append(open("constructedFiles/tmp/"+row[2]+".csv", 'w', newline=''))
                    print("Found new tree " + row[2])
                    newcsvFiles.append(csv.writer(outputFileList[-1], delimiter=',', quotechar='"'))
            else:
                print("Only 2 columns in this csv. No need to for multi-tree support. Exiting")
                exit(1)

        #Close all files
        for f in outputFileList:
            f.close()

    #Compare newly created to csvs to any preexisting ones.
    #If there are changes overwrite old csv and post to train new nlc
    nlcInstance = nlc.NaturalLanguageClassifierInstance(username, password, url)
    for file in os.listdir("constructedFiles/tmp/"):
        #If file doesn't exist copy and post
        if not os.path.exists("constructedFiles/"+file):
            shutil.copy("constructedFiles/tmp/"+file, "constructedFiles/")
            print("Training classifier for " + file)
            try:
                nlcInstance.train_classifier(file, training_file="constructedFiles/tmp/"+file)
            except requests.HTTPError as e:
                    print(e)
        else:
            if filecmp.cmp("constructedFiles/tmp/"+file, "constructedFiles/"+file, shallow=False):
                print(file + " hasn't changed. Skipping classifier training")
            else:
                print("Training classifier for " + file)
                shutil.copy("constructedFiles/tmp/"+file, "constructedFiles/")
                try:
                    nlcInstance.train_classifier(file, training_file="constructedFiles/tmp/"+file)
                except requests.HTTPError as e:
                    print(e)

