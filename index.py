#!/usr/bin/python3

import csv
import sys
import pysolr

solr = pysolr.Solr("http://127.0.0.1:8983/solr/core1")

data=csv.DictReader(sys.stdin,delimiter=";")
to_index=[]
for lidx,line in enumerate(data):
    to_index.append({"id":line["teksti_numero"],"text_text_fi":line["teksti"],"specialty_text_fi":line["nakyma_selite"],"HETU":line["henkilotunnus"],"aika":line["hoitotapahtuma_alkuhetki"]})
    if len(to_index)>10000:
        solr.add(to_index)
        print(lidx)
        to_index=[]
solr.commit()
