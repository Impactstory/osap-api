from app import db
from person import Person
from pmid import Pmid
from util import safe_commit

loop = 0
pmid_pubs = Pmid.query.all()
for pmid_pub in pmid_pubs:
    # pmid_pub.update_from_europepmc()
    # pmid_pub.update_score_oa()
    # pmid_pub.update_score_code()
    pmid_pub.update_score_data()
    print u"updated {}!".format(pmid_pub.id)
    loop += 1
    if loop > 25:
        safe_commit(db)
        loop = 0
safe_commit(db)

