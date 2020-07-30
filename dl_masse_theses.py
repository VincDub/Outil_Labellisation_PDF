import pandas as pd
import requests
import os

df = pd.read_csv('theses.csv',header=0)
liens = list(df['uri_s'].values)

liens_dl = []

for i,l in enumerate(liens):

    l = l + "/document"
    rq = requests.get(l,allow_redirects=True)
    path = os.path.join('PDF',("these_"+str(i)+".pdf"))
    open(path,"wb").write(rq.content)



