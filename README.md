Welcome to the Lightning project!!!



This project consists of a series or wrappers and tools that can make it easier to work with the Watson Natural Language Classifier (NLC). If you haven't used it before, read up on it at http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/nl-classifier.html.


 Here's a layout of the repository:

root/
 python/ (All Python Modules and Projects)
 scripts/ (ANT, Maven or other scripts)
 resources/ (Resource files for training and testing purposes)
    training/
    tests/

For Python Modules

For each script, you can run it without arguments to see example usage.

If you are using this to migrate from WEA to NLC, we reccommend the following workflow:
Step 0: Export the Ground truth XML from WEA. 
Step 1 : Use python/Extract.py to convert ground truth snapshot into CSVs. 
Step 2 : Use python/split.py to split train and test set. You will use the train set to 

Step 3 : Use python/nlc.py to train NLC using the train set

Step 4 : Use python/test.py to test NLC using the test set

Have fun!!! 
