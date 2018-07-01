#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
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
    score_oa = db.Column(db.Numeric)
    score_code = db.Column(db.Numeric)
    score_data = db.Column(db.Numeric)

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    @orm.reconstructor
    def init_on_load(self):
        pass

    def call_europepmc(self, filter=None):
        url_template = u'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=(EXT_ID:"{id}"{filter})&resulttype=core&format=json&email=team@impactstory.org'
        url = url_template.format(id=self.id, filter=filter)
        r = requests.get(url)
        data = r.json()
        if data["hitCount"] == 1:
            return data["resultList"]["result"][0]
        return None

    def update_from_europepmc(self):
        response = self.call_europepmc()
        self.europepmc_api_raw = response

    def get_from_europepmc_api_raw(self, field):
        if not self.europepmc_api_raw:
            return None
        if field not in self.europepmc_api_raw:
            return None
        return self.europepmc_api_raw[field]

    def update_score_oa(self):
        self.score_oa = 0
        if self.derived_pmcid:
            self.score_oa = 1

    def update_score_code(self):
        self.score_code = 0
        filter = "+and+github"
        response = self.call_europepmc(filter)
        if response:
            print "found open code!"
            self.score_code = 1

    def update_score_data(self):
        self.score_data = 0
        filter = "+and+dryad"
        response = self.call_europepmc(filter)
        if response:
            print "found open data!"
            self.score_data = 1

    @property
    def derived_pmcid(self):
        return self.get_from_europepmc_api_raw("pmcid")

    @property
    def doi(self):
        return self.get_from_europepmc_api_raw("doi")

    @property
    def title(self):
        return self.get_from_europepmc_api_raw("title")

    @property
    def year(self):
        return self.get_from_europepmc_api_raw("pubYear")

    @property
    def authors(self):
        return self.get_from_europepmc_api_raw("authorString")

    def to_dict(self):
        response = {
            "pmid": self.id,
            "pubmed_url": u"https://www.ncbi.nlm.nih.gov/pubmed/{}".format(self.id),
            "metadata": {
                "pmcid": self.derived_pmcid,
                "doi": self.doi,
                "title": self.title,
                "year": self.year,
                "authors": self.authors,
                "journal": "Nature"
            },
            "scores": {
                "oa": self.score_oa,
                "code": self.score_code,
                "data": self.score_data
            }
        }
        return response

    def __repr__(self):
        return u"<Pmid ({}, {})>".format(self.id, self.pmcid)


