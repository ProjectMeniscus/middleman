from keystoneclient.v2_0.client import Client as KeystoneClient
from keystoneclient.exceptions import Unauthorized

from flask import Flask
from flask import request

from middleman.config import load_middleman_config
from middleman.log import get_logger, get_log_manager
from middleman.util.request import http_request

import uwsgi


_CONFIG = load_middleman_config()
_LOGGING_MANAGER = get_log_manager()
_LOGGING_MANAGER.configure(_CONFIG)
_LOG = get_logger(__name__)

_KEYSTONE_CLIENT = KeystoneClient(
    token=_CONFIG.keystone.auth_token,
    timeout=_CONFIG.keystone.timeout,
    endpoint=_CONFIG.keystone.endpoint,
    insecure=_CONFIG.keystone.insecure)

X_AUTH_TOKEN = 'X-Auth-Token'
X_TENANT_NAME = 'X-Tenant-Name'

application = Flask(__name__)


def _cached_token_exists(token):
    if uwsgi.cache_get(token, _CONFIG.cache.cache_name) is not None:
        return True
    return False


def _token_is_valid(token, tenant_name):
    token_in_cache = _cached_token_exists(token)

    if not token_in_cache:
        try:
            auth_result = _KEYSTONE_CLIENT.tokens.authenticate(
                token=token, tenant_name=tenant_name)

            if auth_result:
                tenant_id = auth_result.tenant.get('id', None)
                _cache_set_token(token, tenant_id)
                return True, tenant_id
        except Unauthorized:
            return False, None
        except Exception as ex:
            _LOG.exception(ex)

    if token_in_cache:
        return True, _cache_get_tenant_id(token)

    return False, None


def _cache_set_token(token, tenant_id):
    uwsgi.cache_set(token, tenant_id, _CONFIG.cache.ttl,
                    _CONFIG.cache.cache_name)


def _cache_get_tenant_id(token):
    return uwsgi.cache_get(token, _CONFIG.cache.cache_name)


def _build_url(url, tenant_id=None):
    if tenant_id is None:
        return _CONFIG.elasticsearch.endpoint + url
    else:
        return _CONFIG.elasticsearch.endpoint + \
            url.replace(_CONFIG.keystone.url_replacement, tenant_id)


@application.route('/<path:remaining_url>', methods=['GET'])
def on_get(remaining_url):
    #reject GET requests for search until token added to GET in Kibana
    if "_search" in remaining_url.lower():
        return 'Unauthorized', 401

    try:
        response = http_request(url=_build_url(remaining_url, None),
                                http_verb='GET',
                                request_timeout=_CONFIG.elasticsearch.timeout)
        return response.content
    except Exception as ex:
        _LOG.exception(ex)
        return '', 500


@application.route('/<path:remaining_url>', methods=['POST'])
def on_post(remaining_url):
    try:
        token = request.headers.get(X_AUTH_TOKEN)
        tenant_name = request.headers.get(X_TENANT_NAME)

        if token is None or tenant_name is None:
            return "Unauthorized", 401

        token_is_valid, tenant_id = _token_is_valid(token, tenant_name)

        if token_is_valid:
            response = http_request(url=_build_url(remaining_url, tenant_id),
                                    payload=request.data, http_verb='POST',
                                    request_timeout=
                                    _CONFIG.elasticsearch.timeout)
            return response.content
    except Exception as ex:
        _LOG.exception(ex)
        return '', 500

    return 'Unauthorized', 401
