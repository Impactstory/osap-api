import os
import re
import requests
import requests_cache

from person import Person
from pmid import Pmid
from util import safe_commit
from app import db
from util import normalize

# expire_after is in seconds
requests_cache.install_cache('my_requests_cache', expire_after=60*60*24*30, ignored_parameters=["ts"])

# just last 5 years for now
# from https://intramural.nih.gov/search/allreports.taf?_function=search

have_already_downloaded_everything=True  # hack for now to save time when debugging
if not have_already_downloaded_everything:
    report_year_files = "nimh2013.htm nimh2014.htm nimh2015.htm nimh2016.htm nimh2017 nimh2018.htm".split()
    ipids = []
    for report_year_file in report_year_files:
        with open(os.path.join("data", report_year_file), 'r') as f:
            file_contents = f.read()
        new_ipids = re.findall("ipid=(\d+)", file_contents)
        print len(list(set(new_ipids)))
        ipids += new_ipids
    ipids = list(set(ipids))
    print len(ipids)

i = 0
for ipid in ipids:
    i += 1
    pmids_for_this_ipid = []
    # print ipid
    url = "https://intramural.nih.gov/search/searchview.taf?ipid={}".format(ipid)

    # commenting out for now because we have them all
    print url
    r = requests.get(url)
    with open(os.path.join("data/project_reports", "{}.txt".format(ipid)), 'w') as f:
        f.write(r.content)
    text = r.text

    # with open(os.path.join("data/project_reports", "{}.txt".format(ipid)), 'r') as f:
    #     text = f.read()

    pi_name = None
    try:
        pi_name = re.findall(ur'Lead Investigator.*?([A-Z].*?)\n', text, re.MULTILINE | re.DOTALL)[0]
    except IndexError:
        # print "no lead investigator found for {}".format(url)
        try:
            pi_name = re.findall(ur'<!-- faculty test -->\s*\n(.*)\n\s*', text)[0]
        except IndexError:
            print "no PI found for {}".format(url)

    if pi_name:
        print i, pi_name, ipid
        lookup = db.session.query(Person).filter(Person.normalized_name==normalize(pi_name)).all()
        if lookup:
            my_person = lookup[0]
        else:
            my_person = Person()
            my_person.raw_name = pi_name
            my_person.set_normalized_name()
            db.session.add(my_person)

        try:
            my_person.nih_id = re.findall(ur'https://irp.nih.gov/pi/(.*?)"', text)[0]
        except IndexError:
            pass

        try:
            in_press_articles = re.findall(u'^.*?\)\s*(.*?), in press', text, re.MULTILINE)
            for in_press_article in in_press_articles:
                title = in_press_article.rsplit(". ", 1)[0]
                if len(title) < 200:
                    # print title
                    url_pattern = u"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=({})&field=title&email=team@impactstory.org"
                    url = url_pattern.format(title)
                    r = requests.get(url)
                    data = r.json()
                    pmids = data["esearchresult"]["idlist"]
                    pmid = pmids[0]
                    print "found pmid", pmid, len(pmids)
                    pmids_for_this_ipid += [pmid]
        except IndexError:
            print "didn't find pmid"
            pass

        pmids_for_this_ipid += re.findall(u'https://www.ncbi.nlm.nih.gov/pubmed/(\d+)', text)

        for pmid in list(set(pmids_for_this_ipid)):
            if pmid:
                lookup = db.session.query(Pmid).filter(Pmid.id==pmid).all()
                if lookup:
                    new_pmid_obj = lookup[0]
                else:
                    new_pmid_obj = Pmid(id=pmid)
                    db.session.add(new_pmid_obj)
                new_pmid_obj.pi_id = my_person.id
                safe_commit(db)

        safe_commit(db)













