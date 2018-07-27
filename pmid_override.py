#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from sqlalchemy.dialects.postgresql import JSONB
from app import db
from app import logger
from sqlalchemy import orm
from util import normalize
import shortuuid
import datetime

from util import safe_commit


def add_pmid_override(pmid, key, value):
    print pmid, key, value
    my_pmid_override = PmidOverride(pmid=pmid, key=key, value=value)
    db.session.add(my_pmid_override)
    safe_commit(db)

class PmidOverride(db.Model):
    id = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime)
    pmid = db.Column(db.Text, db.ForeignKey('pmid.id'))
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()[0:10]
        self.created = datetime.datetime.now()
        super(self.__class__, self).__init__(**kwargs)

    def __repr__(self):
        return u"<PmidOverride ({}) {} {}={}>".format(self.id, self.pmid, self.key, self.value)


