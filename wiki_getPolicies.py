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
import os.path, urlparse
import collections

def generateSectionsOfURL (url):
	path = urlparse.urlparse(url).path
	sections = []; temp = "";

	while path != '/':
		temp = os.path.split(path)
		path = temp[0]
		sections.append(temp[1])
	return sections



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

def discussionScrape ( discussionLink ):
	baseURL= "https://en.wikipedia.org/wiki/"

	response = requests.get(baseURL + discussionLink)

	if "Wikipedia:Articles_for_deletion".lower() in discussionLink.lower():
		return ""

	policy = ""
	print(discussionLink)
	soup = BeautifulSoup(response._content, "lxml")
	canonical = soup.find('link', {'rel': 'canonical'})
	if canonical['href'] == baseURL + discussionLink:
		print("Policy: " + discussionLink)
		policy = discussionLink
	else:
		sections = generateSectionsOfURL( canonical['href'] )
		if sections:
			print("Policy:" + sections[0])
			policy = sections[0]
	if "Wikipedia:Articles_for_deletion".lower() in policy.lower():
		policy = ""

	return policy

if __name__ == '__main__':
	delIdentifier = readLocalDB_Deletions( )
	references = {}

	for dels in delIdentifier:
		if not dels[0]:
			continue
		delDetail = json.loads(dels[0])
		autoID = dels[1]
		print("------------------------")
		if delDetail["summary"] and delDetail["summary"]["policyRef"]:
			policyRefs = delDetail["summary"]["policyRef"]
			for policyRef,value in policyRefs.items():
				policyRef = policyRef.replace(" ", "_")
				mainPolicy = discussionScrape( policyRef )
				if not mainPolicy:
					continue
				if mainPolicy in references:
					references[mainPolicy] += value
				else:
					references[mainPolicy] = value
			print(references)

	references = sorted(references.items(), key=lambda item: item[1], reverse=True)

	sorted_dict = collections.OrderedDict(references)
	print(sorted_dict)
