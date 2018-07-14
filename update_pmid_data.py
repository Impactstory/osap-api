from app import db
from person import Person
from pmid import Pmid
from util import safe_commit

loop = 0
pmid_pubs = Pmid.query.all()
for pmid_pub in pmid_pubs:
    if not pmid_pub.europepmc_api_raw or pmid_pub.europepmc_api_raw == "null":
        pmid_pub.update_from_europepmc()
    pmid_pub.update_open_status_paper()
    pmid_pub.update_open_status_code()
    pmid_pub.update_open_status_data()
    print u"updated {}!".format(pmid_pub.id)
    loop += 1
    if loop > 25:
        safe_commit(db)
        loop = 0
safe_commit(db)

