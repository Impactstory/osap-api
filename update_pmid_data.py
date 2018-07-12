from app import db
from person import Person
from pmid import Pmid
from util import safe_commit

loop = 0
pmid_pubs = Pmid.query.all()
pmid_pubs = [Pmid.query.get("27347888")]
for pmid_pub in pmid_pubs:
    print pmid_pub.europepmc_api_raw
    if not pmid_pub.europepmc_api_raw or \
                    pmid_pub.europepmc_api_raw == "null" or \
                    pmid_pub.display_score_oa != 1:
        pmid_pub.update_from_europepmc()
    print pmid_pub.europepmc_api_raw
    pmid_pub.update_score_oa()
    # pmid_pub.update_score_code()
    # pmid_pub.update_score_data()
    print u"updated {}!".format(pmid_pub.id)
    loop += 1
    if loop > 25:
        safe_commit(db)
        loop = 0
safe_commit(db)

