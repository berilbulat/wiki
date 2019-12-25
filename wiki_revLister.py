import mwclient
try:
	import cPickle as pickle
except:
	import pickle
import warnings
warnings.filterwarnings(action='ignore')
import argparse

if __name__ == "__main__":
		ap = argparse.ArgumentParser ( )
		ap.add_argument ( '-p', '--pageTitle', type=str )
		args = ap.parse_args ( )

		print ( "getting page... " + args.pageTitle ) 
		site = mwclient.Site(('https', 'en.wikipedia.org'))
		page = site.pages[args.pageTitle]

		revisions = []
		for i, revision in enumerate(page.revisions()):
			revisions.append(revision)
			print("Number: " + str(i))
			print(revision)

		print ( "saving to file... " + args.pageTitle + ".pck" )
		with open(args.pageTitle + ".pck", 'w') as pckFile:
			pickle.dump(revisions, pckFile)
