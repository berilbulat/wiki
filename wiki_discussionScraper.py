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
'''
+-------------+------------+------+-----+---------+----------------+
| Field       | Type       | Null | Key | Default | Extra          |
+-------------+------------+------+-----+---------+----------------+
| pageURL     | mediumtext | YES  |     | NULL    |                |
| linkInfo    | longtext   | YES  |     | NULL    |                |
| linkDetails | longtext   | YES  |     | NULL    |                |
| autoID      | int(11)    | NO   | PRI | NULL    | auto_increment |
+-------------+------------+------+-----+---------+----------------+

'''

def readLocalDB ( page ):
		# Open database connection
		db = MySQLdb.connect ( "localhost","root","cmn_2019","wiki" )

		# prepare a cursor object using cursor  method
		cursor = db.cursor ()

		sql = "select autoID, linkInfo from deletions where pageURL = %s and linkDetails IS NULL"
		try:
			cursor.execute ( sql, page )
			results = cursor.fetchall ( )
		except Exception as e:
			print ( "ERROR read- : " + str( e ) )
		finally:
			# disconnect from server
			db.close ( )
		return results

def updateLocalDB ( result ):
		db = MySQLdb.connect ( "localhost","root","cmn_2019","wiki" )
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

def linkExtract ( HTML ): # to extract policyReferences, userNames and otherLinks.
	links = HTML.find_all("a")
	policyRef = []
	userList = []
	otherLinks = []

	for link in links:
		if "title" in link.attrs:
			if "Wikipedia:" in link.attrs[ "title" ] and "WikiProject Deletion sorting" not in link.attrs["title"]:
				policyRef.append( link.attrs[ "title" ] ) 
			elif "User:" in link.attrs[ "href" ]:
				userName = str( link.attrs[ "title"].replace("User:", "") ).strip()
				userList.append( userName )
			else:
				otherLinks.append( link.attrs["href"] )

	result = ( policyRef, userList, otherLinks )

	return result


def discussionScrape ( discussionLink ):
	baseURL= "https://en.wikipedia.org"

	page = requests.get(baseURL + discussionLink)
	html_content = page.text
	print(baseURL + discussionLink)
	soup = BeautifulSoup (html_content, features="lxml")

	print("#####################")
	resultParagraphs = soup.select( ".boilerplate > p")
	resultDls  = soup.select( ".boilerplate > dl")
	resultComments = soup.select( ".boilerplate > ul li")

	linkDetails = {} # combination all below dictionaries to write into the database
	finalResult = {}	# finalResult of the discussion that is the first line of each page, first <p> under boilerplate class
	initialComment = {}	# initial comment that starts the deletion discussion, second <p> under boilerplate class
	additionalNotes = {} # when there are additional notes that are neither comments nore votes, but they mention where the discussion was inlcuded e.g. "this discussion is included in the list of blabla related discussions"
	comments = {} # comments/votes that are in the deletion discussion
	summary = {} # summary of the discussion such as total policy referecence counts, user counts, vote counts, comment counts, length of comments, word count of comments
	'''
		<p>The result was <b>keep</b>: per <a class="mw-redirect" href="/wiki/Wikipedia:SNOW" title="Wikipedia:SNOW">SNOW</a>. <small><a class="mw-redirect" href="/wiki/Wikipedia:NACD" title="Wikipedia:NACD">(non-admin closure)</a></small> --- <a href="/wiki/User_talk:Coffeeandcrumbs" title="User talk:Coffeeandcrumbs"><span style="color:blue">C</span></a>&amp;<a href="/wiki/Special:Contributions/Coffeeandcrumbs" title="Special:Contributions/Coffeeandcrumbs"><span style="color:#663366">C</span></a> (<a class="new" href="/w/index.php?title=User:Coffeeandcrumbs&amp;action=edit&amp;redlink=1" title="User:Coffeeandcrumbs (page does not exist)">Coffeeandcrumbs</a>) 03:22, 3 January 2020 (UTC)
		</p>

		<p><a class="mw-redirect" href="/wiki/Wikipedia:NOTNEWS" title="Wikipedia:NOTNEWS">WP:NOTNEWS</a>. Helicopters crash all the time, and so far there's no suggestion that there is anything particular to this crash, such as geopolitical implications. The death of a notable person is adequately covered at <a href="/wiki/Shen_Yi-ming#Death" title="Shen Yi-ming">Shen Yi-ming#Death</a>. <small><span style="border:1px solid black;padding:1px;"><a href="/wiki/User:Sandstein" title="User:Sandstein"><span style="color:white;background:blue;font-family:sans-serif;"><b> Sandstein </b></span></a></span></small> 10:30, 2 January 2020 (UTC)
		</p>
	'''
	if len(resultParagraphs) > 1:
		finalResultHTML = resultParagraphs[0] # For Final Vote - first <p> under boilerplate class
		finalResultText = resultParagraphs[0].getText()

		finalResult['selfText'] = finalResultText

		finalResultLinks = linkExtract( finalResultHTML )
		finalResult['policyRef'] = finalResultLinks[0]
		finalResult['user'] = finalResultLinks[1]
		finalResult['otherLinks'] = finalResultLinks[2]

		finalResult['dateTime'] = dateTimeConvert(dateTimeExtract(finalResultText))

		finalVote = finalResultHTML.find("b").getText()
		finalResult["vote"] = finalVote

		initialCommentHTML = resultParagraphs[1] # For Initial Comment - second <p> under boilerplate class
		initialCommentText = resultParagraphs[1].getText()

		initialCommentLinks = linkExtract( initialCommentHTML )
		initialComment['policyRef'] = initialCommentLinks[0]
		initialComment['user'] = initialCommentLinks[1]
		initialComment['otherLinks'] = initialCommentLinks[2]

		initialComment['dateTime'] = dateTimeConvert(dateTimeExtract(initialCommentText))
		initialComment['selfText'] = initialCommentText

	for res in resultDls:
		if "Please do not modify it.</b>" in str(res): # for skipping the header and footer that repeats in each page 
			continue
		elif '(edit | talk | history | protect | delete | links | watch | logs | views)' in res.getText(): # for skipping the links and discussion title under boiler plate 
			continue
		additionalNotesHTML = res # For additional notes 
		additionalNotesText = res.getText()

		additionalNotes['selfText'] = additionalNotesText

		additionalNotesLinks = linkExtract( additionalNotesHTML )
		additionalNotes['policyRef'] = additionalNotesLinks[0]
		additionalNotes['user'] = additionalNotesLinks[1]
		additionalNotes['otherLinks'] = additionalNotesLinks[2]

		additionalNotes['dateTime'] = dateTimeConvert(dateTimeExtract(additionalNotesText))

	commentsVote = []
	commentsDateTimes = []
	commentsSelfTexts = []
	commentsPolicyRefs = []
	commentsUserLists = []
	commentsOtherLinks = []
	'''
	<li><b>Keep</b>. This crash killed as many as eight people including high-level military officers and has received significant coverage in reliable sources. And it occurred just nine days before the <a href="/wiki/2020_Taiwanese_presidential_election" title="2020 Taiwanese presidential election">2020 Taiwanese presidential election</a> and caused candidates <a href="/wiki/Tsai_Ing-wen" title="Tsai Ing-wen">Tsai Ing-wen</a> and <a href="/wiki/Han_Kuo-yu" title="Han Kuo-yu">Han Kuo-yu</a> to stop their campaign activities for three days and two days respectively. In my view, this article meets <a href="/wiki/Wikipedia:Notability" title="Wikipedia:Notability">Wikipedia:Notability</a> and should be kept. --<a href="/wiki/User:Neo-Jay" title="User:Neo-Jay">Neo-Jay</a> (<a href="/wiki/User_talk:Neo-Jay" title="User talk:Neo-Jay">talk</a>) 11:28, 2 January 2020 (UTC)</li>
	'''
	for res in resultComments: 
		commentHTML = res # For comments posted under the deletion discussion 
		commentText = res.getText()
		
		commentsSelfTexts.append(commentText)
		comments['selfText'] = commentsSelfTexts 

		commentsLinks = linkExtract( commentHTML )

		commentsPolicyRefs.append(commentsLinks[0] and commentsLinks[0][0] or "")
		commentsUserLists.append(commentsLinks[1] and commentsLinks[1][0] or "")
		commentsOtherLinks.append(commentsLinks[2] and commentsLinks[2][0] or "")
		comments['policyRef'] = commentsPolicyRefs
		comments['user'] = commentsUserLists
		comments['otherLinks'] = commentsOtherLinks

		commentsDateTimes.append(dateTimeConvert(dateTimeExtract(commentText)))
		comments['dateTime'] = commentsDateTimes

		if commentHTML.find("b"): 
			commentVote = commentHTML.find("b").getText() and commentHTML.find("b").getText() or ""
			commentsVote.append(commentVote)
			comments["votes"] = commentsVote
		
	summaryPolicyRefs = finalResult.get('policyRef',[]) + initialComment.get('policyRef',[]) + additionalNotes.get('policyRef',[]) + comments.get('policyRef',[])
	summaryPolicyRefs = [i for i in summaryPolicyRefs if i] 

	totalPolicyRefs = len(summaryPolicyRefs)

	summaryPolicyRefs = dict((x,summaryPolicyRefs.count(x)) for x in set(summaryPolicyRefs))

	summary["policyRef"] = summaryPolicyRefs
	summary["totalPolicyRef"] = totalPolicyRefs

	summaryUserLists = finalResult.get('user',[]) + initialComment.get('user',[]) + additionalNotes.get('user',[]) + comments.get('user',[])
	summaryUserLists = [i for i in summaryUserLists if i] 

	totalUserCount = len(summaryUserLists)

	summaryUserLists = dict((x,summaryUserLists.count(x)) for x in set(summaryUserLists))
	summary["user"] = summaryUserLists
	summary["totalUser"] = totalUserCount

	summaryVotes = comments.get('votes',[])
	summaryVotes = dict((x,summaryVotes.count(x)) for x in set(summaryVotes))
	summary["votes"] = summaryVotes

	summaryComments = comments.get('selfText',[])
	totalCommentCount = len(summaryComments)

	summary["totalComments"] = totalCommentCount

	totalCharCount = 0
	totalWordCount = 0
	for comment in summaryComments:
		totalCharCount += len(comment)
		totalWordCount += len(comment.split())

	summary["totalChars"] = totalCharCount
	summary["totalWords"] = totalWordCount
	summary["finalDecision"] = finalResult.get('vote',"") 

	print("///////////////")

	print(json.dumps(summary))

	linkDetails["finalResult"] = finalResult
	linkDetails["initialComment"] = initialComment
	linkDetails["additionalNotes"] = additionalNotes
	linkDetails["comments"] = comments
	linkDetails["summary"] = summary

	return json.dumps(linkDetails)


if __name__ == "__main__":
		ap = argparse.ArgumentParser ( )
		ap.add_argument ( '-p', '--pageURL', type=str )
		args = ap.parse_args ( )

		allDiscussions = readLocalDB( args.pageURL )
		for discussion in allDiscussions:
			try: 
				autoID = discussion[0]
				linkInfo = json.loads(discussion[1])

				if linkInfo["link"]:
					linkDetails = discussionScrape(linkInfo["link"])

				if linkDetails:
					result = ( linkDetails, autoID )
					updateLocalDB(result)
			except Exception as e:
				print ( "ERROR in main- : " + str( e ) )
				continue

