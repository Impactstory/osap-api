#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app import logger
from nameparser import HumanName
import shortuuid
from sqlalchemy import orm
from util import normalize

from pmid import Pmid

class Person(db.Model):
    id = db.Column(db.Text, primary_key=True)
    raw_name = db.Column(db.Text)
    normalized_name = db.Column(db.Text)
    nih_id = db.Column(db.Text)

    pmids = db.relationship(
        'Pmid',
        lazy='subquery',
        cascade="all, delete-orphan",
        backref=db.backref("pi", lazy="subquery"),
        foreign_keys="Pmid.pi_id"
    )

    def __init__(self, **kwargs):
        self.id = shortuuid.uuid()[0:10]
        super(self.__class__, self).__init__(**kwargs)

    @orm.reconstructor
    def init_on_load(self):
        pass

    @property
    def parsed_name_simple_dict(self):
        simple_name_dict = {
            "family": self.parsed_name["last"],
            "given": self.parsed_name["first"],
            "middle": self.parsed_name["middle"],
            "suffix": self.parsed_name["suffix"]
        }
        return simple_name_dict

    @property
    def parsed_name(self):
        name_no_semicolons = self.raw_name.replace(";", ",")

        # hack because this is causing problems on "Peter A Bandettini, BS PhD")
        name_no_semicolons = name_no_semicolons.replace(", BSEE", "")
        name_no_semicolons = name_no_semicolons.replace(", BS", "")
        name_no_semicolons = name_no_semicolons.replace(", SB", "")
        name_no_semicolons = name_no_semicolons.replace(", MSSE", "")

        return HumanName(name_no_semicolons)

    @property
    def display_name(self):
        return u"{} {}".format(self.parsed_name.first, self.parsed_name.last)

    @property
    def nih_webpage(self):
        if not self.nih_id:
            return None
        return "https://irp.nih.gov/pi/{}".format(self.nih_id)

    def set_normalized_name(self):
        self.normalized_name = normalize(self.raw_name)

    @property
    def num_pubs(self):
        return len(self.pmids)

    @property
    def score_oa(self):
        if self.num_pubs == 0:
            return 0

        num = 0.0
        for pmid_pub in self.pmids:
            if pmid_pub.open_status_paper != "closed":
                num += 1.0
        return num/self.num_pubs

    @property
    def score_code(self):
        if self.num_pubs == 0:
            return 0

        num = 0.0
        for pmid_pub in self.pmids:
            if pmid_pub.open_status_code != "closed":
                num += 1.0
        return num/self.num_pubs

    @property
    def score_data(self):
        if self.num_pubs == 0:
            return 0

        num = 0.0
        for pmid_pub in self.pmids:
            if pmid_pub.open_status_data != "closed":
                num += 1.0
        return num/self.num_pubs

    @property
    def score_total(self):
        return round((0.0+ self.score_oa + self.score_code + self.score_data) / 3, 3)

    def to_dict_detailed(self):
        response = self.to_dict_summary()
        response["papers"] = [p.to_dict() for p in self.pmids]
        return response


    def to_dict_summary(self):
        response = {
            "id": self.id,
            "name": self.parsed_name_simple_dict,
            "nih_webpage": self.nih_webpage,
            "num_papers": self.num_pubs,
            "scores": {
                "paper": self.score_oa,
                "code": self.score_code,
                "data": self.score_data,
                "total": self.score_total
            }
        }
        return response

    def __repr__(self):
        return u"<Person ({}) {}, {} pubs>".format(self.id, self.display_name, self.num_pubs)


