import marshmallow as ma
from datetime import datetime, date, time


class ListExistingDomainsArgs(ma.Schema):
    page_id = ma.fields.Integer(description='Page ID')


class ListExistingDomainsResponse(ma.Schema):
    domain = ma.fields.String(description='Domain name')
    domain_list = ma.fields.List(domain, description='List of domains for which pages were created')


class PagesByUserArgs(ma.Schema):
    user_id = ma.fields.Integer(description='User ID')


class PagesByUserResponse(ma.Schema):
    page_id = ma.fields.Integer(description='Page ID')
    page_list = ma.fields.List(page_id, description='List of pages id for specified user_id')


class PagesByDomainArgs(ma.Schema):
    domain = ma.fields.String(description='Domain')


class PagesByDomainResponse(ma.Schema):
    domain = ma.fields.String(description='Domain name')
    number_of_pages = ma.fields.Integer(description='Number of created pages for specified domain')


class PageByIdArgs(ma.Schema):
    page_id = ma.fields.Integer(description='Page ID')


class PageByIdResponse(ma.Schema):
    page_id = ma.fields.Integer(description='Page ID')
    url = ma.fields.URL(description='Url of the page')
    title = ma.fields.String(description='Title of the page')
    domain = ma.fields.String(description='Domain name')
    namespace = ma.fields.Integer(description='Namespace of the page')


class UsersArgs(ma.Schema):
    start = ma.fields.DateTime('%Y-%m-%dT%H:%M:%SZ',
                               description='From date in format Y-m-dTH:M:SZ. If not specified, set to today 00:00:00',
                               missing=datetime.combine(date.today(), time.min))
    end = ma.fields.DateTime('%Y-%m-%dT%H:%M:%SZ',
                             description='To date in format Y-m-dTH:M:SZ. If not specified, set to now',
                             missing=datetime.now())


class UsersResponse(ma.Schema):
    id = ma.fields.Integer(description='User ID')
    name = ma.fields.String(description='User name')
    number_of_pages = ma.fields.Integer(description='Number of created pages for specified user')


class CreatedPagesStats(ma.Schema):
    statistics = ma.fields.Dict(keys=ma.fields.String(description='Domain name'),
                                values=ma.fields.Integer(
                                    description='Number of created pages for domain'))


class CreatedPagesDomainsResponse(ma.Schema):
    time_start = ma.fields.String(description='From time')
    time_end = ma.fields.String(description='To time')
    statistics = ma.fields.List(ma.fields.Nested(CreatedPagesStats), description='Statistics for created pages')


class PagesBots(ma.Schema):
    domain = ma.fields.String(description='Domain name')
    created_by_bots = ma.fields.Integer(description='Number of pages for the domain that are created by bots')


class CreatedPagesBotsResponse(ma.Schema):
    time_start = ma.fields.String(description='From time')
    time_end = ma.fields.String(description='To time')
    statistics = ma.fields.List(ma.fields.Nested(PagesBots),
                                description='Number of created pages by bots for domain')


class UsersByPagesResponse(ma.Schema):
    time_start = ma.fields.String(description='From time')
    time_end = ma.fields.String(description='To time')
    user_name = ma.fields.String(description='User name')
    user_id = ma.fields.String(description='User ID')
    page_titles = ma.fields.List(ma.fields.String(description='Page title'))
    number_of_pages = ma.fields.Integer(description='Number of created pages for user')
