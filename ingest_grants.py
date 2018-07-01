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
report_year_files = "nimh2013.htm nimh2014.htm nimh2015.htm nimh2016.htm nimh2017.htm".split()
ipids = []
for report_year_file in report_year_files:
    with open(os.path.join("data", report_year_file), 'r') as f:
        file_contents = f.read()
    new_ipids = re.findall("ipid=(\d+)", file_contents)
    print len(list(set(new_ipids)))
    ipids += new_ipids
ipids = list(set(ipids))
print len(ipids)

people = []
pmids = []
for ipid in ipids:
    url = "https://intramural.nih.gov/search/searchview.taf?ipid={}".format(ipid)
    print url
    r = requests.get(url)
    with open(os.path.join("data", "{}.txt".format(ipid)), 'w') as f:
        f.write(r.content)

    pi_name = None
    try:
        pi_name = re.findall(ur'<!-- faculty test -->\s*\n(.*)\n\s*<', r.text)[0]
        print "pi_name", pi_name
    except IndexError:
        print "no PI found for {}".format(url)

    if pi_name:
        lookup = db.session.query(Person).filter(Person.normalized_name==normalize(pi_name)).all()
        if lookup:
            my_person = lookup[0]
        else:
            my_person = Person()
            my_person.raw_name = pi_name
            my_person.set_normalized_name()
            db.session.add(my_person)
        safe_commit(db)

        try:
            my_person.nih_id = re.findall(ur'https://irp.nih.gov/pi/(.*?)"', r.text)[0]
        except IndexError:
            pass

        new_pmids = re.findall(u'https://www.ncbi.nlm.nih.gov/pubmed/(\d+)', r.text)
        new_pmid_objects = []
        for pmid in list(set(new_pmids)):
            if pmid and not Pmid.query.filter(id==pmid).all():
                new_pmid_obj = Pmid(id=pmid)
                new_pmid_objects.append(new_pmid_obj)
                new_pmid_obj.pi_id = my_person.id
                db.session.merge(new_pmid_obj)
                pmids += [pmid]

        people.append(my_person)
        db.session.merge(my_person)
        safe_commit(db)

print pmids












