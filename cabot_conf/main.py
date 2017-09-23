import argparse
import json
import logging
import urlparse

import requests
from requests.auth import HTTPBasicAuth

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def factory_reset(args):
    """Delete all objects."""

    for name in [
            'instances',
            'services',
            'status_checks',
    ]:
        found = requests.get(
            urlparse.urljoin(args.cabot, 'api/{}/'.format(name)),
            auth=HTTPBasicAuth(args.user, args.password),
        ).json()
        if found is None:
            return 1
        for item in found:
            requests.delete(
                url=urlparse.urljoin(
                    args.cabot,
                    'api/{}/{}'.format(name, item['id'])
                ),
                auth=HTTPBasicAuth(args.user, args.password),
            )


def create(args):
    """Create objects."""

    def post(subpage, data):
        """Wrap requests.post."""
        url = urlparse.urljoin(
            args.cabot,
            'api/{}/'.format(subpage),
        )
        try:
            result = requests.post(
                url=url,
                data=json.dumps(data),
                headers={
                    'Content-Type': 'application/json'
                },
                auth=HTTPBasicAuth(args.user, args.password),
            )
        except requests.exceptions.ConnectionError as e:
            logger.error('ConnectionError on url {}: {}'.format(url, e))
            return None
        if result.status_code >= 400:
            logger.warning(
                'Post failed (status code {}):'
                '\nurl: {}'
                '\ndata: {}'
                '\nbody: {}'.format(
                    result.status_code,
                    url,
                    data,
                    result.text
                )
            )
            return None
        return result.json()

    config = json.load(open(args.config, 'r'))

    services = {}
    instances = {}
    checks = {}

    for check_type in [
            'graphite_checks',
            'icmp_checks',
            'jenkins_checks',
            'http_checks'
    ]:
        for element in config[check_type]:
            ref = element.pop('ref')
            created = post(
                check_type,
                data=element,
            )
            checks[ref] = created['id'] if created else None

    for element in config['services']:
        ref = element.pop('ref')
        element['status_checks'] = [
            checks[check_ref] for check_ref in element['status_checks']
        ]
        created = post(
            'services',
            data=element,
        )
        services[ref] = created['id']

    for element in config['instances']:
        ref = element.pop('ref')
        element['status_checks'] = [
            checks[check_ref] for check_ref in element['status_checks']
        ]
        created = post(
            'instances',
            data=element,
        )
        instances[ref] = created['id'] if created else None


def main():
    """Read the config file and make cabot api requests."""
    parser = argparse.ArgumentParser(
        description='Set up Cabot using a config file.'
    )
    parser.add_argument('config', help='Config file')
    parser.add_argument(
        '-r',
        '--factory_reset',
        help='Remove all existing objects, indiscriminately.',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '-c',
        '--cabot',
        help='Cabot host',
        required=True
    )
    parser.add_argument(
        '-u',
        '--user',
        help='Cabot user',
        required=True
    )
    parser.add_argument(
        '-p',
        '--password',
        help='Cabot password',
        required=True
    )
    args = parser.parse_args()

    if args.factory_reset:
        factory_reset(args)

    create(args)


if __name__ == '__main__':
    main()
