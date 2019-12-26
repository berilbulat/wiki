# wiki

Wiki scraper for revisions made on Wikipedia articles

---

**wiki_revLister.py**: Lists all the revisions for a title given as argument 

  e.g.  python wiki_revLister.py -p "Wikipedia:Notability_(events)"

**wiki_revRequester.py**: Requests the details of a given revision from Wiki API and stores attempt responses in JSON format

e.g.  python wiki_revRequester.py -p "Wikipedia:Notability_(events)"

**wiki_revParser.py**: Parses the details of succesful attempts, such as revision ID, page title, date&time, user ID, comment, diff size, actual edit size, added and deleted text and their lenghts, and diff characters (- and/or +) and its length

e.g.  python wiki_revParser.py -p "Wikipedia:Notability_(events)"

**wiki_test.py**: Extracts deleted texts and added texts from a given revision

**schema.sql**: 

| Field     | Type       | Null | Key | Default | Extra |
| --------- |:----------:| ----:|---- |:-------:| -----:|
| id        | bigint(20) | NO   | PRI | NULL    |       |
| info      | text       | YES  |     | NULL    |       |
| pageTitle | text       | YES  |     | NULL    |       |
| added     | mediumtext | YES  |     | NULL    |       |
| deleted   | mediumtext | YES  |     | NULL    |       |
| diff      | mediumtext | YES  |     | NULL    |       |

---
result ex. for one revision:

**id**: 885201796  <br />
**info**: {"comment": "/* Primary criteria */ Minor change to the table: The newspaper's name is \"The New York Times\" (with the  \"The\")", "time": "02/26/2019, 16:25:53", "length": 40447, "revid": 885201796, "diffsize": 1834, "user": "Rsfinlayson", "editsize": 4} <br />
**pageTitle**: Wikipedia:Notability_(organizations_and_companies)  <br />
**added**: {"text": "| ''The New York Times'' || {{nay}} || {{aye}} || {{aye}} || {{aye}} || {{nay}} || A single-sentence mention in an article about another company", "length": 144}  <br />
**deleted**: {"text": "| ''New York Times'' || {{nay}} || {{aye}} || {{aye}} || {{aye}} || {{nay}} || A single-sentence mention in an article about another company", "length": 140}  <br />
**diff**: {"text": "[\"+ T\", \"+ h\", \"+ e\", \"+  \"]", "length": 4}  <br />

Happy scraping! 
