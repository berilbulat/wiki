import mwclient
try:
	import cPickle as pickle
except:
	import pickle
import warnings
warnings.filterwarnings(action='ignore')
import argparse
import requests, json
from bs4 import BeautifulSoup



if __name__ == "__main__":
		ap = argparse.ArgumentParser ( )
		ap.add_argument ( '-p', '--pageTitle', type=str )
		args = ap.parse_args ( )
		
		print("Reading pickle file for... " + args.pageTitle + ".pck")
		revisions = pickle.load(open(args.pageTitle + ".pck"))
		print ("Total Revision Count: " + str(len(revisions)))

		print("Reading json file for... " + args.pageTitle + ".json")
		allRevisionInfo = json.load(open(args.pageTitle + ".json"))
		print ("Total Revision Count: " + str(len(allRevisionInfo)))


		html = allRevisionInfo[389]['compare']['*']
		tree = BeautifulSoup(html, 'lxml')

		deleted = tree.find_all(attrs={'class': 'diff-deletedline'})
		added = tree.find_all(attrs={'class': 'diff-addedline'})

		# get the text from these elements
		deletedText = "".join([element.text for element in deleted])
		addText = "".join([element.text for element in added])

		# show size of changes
		print "deleted characters:", len(deletedText)
		print "added characters:", len(addText)

		print(deletedText)
		print(addText)	
	
		set(deletedText.split()).difference(set(addText.split()))

		print( set(addText.split()).difference(set(deletedText.split())) )
