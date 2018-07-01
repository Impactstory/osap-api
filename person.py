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

    def to_dict_detailed(self):
        response = self.to_dict_summary()
        response["pmids"] = [p.to_dict() for p in self.pmids]
        return response


    def to_dict_summary(self):
        oa_score = round(.8 + .2*((ord(self.display_name[2]) - 96.0) / 26), 3)
        code_score = round(0.2 * (ord(self.display_name[3]) - 96.0) / 26, 3)
        data_score = round(0.2 * (ord(self.display_name[4]) - 96.0) / 26, 3)
        response = {
            "id": self.id,
            "name": self.parsed_name_simple_dict,
            "nih_webpage": self.nih_webpage,
            "num_papers": len(self.pmids),
            "scores": {
                "oa": oa_score,
                "code": code_score,
                "data": data_score,
                "total": round((oa_score + code_score + data_score) / 3, 3)
            }
        }
        return response

    def __repr__(self):
        return u"<Person ({}) {}, {} pubs>".format(self.id, self.display_name, self.num_pubs)


