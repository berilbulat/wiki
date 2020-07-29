# "Wikipedia:Notability", "Wikipedia:Notability_(organizations_and_companies)", "Wikipedia:What_Wikipedia_is_not", "Wikipedia:Deletion_process", "Wikipedia:Notability_(events)", "Wikipedia:Reliable_sources", "Wikipedia:Signatures", "Wikipedia:Non-admin_closure"

import subprocess
  
pages = ["Wikipedia:Notability", "Wikipedia:Notability_(organizations_and_companies)", "Wikipedia:What_Wikipedia_is_not", "Wikipedia:Deletion_process", "Wikipedia:Notability_(events)", "Wikipedia:Reliable_sources", "Wikipedia:Signatures", "Wikipedia:Non-admin_closure"]

for page in pages:
        call1 = "python wiki_revLister.py -p " + '"' + page + '"'
        print(call1)
        call2 = "python wiki_revRequester.py -p " + '"' + page + '"'
        print(call2)
        call3 = "python wiki_revParser.py -p " + '"' + page + '"'
        print(call3)
        subprocess.call(call1, shell=True)
        subprocess.call(call2, shell=True)
        subprocess.call(call3, shell=True)
