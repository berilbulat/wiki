import mwclient
try:
	import cPickle as pickle
except:
	import pickle
import warnings
warnings.filterwarnings(action='ignore')
import argparse
import requests, json

def getRevisionInfo(revision):
	"""Given a revision field, request info from the API"""
	urlbase = "https://en.wikipedia.org/w/api.php"
	req = requests.get(url=urlbase,
					params = { 'action': 'compare',
								'format': 'json',
								'prop': 'size|diffsize|user|diff',
								'fromrev': revision['parentid'],
								'torev': revision['revid']})  

	if req.status_code == 200:
		response = json.loads(req.content)
		return response


if __name__ == "__main__":
		ap = argparse.ArgumentParser ( )
		ap.add_argument ( '-p', '--pageTitle', type=str )
		args = ap.parse_args ( )
		

		print("Reading pickle file for... " + args.pageTitle + ".pck")
		revisions = pickle.load(open(args.pageTitle + ".pck"))
		print ("Total Revision Count: " + str(len(revisions)))

		allRevisionInfo = []
		noRevisionInfo = []
		for rev in revisions:
			result = getRevisionInfo(rev)
			if result:
				allRevisionInfo.append(result)
				print( "Result for.. " + str(rev['revid']))  
			else:
				noRevisionInfo.append(rev['revid'])
				print( "No Result for.. " + str(rev['revid']))  
				
		print "we got info for {} revisions.".format(len(allRevisionInfo))

		print "we got NO info for {} revisions.".format(len(noRevisionInfo))

		json.dump(allRevisionInfo, open(args.pageTitle + ".json", 'w'))

		json.dump(noRevisionInfo, open("No-result-" + args.pageTitle + ".json", 'w'))
