import requests
from middleman.log import get_logger


_LOG = get_logger(__name__)


# For this project only GET and POST are supported
HTTP_VERBS = (
    'GET',
    'POST'
)


def http_request(url, add_headers=None, payload='', http_verb='GET',
                 request_timeout=15.0):
    headers = {'content-type': 'application/json'}

    if add_headers:
        headers.update(add_headers)
    http_verb = str(http_verb).upper()

    if not http_verb in HTTP_VERBS:
        raise ValueError(
            'Invalid HTTP verb supplied: {0}'.format(http_verb))

    try:
        if http_verb == 'GET':
            return requests.get(url, headers=headers, timeout=request_timeout)
        elif http_verb == 'POST':
            return requests.post(url, data=payload, headers=headers,
                                 timeout=request_timeout)

    except requests.ConnectionError as conn_err:
        _LOG.exception(conn_err)
        raise conn_err
    except requests.HTTPError as http_err:
        _LOG.exception(http_err)
        raise http_err
    except requests.RequestException as req_err:
        _LOG.exception(req_err)
        raise req_err
