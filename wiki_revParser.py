import MySQLdb
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
import difflib

def createDateTime(rev):
	"""Given a revision entry, return a datetime object."""
	if 'timestamp' in rev:
		return datetime.fromtimestamp(mktime(rev['timestamp'])).strftime("%m/%d/%Y, %H:%M:%S")

def getRevisionInfo(oneRevision):
	"""Given a revision entry, return only a few of its fields."""
	return {'revid' :  oneRevision.get('revid', None),
			'comment': oneRevision.get('comment', None),
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

def getAddedDeletedDiff(oneRevision):
	if 'compare' in oneRevision:
		html = oneRevision['compare']['*']
		tree = BeautifulSoup(html, 'lxml')

		deleted = tree.find_all(attrs={'class': 'diff-deletedline'})
		added = tree.find_all(attrs={'class': 'diff-addedline'})

		# get the text from these elements
		deletedText = "".join([element.text for element in deleted])
		addText = "".join([element.text for element in added])

		deletedDict = {}
		addDict = {}
		diffDict = {}

		deletedDict['text'] = deletedText
		deletedDict['length'] = len(deletedText)

		addDict['text'] = addText
		addDict['length'] = len(addText)

		diff_list = [li for li in difflib.ndiff(deletedText, addText) if li[0] != ' ']
		diffDict['text'] = json.dumps(diff_list)
		diffDict['length'] = len(diff_list)

		results = (json.dumps(addDict), json.dumps(deletedDict), json.dumps(diffDict), oneRevision['revid'])
		return results
	return ''

'''
+-----------+------------+------+-----+---------+-------+
| Field     | Type       | Null | Key | Default | Extra |
+-----------+------------+------+-----+---------+-------+
| id        | bigint(20) | NO   | PRI | NULL    |       |
| info      | text       | YES  |     | NULL    |       |
| pageTitle | text       | YES  |     | NULL    |       |
| added     | mediumtext | YES  |     | NULL    |       |
| deleted   | mediumtext | YES  |     | NULL    |       |
| diff      | text       | YES  |     | NULL    |       |
+-----------+------------+------+-----+---------+-------+
'''

def writeLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","cmn_2019","wiki" )
		sql = "insert into revisions ( id, info, pageTitle ) values ( %s, %s, %s )"

		cursor = db.cursor ( )
		try:
			cursor.execute ( sql, result )
			db.commit ( )
		except Exception as e:
			print ( "ERROR write- : " + str( e ) )
			db.rollback ( )
		db.close ( )

def updateLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","cmn_2019","wiki" )
		sql = "update revisions set added = %s, deleted = %s, diff = %s where id = %s"
		cursor = db.cursor ( )
		try:
				cursor.execute ( sql, result )
				db.commit ( )
		except Exception as e:
				print ( "ERROR update- : " + str( e ) )
				db.rollback ( )
		db.close ( )

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
			allRevisionInfo[i]['revid'] = item['revid']
			detail = allRevisionInfo[i]

			revDct = getRevisionInfo(item) 
			detailDct = getRevisionDetails(detail)
			
			detailDct.update(revDct) 
			combinedRevisions.append(detailDct)

		for combinedRev in combinedRevisions:
			info_string = json.dumps(combinedRev)
			results = ( combinedRev['revid'], info_string, args.pageTitle)
			writeLocalDB(results)

		for revInfo in allRevisionInfo:
			results = getAddedDeletedDiff(revInfo)
			print(revInfo['revid'])
			if results:
				updateLocalDB(results)



