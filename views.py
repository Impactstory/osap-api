from flask import make_response
from flask import request
from flask import abort
from flask import render_template
from flask import jsonify
from nameparser import HumanName

import json
import os
import sys
import requests
import re
from util import normalize

from app import app

def json_dumper(obj):
    """
    if the obj has a to_dict() function we've implemented, uses it to get dict.
    from http://stackoverflow.com/a/28174796
    """
    try:
        return obj.to_dict()
    except AttributeError:
        return obj.__dict__


def json_resp(thing):
    json_str = json.dumps(thing, sort_keys=True, default=json_dumper, indent=4)

    if request.path.endswith(".json") and (os.getenv("FLASK_DEBUG", False) == "True"):
        print u"rendering output through debug_api.html template"
        resp = make_response(render_template(
            'debug_api.html',
            data=json_str))
        resp.mimetype = "text/html"
    else:
        resp = make_response(json_str, 200)
        resp.mimetype = "application/json"
    return resp


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



# FUNCTIONS. move this to another file later.
#
######################################################################################



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




# ENDPOINTS
#
######################################################################################


@app.route('/', methods=["GET"])
def index_endpoint():
    return jsonify({
        "version": "0.1",
        "documentation_url": "none yet",
        "msg": "Don't panic"
    })

@app.route('/persons', methods=["GET"])
def get_persons():
    names = list(set(['Mortimer  Mishkin, PhD ', 'Carolyn E Beebe, PhD ', 'Miles  Herkenham, PhD ', 'Mortimer  Mishkin, PhD ', 'Barry J Richmond, MD ', 'Leslie G Ungerleider, PhD ', 'Mortimer  Mishkin, PhD ', 'Lee E Eiden, PhD ', 'Charles R Gerfen, PhD ', 'Walter Scott Young, MD, PhD ', 'Peter J Schmidt, MD ', 'Judith L Rapoport, MD ', 'Alex  Martin, PhD ', 'Barry J Richmond, MD ', 'Karen F Berman, MD ', 'Susan Elizabeth Swedo, MD ', 'Karen F Berman, MD ', 'Elisabeth Adams Murray, PhD ', 'Barry Bernard Kaplan, PhD ', 'Ellen  Leibenluft, MD ', 'Daniel  Pine, MD ', 'Daniel  Pine, MD ', 'Peter A Bandettini, BS, PhD ', 'Heather A Cameron, PhD ', 'Ellen  Leibenluft, MD ', 'Victor W Pike, PhD ', 'Robert  Innis, MD ', 'Dietmar  Plenz, PhD ', 'Christian  Grillon, PhD ', 'Benjamin H White, PhD ', 'Jun  Shen, PhD ', 'Kathleen R Merikangas, PhD ', 'Francis Joseph McMahon, MD ', 'David A Leopold, PhD ', 'Francis Joseph McMahon, MD ', 'Francis Joseph McMahon, MD ', 'Robert  Innis, MD ', 'Carlos Alberto Zarate, MD ', 'Karen F Berman, MD ', 'Peter J Schmidt, MD ', 'Susan Elizabeth Swedo, MD ', 'Peter J Schmidt, MD ', 'Zheng  Li, PhD ', 'Zheng  Li, PhD ', 'Elisabeth Adams Murray, PhD ', 'Elisabeth Adams Murray, PhD ', 'Richard  Coppola, SB, DSc ', 'Christopher Ian Baker, PhD ', 'David A Leopold, PhD ', 'Kuan Hong Wang, PhD ', 'David A Leopold, PhD ', 'Christopher Ian Baker, PhD ', 'Susan G Amara, PhD ', 'Leslie G Ungerleider, PhD ', 'Alex  Martin, PhD ', 'Maryland  Pao, MD ', 'Carlos Alberto Zarate, MD ', 'Bruno B Averbeck ', 'Peter J Schmidt, MD ', 'Carolyn E Beebe, PhD ', 'Carolyn E Beebe, PhD ', 'Karen F Berman, MD ', 'Susan G Amara, PhD ', 'Carolyn E Beebe, PhD ', 'Armin  Raznahan ', 'Mario Alexander Penzo ', 'Yogita  Chudasama, PhD ', 'Kathleen R Merikangas, PhD ', 'Kathleen R Merikangas, PhD ', 'Sarah Hollingsworth Lisanby ', 'Mark H Histed, PhD ', 'Argyrios  Stringaris ', 'Arash  Afraz, MD, PhD ', 'Soohyun  Lee ', 'Samer Saleh Hattar ', 'Yin Y Yao, PhD ', 'Elisha Prem Merriam ', 'Mark H Histed, PhD ', 'Peter A Bandettini, BS, PhD ', 'Robert  Cox, PhD ', 'Richard  Coppola, SB, DSc ', 'Jun  Shen, PhD ', 'David A Leopold, PhD ', 'James M Pickel, AB, PhD ', 'Barbara K Lipska, PhD ', 'George Raphael Dold, MME, BSEE ', 'Yogita  Chudasama, PhD ', 'Adam G Thomas, PhD ', 'Audrey E Thurm, PhD ', 'Ashura  Buckley ', 'Theodore B Usdin, MD, PhD ', 'Maryland  Pao, MD ', 'Maryland  Pao, MD ', 'James  Raber, DVM, PhD ', 'Susan G Amara, PhD ', 'Janet Elizabeth Clark ', 'Jennifer S Wong ']))
    persons = []
    for name in names:
        full_name_dict = HumanName(name).as_dict()
        simple_name_dict = {
            "family": full_name_dict["last"],
            "given": full_name_dict["first"],
            "middle": full_name_dict["middle"],
            "suffix": full_name_dict["suffix"]
        }
        clean_name = name.strip()
        id = normalize(u"{} {}".format(full_name_dict["first"], full_name_dict["last"]))
        oa_score = round(.8 + .2*((ord(id[0]) - 96.0) / 26), 3)
        code_score = round(0.2 * (ord(id[1]) - 96.0) / 26, 3)
        data_score = round(0.2 * (ord(id[2]) - 96.0) / 26, 3)
        persons.append({
            "id": id,
            "name": simple_name_dict,
            "num_papers": 3 * len(clean_name),
            "scores": {
                "oa": oa_score,
                "code": code_score,
                "data": data_score,
                "total": round((oa_score + code_score + data_score) / 3, 3)
            }
        })

    sorted_persons = sorted(persons, key=lambda k: k["scores"]["total"], reverse=True)

    return jsonify({"response": sorted_persons})

#
#
# @app.route("/product/<path:id>", methods=["GET"])
# def citeas_product_get(id):
#     my_software = Software(id)
#     my_software.find_metadata()
#     return jsonify(my_software.to_dict())
#
# @app.route("/steps", methods=["GET"])
# @app.route("/steps/", methods=["GET"])
# def citeas_step_configs():
#     return jsonify(step_configs())





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)

















