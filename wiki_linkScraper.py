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

'''
+-------------+------------+------+-----+---------+-------+
| Field       | Type       | Null | Key | Default | Extra |
+-------------+------------+------+-----+---------+-------+
| pageURL     | mediumtext | YES  |     | NULL    |       |
| linkInfo    | longtext   | YES  |     | NULL    |       |
| linkDetails | longtext   | YES  |     | NULL    |       |
+-------------+------------+------+-----+---------+-------+

'''

def writeLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","cmn_2019","wiki" )
		sql = "insert into deletions ( pageURL, linkInfo ) values ( %s, %s )" 

		cursor = db.cursor ( )
		try:
			cursor.execute ( sql, result )
			db.commit ( )
		except Exception as e:
			print ( "ERROR write- : " + str( e ) )
			db.rollback ( )
		db.close ( )

def dateTimeExtract ( Text ):  # to extract dateTime with Regex
	dateTime = re.search('(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9],.*$', Text) 
	if dateTime:
		return dateTime.group().strip()
	return ""

if __name__ == "__main__":
		ap = argparse.ArgumentParser ( )
		ap.add_argument ( '-p', '--pageURL', type=str )
		args = ap.parse_args ( )

		page = requests.get(args.pageURL)
		html_content = page.text

		soup = BeautifulSoup (html_content, features="lxml")


		result = soup.select( ".mw-parser-output > ul li")

		for res in result:
			linkInfo = {}
			#print("Date: " + str ( res.find("small").text ))
			title = res.find('a').children.next()
			if "redirect to" or "move to" in str(res):
				# print("Result: " + str( res.find('a').next_sibling ))
				result = res.find('a').next_sibling
				# print(result)
			else: 	
				# print("Result: " + str( res.find('small').previous_sibling ))
				result = res.find('small').previous_sibling
			link = str( res.find("a").attrs["href"] )
			linkTitle = res.find("a").attrs["title"]

			date = str(res.find("small").text) # This is to be able to substract dates later for table 3
			dateTime = dateTimeExtract(date)
			# print(dateTime.group())

			if dateTime in date:
				decision = str( date.replace(dateTime, "") ).strip()

			linkInfo["dateTime"] = str(dateTime) # edited time
			linkInfo["dateTime_decision"] = decision # decision that appears next to date and time, always "closed" for every artcile, but kept it anyways
			linkInfo["linkTitle"] = linkTitle # title for the link
			linkInfo["link"] = link # link itself, basically same as above, but kept it
			linkInfo["articleTitle"] = title # title of the article itself 


			resValue = re.split(" - ", result)
			# When result has different lenghts
			if len(resValue) == 4: 
				resNumber = re.sub(r"[\(\)]", "", resValue[1]) 
				linkInfo["resultNumber"] = resNumber # this is the (number) that is next to the result/decision on the deleted articles list, e.g. (6719) - delete, still not sure what it signifies so I kept it and named it resNumber 
				linkInfo["result"] = resValue[2].strip()
			elif len(resValue) == 3:
				resNumber = re.sub(r"[\(\)]", "", resValue[1])
				linkInfo["resultNumber"] = resNumber
				linkInfo["result"] = resValue[2].strip()
			elif len(resValue) == 5:
				# - (3200) - Deleted as G12 - copyright violation. - 
				resNumber = re.sub(r"[\(\)]", "", resValue[1])
				linkInfo["resultNumber"] = resNumber
				linkInfo["result"] = resValue[2].strip()
				linkInfo["resultExplained"] = resValue[3].strip() # When there is additional explanation for the decision i.e. copyright violation.
			else:
				print(" Not sure how to handle this")
				continue
			# break

			print(args.pageURL)
			print(json.dumps(linkInfo))
			results = (args.pageURL, json.dumps(linkInfo))
			writeLocalDB(results)
			print("----------------")



			

		# <li><a href="/wiki/Wikipedia:Articles_for_deletion/Ikes_Fire" title="Wikipedia:Articles for deletion/Ikes Fire">Ikes Fire</a> - (12628) - keep - <small>closed 19:21, 26 December 2019 (UTC)</small></li>

		# when it redirects 

		# <li><a href="/wiki/Wikipedia:Articles_for_deletion/Escape_from_Zyzzlvaria" title="Wikipedia:Articles for deletion/Escape from Zyzzlvaria">Escape from Zyzzlvaria</a> - (6850) - redirect to <a class="mw-redirect" href="/wiki/Mystery_Hunt" title="Mystery Hunt">Mystery Hunt</a> - <small>closed 09:05, 28 March 2009 (UTC)</small></li>




