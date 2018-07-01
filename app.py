from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_compress import Compress
from sqlalchemy.pool import NullPool

import logging
import sys
import os
import requests


# set up logging
# see http://wiki.pylonshq.com/display/pylonscookbook/Alternative+logging+configuration
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(name)s - %(message)s'
)
logger = logging.getLogger("osat-api")

libraries_to_mum = [
    "requests.packages.urllib3",
    "requests.packages.urllib3.connectionpool",
    "requests_oauthlib",
    "urllib3.connectionpool"
    "stripe",
    "oauthlib",
    "boto",
    "citeproc",
    "newrelic",
    "RateLimiter",
    "requests",
    "urllib3",
    "paramiko",
    "chardet"
]

for a_library in libraries_to_mum:
    the_logger = logging.getLogger(a_library)
    the_logger.setLevel(logging.WARNING)
    the_logger.propagate = True

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

# database stuff
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True  # as instructed, to suppress warning
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_ECHO'] = (os.getenv("SQLALCHEMY_ECHO", False) == "True")

# from http://stackoverflow.com/a/12417346/596939
class NullPoolSQLAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        options['poolclass'] = NullPool
        return super(NullPoolSQLAlchemy, self).apply_driver_hacks(app, info, options)

db = NullPoolSQLAlchemy(app, session_options={"autoflush": False})

# do compression.  has to be above flask debug toolbar so it can override this.
compress_json = os.getenv("COMPRESS_DEBUG", "False")=="True"

# gzip responses
Compress(app)
app.config["COMPRESS_DEBUG"] = compress_json

