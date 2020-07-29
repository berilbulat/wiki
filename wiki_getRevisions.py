# encoding=utf8  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import re
import requests, json


def readLocalDB_Deletions ( ):
	# Open database connection
	db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )

	# prepare a cursor object using cursor  method
	cursor = db.cursor ()

	sql = "select linkDetails, autoID from deletions"
	try:
		cursor.execute ( sql )
		results = cursor.fetchall ( )
	except Exception as e:
		print ( "ERROR read- : " + str( e ) )
	finally:
		# disconnect from server
		db.close ( )
	return results

if __name__ == '__main__':

	results = [];

	notabilityString = {
		"academics" : ["WP:PROF", "WP:NPROF"],
		"astronomical_objects" : ["WP:NASTRO"],
		"books" : ["WP:BK", "WP:NB", "WP:NBOOK"],
		"events": ["WP:N(E)","WP:EVENT", "WP:NEWSEVENT" ,"WP:NNEWS","WP:NEVENTS"],
		"films" : ["WP:NFILM", "WP:NF"],
		"geographic_features" : ["WP:NGEO"],
		"music" : ["WP:NMG","WP:NMUSIC", "WP:NM"],
		"numbers" : ["WP:NUMBER", "WP:NNUM"],
		"organizations_and_companies" : ["WP:ORG", "WP:CORP","WP:NCORP", "WP:GROUP", "WP:COMPANY"],
		"people" : ["WP:BIO", "WP:NBIO"],
		"sports" : ["WP:NSPORT"],
		"web" : ["WP:WEB", "WP:NWEB", "WP:WEBPAGE", "WP:WEBSITE", "WP:WEBNOTE"]
	}

	notabilityObj = json.loads( json.dumps(notabilityString , indent=4) )


	delIdentifier = readLocalDB_Deletions( )
	autoIDs = {}

	for dels in delIdentifier:
		try:
			if not dels[0]:
				continue
			delDetail = json.loads(dels[0])
			autoID = dels[1]
			if delDetail["summary"] and delDetail["summary"]["policyRef"]:
				policyRefs = delDetail["summary"]["policyRef"]
				for policyRef in policyRefs:
					policyRef = policyRef.split( "Wikipedia:")[1]
					for notability, refs in notabilityObj.items():
						 for ref in refs:
						 	if policyRef.lower() == ref.split("WP:")[1].lower():
						 		print("Found: " + ref )
						 		if autoID not in autoIDs:
						 			autoIDs[autoID] = []
						 		if notability not in autoIDs[autoID]:
						 			autoIDs[autoID].append(notability)
						 		if notability not in results:
						 			results.append(notability)



		except Exception as e:
				print ( "ERROR __main__ : " + str( e ) )
				continue

	print(autoIDs)
	print(results)

        maxRev = 0
        auto = 0
        for autoID,refs in autoIDs.items():
            if len(refs) > maxRev:
                maxRev = len(refs)
                auto = str(autoID) + " : " + str(refs)

        print(maxRev)
        print(auto)
            
