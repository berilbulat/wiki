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
from datetime import datetime
from time import mktime

def createDateTime(rev):
	"""Given a revision entry, return a datetime object."""
	if 'timestamp' in rev:
		return datetime.fromtimestamp(mktime(rev['timestamp']))

def getRevisionInfo(oneRevision):
	"""Given a revision entry, return only a few of its fields."""
	return {'comment': oneRevision.get('comment', None),
			'user': oneRevision.get('user', None),
			'time': createDateTime(oneRevision)
		   }

def getRevisionDetails(oneRevision):
	"""Given a revision with info, extract some details and return a dict."""
	data = oneRevision.get('compare')
	result = {'user': None, 'length': None, 'editsize': None, 'diffsize': None}
	if data:
		result['user'] = data['touser'] # this is the user who made the edit
		result['length'] = data['tosize'] # final size of page
		result['editsize'] = data['tosize'] - data['fromsize'] # edit as difference
		result['diffsize'] = data['diffsize']
		
	return result

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

		combinedRevisions = []
		for i, item in enumerate(revisions):
			detail = allRevisionInfo[i]
			
			revDct = getRevisionInfo(item) 
			detailDct = getRevisionDetails(detail)
			
			# update to add fields from one dict to the other
			# notice that we update detailDct, which doesn't have meaningful data in some occasions
			detailDct.update(revDct) 
			combinedRevisions.append(detailDct)

		print(combinedRevisions)
