# encoding=utf8   
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import re
import requests, json
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import pandas as pd

generalNotability = [ "Wikipedia:N", "Wikipedia:NN", "Wikipedia:NNC", "Wikipedia:ARTN", "Wikipedia:CONTN", "Wikipedia:NLISTITEM", "Wikipedia:NOTEWORTHY", "Wikipedia:NRV", "Wikipedia:NRVE", "Wikipedia:NEXIST", "Wikipedia:POSSIBLE", "Wikipedia:NTEMP", "Wikipedia:NOTTEMPORARY", "Wikipedia:15MOF", "Wikipedia:SUSTAINED", "Wikipedia:PAGEDECIDE", "Wikipedia:NOPAGE", "Wikipedia:WHYN", "Wikipedia:SPIP", "Wikipedia:NOTESAL", "Wikipedia:LISTN", "Wikipedia:FAILN", "Wikipedia:NOTE", "Wikipedia:GNG ", "Wikipedia:GNG", "Wikipedia:Notability", "Wikipedia:SIGCOV" ]

eventNotability = [ "Wikipedia:EVENT", "Wikipedia:N(E)", "Wikipedia:Notability (events)", "Wikipedia:NEWSEVENT", "Wikipedia:NEWS", "Wikipedia:NEVENTS", "Wikipedia:EVENTCRIT", "Wikipedia:EVENTCRITERIA", "Wikipedia:LASTING", "Wikipedia:EFFECT", "Wikipedia:GEOSCOPE", "Wikipedia:DEPTH", "Wikipedia:INDEPTH", "Wikipedia:CONTINUEDCOVERAGE", "Wikipedia:PERSISTENCE", "Wikipedia:DIVERSE", "Wikipedia:ROUTINE", "Wikipedia:DOGBITESMAN", "Wikipedia:SENSATIONAL", "Wikipedia:N/CA", "Wikipedia:NCRIME", "Wikipedia:BREAKING", "Wikipedia:ANTICIPATION", "Wikipedia:DELAY", "Wikipedia:RAPID" ]

orgNotability = [ "Wikipedia:ORG", "Wikipedia:COMPANY", "Wikipedia:CORP", "Wikipedia:NCORP", "Wikipedia:GROUP", "Wikipedia:COMPANY", "Wikipedia:ORIGIN", "Wikipedia:ORGSIG", "Wikipedia:INHERITORG", "Wikipedia:ORGCRITE", "Wikipedia:ORGCRIT", "Wikipedia:CORPDEPTH", "Wikipedia:ORGDEPTH", "Wikipedia:AUD", "Wikipedia:ILLCON", "Wikipedia:ORGIND", "Wikipedia:MULTSOURCES", "Wikipedia:PRODUCTREV", "Wikipedia:ADPROMO", "Wikipedia:CLUB", "Wikipedia:NONPROFIT", "Wikipedia:NGO", "Wikipedia:BRANCH", "Wikipedia:SCHOOL", "Wikipedia:NHSCHOOL", "Wikipedia:NCHURCH", "Wikipedia:LISTED", "Wikipedia:CHAIN", "Wikipedia:PRODUCT", "Wikipedia:NPRODUCT", "Wikipedia:FAILORG", "Wikipedia:FAILCORP" ]




def readLocalDB_Revisions ( page ):
		# Open database connection
		db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )

		# prepare a cursor object using cursor  method
		cursor = db.cursor ()

		sql = "select id, info, added, deleted, diff, pageTitle from revisions where pageTitle = %s"
		try:
			cursor.execute ( sql, page )
			results = cursor.fetchall ( )
		except Exception as e:
			print ( "ERROR read- : " + str( e ) )
		finally:
			# disconnect from server
			db.close ( )
		return results

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

def readLocalDB_autoID ( autoID ):
	# Open database connection
	db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )

	# prepare a cursor object using cursor  method
	cursor = db.cursor ()

	sql = "select linkDetails, linkInfo from deletions where autoID = %s"
	try:
		cursor.execute ( sql, autoID )
		results = cursor.fetchone ( )
	except Exception as e:
		print ( "ERROR read- : " + str( e ) )
	finally:
		# disconnect from server
		db.close ( )
	return results

def updateLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )
		sql = "update deletions set linkDetails = %s where autoID = %s"

		cursor = db.cursor ( )
		try:
				cursor.execute ( sql, result )
				db.commit ( )
		except Exception as e:
				print ( "ERROR update- : " + str( e ) )
				db.rollback ( )
		finally:
			db.close ( )

def writeLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )
		sql = "insert into deletions ( pageURL, linkInfo ) values ( %s, %s )" 

		cursor = db.cursor ( )
		try:
			cursor.execute ( sql, result )
			db.commit ( )
		except Exception as e:
			print ( "ERROR write- : " + str( e ) )
			db.rollback ( )
		finally:
			db.close ( )

def dateTimeExtract ( Text ):  # to extract dateTime with Regex
	dateTime = re.search('(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9],.*$', Text) 
	if dateTime:
		return dateTime.group().strip()
	return ""

def dateTimeConvert ( DT ):  # to convert dateTime
	if DT:
		print("DT: " + str(DT))
		DATE = DT.split(" (UTC)")

		DT = str(DATE[0]).strip()
		DT = DT.replace(",","")
		datetime_object = datetime.strptime(DT, '%H:%M %d %B %Y')
		# %Y-%m-%d %H:%M:%S
		return datetime_object.strftime('%Y-%m-%d %H:%M:%S') 
	return DT

def policyCategorizer ( allPolicyRefs ): #to categorize policy references
	
	genRefCount = []
	eventRefCount = []
	orgRefCount = []
	otherRefCount = []

	for policyRef,count in allPolicyRefs.items():
		if policyRef in generalNotability:
			genRefCount.append(count)
		elif policyRef in eventNotability:
			eventRefCount.append(count)
		elif policyRef in orgNotability:
			orgRefCount.append(count)
		else:
			otherRefCount.append(count)

	genRefSum = sum(genRefCount)
	eventRefSum = sum(eventRefCount)
	orgRefSum = sum(orgRefCount)
	otherRefSum = sum(otherRefCount)

	return (genRefSum, eventRefSum, orgRefSum, otherRefSum)


def findRevEditSize ( rev ):
	added = rev[2]
	deleted = rev[3]
	diff = rev[4] 

	# Initialize values as zero 
	addedLength = 0
	deletedLength = 0
	editSize = 0

	# Calculate edit size of the revision
	if added:
		added = json.loads(added)
		addedLength = added['length']

	if deleted:
		deleted = json.loads(deleted)
		deletedLength = deleted['length']

	editSize = abs (addedLength - deletedLength)

	if not editSize:
		if diff:
			diff = json.loads(diff)
			editSize = diff['length']

	return editSize


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
	references = {}

	for dels in delIdentifier:
		if not dels[0]:
			continue
		delDetail = json.loads(dels[0])
		autoID = dels[1]
		if delDetail["summary"] and delDetail["summary"]["policyRef"]:
			policyRefs = delDetail["summary"]["policyRef"]
			for policyRef in policyRefs:
				policyRef = policyRef.replace( "Wikipedia:", "WP:")
				if policyRef in references:
					references[policyRef] += 1
				else:
					references[policyRef] = 1
	print(references)


