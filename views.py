from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask import jsonify
from nameparser import HumanName
import json
import os
import sys
import shortuuid

from app import app
from app import db
from person import Person
from pmid import Pmid
from pmid_override import add_pmid_override


def abort_json(status_code, msg):
    body_dict = {
        "HTTP_status_code": status_code,
        "message": msg,
        "error": True
    }
    resp_string = json.dumps(body_dict, sort_keys=True, indent=4)
    resp = make_response(resp_string, status_code)
    resp.mimetype = "application/json"
    abort(resp)


@app.after_request
def after_request_stuff(resp):
    #support CORS
    resp.headers['Access-Control-Allow-Origin'] = "*"
    resp.headers['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS, PUT, DELETE, PATCH"
    resp.headers['Access-Control-Allow-Headers'] = "origin, content-type, accept, x-requested-with"

    # without this jason's heroku local buffers forever
    sys.stdout.flush()

    return resp


def print_ip():
    user_agent = request.headers.get('User-Agent')
    # from http://stackoverflow.com/a/12771438/596939
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr
    print u"calling from IP {ip}. User-Agent is '{user_agent}'.".format(
        ip=ip,
        user_agent=user_agent
    )


@app.route('/', methods=["GET"])
def index_endpoint():
    return jsonify({
        "version": "0.1",
        "documentation_url": "none yet",
        "msg": "Don't panic"
    })


@app.route('/person/<id>', methods=["GET"])
def get_person(id):
    my_person = Person.query.get(id)
    return jsonify(my_person.to_dict_detailed())


@app.route('/persons', methods=["GET"])
def get_persons():
    responses = [p.to_dict_summary() for p in Person.query.all()]
    sorted_responses = sorted(responses, key=lambda k: k["scores"]["total"], reverse=True)
    return jsonify({"results": sorted_responses})


@app.route('/papers', methods=["GET"])
def get_papers():
    responses = [p.to_dict_sparkline() for p in Pmid.query.all()]
    return jsonify({"results": responses})

@app.route('/paper/<pmid>', methods=["GET"])
def get_paper(pmid):
    my_paper = Pmid.query.get(pmid)
    return jsonify(my_paper.to_dict())

# curl -d '{"is_na":true}' -H "Content-Type: application/json" -X POST http://localhost:5002/paper/26654786/open_status/code
# curl -d '{"link":"http://cnn.com"}' -H "Content-Type: application/json" -X POST http://localhost:5002/paper/26654786/open_status/data


@app.route('/paper/<pmid>/open_status/<genre>', methods=["POST"])
def open_status_post(pmid, genre):
    add_pmid_override(pmid, genre, **request.json)
    my_paper = Pmid.query.get(pmid)
    return jsonify(my_paper.to_dict())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

