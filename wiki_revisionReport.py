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

if __name__ == "__main__":

	revIdentifiers = readLocalDB_Revisions( )
	
	results = {}
	for rev in revIdentifiers:
		revID = rev[0]

		revDiff = rev[4]
		results[revID] = revDiff

        print(results)
	with open('revision_data.json', 'w') as fp:
		json.dump(results, fp)
