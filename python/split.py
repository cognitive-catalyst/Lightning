#this script takes a csv file in classifier format and breaks it into a train and a test csv file given a percentage
#command : python split.py inputcsvfile percent_train outputtraincsvfile outputtestcsvfile
#example : python split.py nlc_data_train 80 train.csv test.csv


from random import random
import csv
import sys

# Splits inputfile into two files: one for testing and one for training
# Pre-Requisite : Inputfile, a csv generated from extract.py
# Parameters :
# inputfile - a csv that is in the format NLC expects (see extract.py)
# outputtrainfile - the outputfile as CSV in the format, to be used for training 
# outputestfile - the outputfile as CSV in the format, to be used for training 
# percent_train, the percent of questions to reserve for training

#TODO make split.csv optimized to prevent class imbalances
def main(argv):
    if len(argv) != 4:
        print 'split.py inputfile percent_train outputtrainfile outputtestfile'
    else:
            train_classes = set()
            test_classes = set()
            all_classes = set()
            num_instances = 0
	    csvFile = open(argv[0],'rb')

	    trainCsv = open(argv[2],'w')
	    testCsv = open(argv[3],'w')
	    csvTrainWriter = csv.writer(trainCsv, delimiter=',')
	    csvTestWriter = csv.writer(testCsv, delimiter=',')

	    with open(argv[0]) as f:
		total_data = csv.reader(csvFile, delimiter=',')

	    percent_as_decimal = float(argv[1])/100

	    for row in total_data:
                num_instances +=1
		if random() < percent_as_decimal:
                    train_classes.add(row[1])
		    csvTrainWriter.writerow([row[0], row[1]])
		else:
                    test_classes.add(row[1])
		    csvTestWriter.writerow([row[0], row[1]])
                all_classes.add(row[1])
            print "\n#########" + "DATA STATISTICS" + "#########"
            print num_instances, " training instances"
	    print len(all_classes), " classes"
            print len(train_classes), " classes in the training set"
            print len(test_classes), " classes in the training set"
            train_count = 0
            for item in train_classes:
                if not item in test_classes:
			train_count += 1
            print train_count, "classes ONLY in the training set"
            test_count = 0
            for item in test_classes:
                if not item in train_classes:
			test_count += 1
            print test_count, "classes ONLY in the testing set"
            print "\n**If you have lots of classes only in the training or only in the testing set, you are going to get bad results. If you test on something you've never seen before, you have no chance of getting it right. To fix this, make sure each class has at least 2 instances (preferrably 8)**"
            print "#########" + "##############" + "#########\n"	
	    trainCsv.close()
	    testCsv.close()
	    csvFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
