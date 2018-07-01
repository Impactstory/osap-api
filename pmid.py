#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy.dialects.postgresql import JSONB
from app import db
from app import logger
from sqlalchemy import orm
from util import normalize

class Pmid(db.Model):
    id = db.Column(db.Text, primary_key=True)
    pmcid = db.Column(db.Text)
    pi_id = db.Column(db.Text, db.ForeignKey('person.id'))
    europepmc_api_raw = db.Column(JSONB)

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    @orm.reconstructor
    def init_on_load(self):
        pass

    def to_dict(self):
        response = {
            "pmid": self.id,
            "pmcid": self.pmcid
        }
        return response

    def __repr__(self):
        return u"<Pmid ({}, {})>".format(self.id, self.pmcid)


