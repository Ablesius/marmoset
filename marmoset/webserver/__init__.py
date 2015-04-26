from flask import Flask, jsonify
from flask.ext import restful
from marmoset import config
from .flask import auth
from . import pxe, vm


def jsonify_nl(*args, **kwargs):
    resp = jsonify(*args, **kwargs)
    resp.set_data(resp.get_data() + b'\n')
    return resp


def run(args):
    auth.Username  = config['Webserver'].get('Username')
    auth.Password  = config['Webserver'].get('Password')

    app = Flask(config['Webserver'].get('BasicRealm'))
    auth.for_all_routes(app)
    app.config['SERVER_NAME'] = config['Webserver'].get('ServerName')

    api = restful.Api(app)

    api.add_resource(pxe.PXECollection, '/pxe')
    api.add_resource(pxe.PXEObject, '/pxe/<ip_address>')
    api.add_resource(vm.VMCollection, '/vm')
    api.add_resource(vm.VMObject, '/vm/<uuid>')
    api.add_resource(vm.VMCommand, '/vm/<uuid>/action')

    @app.errorhandler(404)
    def not_found(ex):
        resp = jsonify_nl(message="Route not found.", status=404)
        resp.status_code = 404
        return resp

    @app.errorhandler(401)
    def not_found(ex):
        resp = jsonify_nl(message="Unauthorized", status=401)
        resp.status_code = 401
        return resp

    print(app.url_map)

    app.run(
        host = config['Webserver'].get('Host'),
        port = config['Webserver'].get('Port'),
        debug = config['Webserver'].getboolean('Debug')
    )

from . import subparser
