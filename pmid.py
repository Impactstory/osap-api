#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from sqlalchemy.dialects.postgresql import JSONB
from app import db
from app import logger
from sqlalchemy import orm
from util import normalize
import datetime

class Pmid(db.Model):
    id = db.Column(db.Text, primary_key=True)
    pi_id = db.Column(db.Text, db.ForeignKey('person.id'))
    europepmc_api_raw = db.Column(JSONB)
    open_status_paper = db.Column(db.Text)
    open_status_code = db.Column(db.Text)
    open_status_data = db.Column(db.Text)

    overrides = db.relationship(
        'PmidOverride',
        lazy='subquery',
        cascade="all, delete-orphan",
        backref=db.backref("pmid_override", lazy="subquery"),
        foreign_keys="PmidOverride.pmid"
    )

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    @orm.reconstructor
    def init_on_load(self):
        pass

    def call_europepmc(self, filter=""):
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

    @property
    def overrides_newest_first(self):
        pass

    @property
    def has_override(self, key):
        return [key in override.key for override in self.overrides]

    @property
    def override(self, key):
        for override in self.overrides_newest_first:
            if override.key == key:
                return override.value
        return None

    @property
    def has_open_data(self):
        if self.has_override("data"):
            return self.override("data")
        if self.open_status_data in ["open"]:
            return True
        return False

    @property
    def has_open_code(self):
        if self.has_override("code"):
            return self.override("code")
        if self.open_status_code in ["open"]:
            return True
        return False

    @property
    def has_open_paper(self):
        if self.has_override("paper"):
            return self.override("paper")
        if self.open_status_paper in ["open", "embargo"]:
            return True
        return False

    def update_open_status_paper(self):
        self.open_status_paper = "closed"
        if self.derived_pmcid:
            self.open_status_paper = "open"
        elif self.europepmc_api_raw:
            published_date = self.europepmc_api_raw["firstPublicationDate"]
            # if it has an embargo date it is under embargo
            if "embargoDate" in self.europepmc_api_raw and self.europepmc_api_raw["embargoDate"] > datetime.datetime.now().isoformat():
                print "under embargo", self.id
                self.open_status_paper = "embargo"
            # or if it is less than a year old it is under embargo
            elif published_date > (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat():
                print "under embargo", self.id
                self.open_status_paper = "embargo"

    def update_open_status_code(self):
        self.open_status_code = "closed"
        filter = "+and+github"
        response = self.call_europepmc(filter)
        if response:
            print "found open code!"
            self.open_status_code = "open"

    def update_open_status_data(self):
        self.open_status_data = "closed"
        filter = "+and+(dryad+or+figshare+or+dataverse+or+openneuro.org+or+ndar)"
        response = self.call_europepmc(filter)
        if response:
            print "found open data!"
            self.open_status_data = "open"

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

    def to_dict_sparkline(self):
        response = {
            "pmid": self.id,
            "metadata": {
                "year": self.year,
            },
            # "is_open": {
            #     "paper": self.has_open_paper,
            #     "code": self.has_open_code,
            #     "data": self.has_open_data
            # },
            "open_status": {
                "paper": self.open_status_paper,
                "code": self.open_status_code,
                "data": self.open_status_data,
            }
        }
        return response

    def to_dict(self):
        response = {
            "pmid": self.id,
            "metadata": {
                "pubmed_url": u"https://www.ncbi.nlm.nih.gov/pubmed/{}".format(self.id),
                "pmcid": self.derived_pmcid,
                "doi": self.doi,
                "title": self.title,
                "year": self.year,
                "authors": self.authors
            },
            # "is_open": {
            #     "paper": self.has_open_paper,
            #     "code": self.has_open_code,
            #     "data": self.has_open_data
            # },
            "open_status": {
                "paper": self.open_status_paper,
                "code": self.open_status_code,
                "data": self.open_status_data,
            }
        }
        return response

    def __repr__(self):
        return u"<Pmid ({}, {})>".format(self.id, self.derived_pmcid)


