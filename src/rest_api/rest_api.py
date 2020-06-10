from collections import Counter

from flask import request, jsonify, Flask, abort
from flask_rest_api import Api, Blueprint, abort
from datetime import datetime, date, time

from src.rest_api.rest_api_schemas import *
from src.cassandra.cluster import cluster

app = Flask('API')

app.config['OPENAPI_VERSION'] = '3.0.2'
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config['OPENAPI_SWAGGER_UI_VERSION'] = '3.3.0'
app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger_ui'
app.config['OPENAPI_REDOC_PATH'] = '/redoc_ui'

api = Api(app)
blp = Blueprint('api', 'api', url_prefix='/api/v1',
                description='Wikipedia Big Data Project')

session = cluster.connect('project', wait_for_all_pools=True)
session.set_keyspace('project')

cluster.connect()


@blp.route('/pages', methods=["GET"], strict_slashes=False)
@blp.arguments(PageByIdArgs, location='query')
@blp.response(PageByIdResponse(many=False),
              description="Return the page with the specified page_id.",
              example={
                  'id': 651784,
                  'url': 'https://sk.wikipedia.org/wiki/Modul:ConvertNumeric',
                  'title': 'Modul:ConvertNumeric',
                  'namespace': 828
              })
def get_page_by_id(_):
    """Get the the info about specified page_id

    Return the information about page
    """
    page_id = request.args.get('page_id')
    if not page_id:
        abort(422, message='Page ID must be not null.')

    page = session.execute("select url, title, namespace from pages where id = %s", (page_id,))
    if not page:
        abort(404, f'Page with ID = {page} not found')

    page = {name: (getattr(page, name)) for name in page._fields}
    return jsonify(page)


@blp.route('/pages/domains', methods=["GET"])
@blp.response(ListExistingDomainsResponse(many=True),
              description="Return the list of existing domains for which pages were created.",
              example=['domain1', 'domain2'])
def get_existing_domains():
    """Get the list the domains for which pages were created

    Return the list of domains
    """
    domains = list(session.execute("select domain from pages"))
    return jsonify(domains)


@blp.route('/pages/user', methods=["GET"])
@blp.arguments(PagesByUserArgs, location='query')
@blp.response(PagesByUserResponse(many=False),
              description="Return all the pages ids which were created by the user with a specified user_id.",
              example=[1, 2])
@blp.response(code=404, description="User not found.")
@blp.response(code=422, description="User id cannot be null.")
def get_pages_by_user(_):
    """Get all the pages which were created by the user with a specified user_id.

    Return the list of pages id"""
    user_id = request.args.get('user_id')
    if not user_id:
        abort(422, message='User id must be not null.')

    pages = list(session.execute("select page_id from users where id = %s", (user_id,)))
    if not pages:
        return abort(404, message=f'User with id={user_id} not found')

    return jsonify(pages)


@blp.route('/pages/domains/number', methods=["GET"])
@blp.arguments(PagesByDomainArgs, location='query')
@blp.response(PagesByDomainResponse(many=False),
              description="Return the number of articles created for a specified domain.",
              example={
                  'domain': 'domain1',
                  'number_of_pages': 2
              })
@blp.response(code=404, description="Domain not found.")
@blp.response(code=422, description="Domain cannot be null.")
def get_number_of_pages_by_user_id(_):
    """Get the number of articles created for a specified domain.

    Return the number of pages with domain"""
    domain = request.args.get('domain')
    if not domain:
        abort(422, message='Domain must be not null.')

    domains = list(session.execute("select page_id from pages where domain = %s", (domain,)))
    if not domains:
        abort(404, message=f'Domain {domain} not found')

    return jsonify(domains)


@blp.route('/users', methods=["GET"])
@blp.arguments(UsersArgs, location='query')
@blp.response(UsersResponse(many=True),
              description="Return the id, name, and the number of created pages of "
                          "all the users who created at least one page in a specified time range.",
              example={
                  'id': 1,
                  'name': 'username1',
                  'number_of_pages': 2
              })
def get_users_stats_by_date(_):
    """Get the the info about users who created at least one page in a specified time range.

    Return the information about users
    """

    def validate_date(date_string):
        try:
            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            return None

    start = request.args.get('start', datetime.combine(date.today(), time.min))
    end = request.args.get('end', datetime.now())

    start = datetime.combine(date.today(), time.min) if not start else validate_date(start)
    end = datetime.now() if end else validate_date(end)

    if not any([start, end]):
        abort(422, message=f'"{start if not start else end}" is not a correct value for date.')

    start = start.timestamp()
    end = end.timestamp()

    users = session.execute("select id, name, page_id, timestamp from users where timestamp >= %s and timestamp <= %s "
                            "allow filtering;",
                            (start, end))

    results = [{'id': x[0], 'name': x[1], 'number_of_pages': y} for x, y in
               Counter(
                   [(user.id, user.name, user.page_id) for
                    user in users]).most_common()]

    return jsonify(results)


api.register_blueprint(blp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
    cluster.shutdown()