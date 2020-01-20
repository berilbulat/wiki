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

# Notability reference categories and related policy references for each category

generalNotability = [ "Wikipedia:N", "Wikipedia:NN", "Wikipedia:NNC", "Wikipedia:ARTN", "Wikipedia:CONTN", "Wikipedia:NLISTITEM", "Wikipedia:NOTEWORTHY", "Wikipedia:NRV", "Wikipedia:NRVE", "Wikipedia:NEXIST", "Wikipedia:POSSIBLE", "Wikipedia:NTEMP", "Wikipedia:NOTTEMPORARY", "Wikipedia:15MOF", "Wikipedia:SUSTAINED", "Wikipedia:PAGEDECIDE", "Wikipedia:NOPAGE", "Wikipedia:WHYN", "Wikipedia:SPIP", "Wikipedia:NOTESAL", "Wikipedia:LISTN", "Wikipedia:FAILN", "Wikipedia:NOTE", "Wikipedia:GNG ", "Wikipedia:GNG", "Wikipedia:Notability", "Wikipedia:SIGCOV" ]

eventNotability = [ "Wikipedia:EVENT", "Wikipedia:N(E)", "Wikipedia:Notability (events)", "Wikipedia:NEWSEVENT", "Wikipedia:NEWS", "Wikipedia:NEVENTS", "Wikipedia:EVENTCRIT", "Wikipedia:EVENTCRITERIA", "Wikipedia:LASTING", "Wikipedia:EFFECT", "Wikipedia:GEOSCOPE", "Wikipedia:DEPTH", "Wikipedia:INDEPTH", "Wikipedia:CONTINUEDCOVERAGE", "Wikipedia:PERSISTENCE", "Wikipedia:DIVERSE", "Wikipedia:ROUTINE", "Wikipedia:DOGBITESMAN", "Wikipedia:SENSATIONAL", "Wikipedia:N/CA", "Wikipedia:NCRIME", "Wikipedia:BREAKING", "Wikipedia:ANTICIPATION", "Wikipedia:DELAY", "Wikipedia:RAPID" ]

orgNotability = [ "Wikipedia:ORG", "Wikipedia:COMPANY", "Wikipedia:CORP", "Wikipedia:NCORP", "Wikipedia:GROUP", "Wikipedia:COMPANY", "Wikipedia:ORIGIN", "Wikipedia:ORGSIG", "Wikipedia:INHERITORG", "Wikipedia:ORGCRITE", "Wikipedia:ORGCRIT", "Wikipedia:CORPDEPTH", "Wikipedia:ORGDEPTH", "Wikipedia:AUD", "Wikipedia:ILLCON", "Wikipedia:ORGIND", "Wikipedia:MULTSOURCES", "Wikipedia:PRODUCTREV", "Wikipedia:ADPROMO", "Wikipedia:CLUB", "Wikipedia:NONPROFIT", "Wikipedia:NGO", "Wikipedia:BRANCH", "Wikipedia:SCHOOL", "Wikipedia:NHSCHOOL", "Wikipedia:NCHURCH", "Wikipedia:LISTED", "Wikipedia:CHAIN", "Wikipedia:PRODUCT", "Wikipedia:NPRODUCT", "Wikipedia:FAILORG", "Wikipedia:FAILCORP" ]



def readLocalDB_Revisions ( ):
		# Open database connection
		db = MySQLdb.connect ( "localhost","root","adalovelace","wiki" )

		# prepare a cursor object using cursor  method
		cursor = db.cursor ()

		sql = "select id, info, added, deleted, diff from revisions"
		try:
			cursor.execute ( sql )
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

		sql = "select autoID, linkDetails, linkInfo from deletions"
		try:
			cursor.execute ( sql )
			results = cursor.fetchall ( )
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

if __name__ == "__main__":

	revIdentifier = readLocalDB_Revisions( )
	delIdentifier = readLocalDB_Deletions( )
	results = {}
	results['articleTitle'] = []
	results['articleLink'] = []

	results['discussionResult'] = []
	results['discussionResultDate'] = []

	results['totalUser'] = []
	results['totalPosts'] = []
	results['totalWords'] = []
	results['totalChars'] = []

	results['keepVote'] = []
	results['deleteVote'] = []
	results['otherVotesCount'] = []

	results['generalNotabilityCount'] = []
	results['eventNotabilityCount'] = []
	results['orgNotabilityCount'] = []
	results['otherNotabilityCount'] = []

	results['revClosestDate'] = []
	results['revClosestID'] = []
	results['revEditSize'] = []

	for dels in delIdentifier:
		try:
			autoID = dels[0]
			if not dels[1]:
				continue
			if not dels[2]:
				continue
			delDetail = json.loads(dels[1])
			delInfo = json.loads(dels[2])
			delStartTime = 0
			if delDetail["initialComment"]:
				delStartTime = delDetail["initialComment"]["dateTime"]
			if not delStartTime and 'dateTime' in delDetail['comments']:
				dateTimeList = [x for x in delDetail['comments']['dateTime'] if x]
				dateTimeList= dateTimeList.sort()
				if dateTimeList:
					delStartTime = dateTimeList[0]
			if not delStartTime:
				continue

			# Get values from deletions info
			articleTitle =  delInfo['articleTitle']
			articleLink = delInfo['link']
			discussionResult = delInfo['result']
			discussionResultDate = delInfo['dateTime']

			# Initialize them as zero
			keepVote = 0
			deleteVote = 0
			otherVotesCount = 0

			generalRef = 0
			eventRef = 0
			orgRef = 0
			otherRefCount = 0


			# Get values from deletions details
			if delDetail['summary']:
				totalPosts = delDetail['summary']['totalComments'] and delDetail['summary']['totalComments'] or 0
				totalUsers = delDetail['summary']['totalUser'] and delDetail['summary']['totalUser'] or 0
				totalWords = delDetail['summary']['totalWords'] and delDetail['summary']['totalWords'] or 0
				totalChars = delDetail['summary']['totalChars'] and delDetail['summary']['totalChars'] or 0

				# Get Votes
				if delDetail['summary']['votes']:
					allVotes = delDetail['summary']['votes']
					allVotesCount = sum(allVotes.values())
					print(allVotes)
					if 'Keep' in allVotes:
						keepVote = allVotes['Keep']

					if 'Delete' in allVotes:
						deleteVote = allVotes['Delete']

					otherVotesCount = allVotesCount - keepVote - deleteVote

				# Get policy references
					if delDetail['summary']['policyRef']:
						allPolicyRefs = delDetail['summary']['policyRef']
						policyResult = policyCategorizer(allPolicyRefs)

			delTime_obj = datetime.strptime(delStartTime, '%Y-%m-%d %H:%M:%S')
			print("deletionTime: " + str(delTime_obj))
			CLOSEST_date = -100 # I set it to -100 to make sure the value will not be one of the results, so I can update it in the first round of iteration 
			CLOSEST_revID = -100
			CLOSEST_diff = -100
			CLOSEST_revIndex = -100
			for revIndex, rev in enumerate(revIdentifier):  # Go through the revisions, find the closes date, and keep index number to calculate the edit size  
				revID = rev[0] # Revision ID 
				if not rev[1]:
					continue
				info = json.loads(rev[1])

				# Find the closest preceding policy

				if not info["time"]:
					continue
				revTime = info["time"]
				revTime_obj = datetime.strptime(revTime, '%m/%d/%Y, %H:%M:%S')
				delta = delTime_obj - revTime_obj
				secondDiff= delta.total_seconds() # difference in seconds between policy edit date and the start of deletion discussion 
				if secondDiff < 0:
					continue
				if CLOSEST_date == -100:
					CLOSEST_date = revTime_obj
					CLOSEST_revID = revID
					CLOSEST_diff = secondDiff
					CLOSEST_revIndex = revIndex
					continue
				if secondDiff < CLOSEST_diff:
					CLOSEST_date = revTime_obj
					CLOSEST_revID = revID
					CLOSEST_diff = secondDiff
					CLOSEST_revIndex = revIndex

			print("autoID: " + str(autoID))
			print("revClosestDate: " + str(CLOSEST_date))
			print("revClosest_ID: " + str(CLOSEST_revID))

			editSize = findRevEditSize(revIdentifier[CLOSEST_revIndex])
			print("editSize: " + str(editSize))
			print("articleTitle: " + str(articleTitle))
			print("articleLink: " + str(articleLink))
			print("discussionResult: " + str(discussionResult))
			print("discussionResultDate: " + str(discussionResultDate))
			print("keepVote: " + str(keepVote))
			print("deleteVote: " + str(deleteVote))
			print("otherVotesCount: " + str(otherVotesCount))
			print("policyResult" + str(policyResult))

			results['articleTitle'].append(articleTitle)
			results['articleLink'].append(articleLink)
			results['discussionResult'].append(discussionResult)
			results['discussionResultDate'].append(discussionResultDate)
			results['totalUser'].append(totalUsers)
			results['totalPosts'].append(totalPosts)
			results['totalWords'].append(totalWords)
			results['totalChars'].append(totalChars)
			results['keepVote'].append(keepVote)
			results['deleteVote'].append(deleteVote)
			results['otherVotesCount'].append(otherVotesCount)
			results['generalNotabilityCount'].append( policyResult[0] )
			results['eventNotabilityCount'].append( policyResult[1] )
			results['orgNotabilityCount'].append( policyResult[2] )
			results['otherNotabilityCount'].append( policyResult[3] )
			results['revClosestDate'].append(str(CLOSEST_date))
			results['revClosestID'].append(CLOSEST_revID)
			results['revEditSize'].append(editSize)

			print("-------------------------")
		except Exception as e:
				print ( "ERROR __main__ : " + str( e ) )
				continue


		df = pd.DataFrame(results)
		print(df)

		df.to_csv("wiki_data.csv", encoding='utf-8', index=False)

