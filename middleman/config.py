from middleman.util.config import (load_config, ConfigurationPart,
                                   ConfigurationError)


_DEFAULTS = {
    'logging': {
        'console': True,
        'logfile': None,
        'verbosity': 'WARNING'
    },
    'keystone': {
        'auth_token': None,
        'timeout': 5,
        'insecure': False,
        'endpoint': 'http://localhost:35357/v2.0/tokens',
        'url_replacement': ''
    },
    'cache': {
        'cache_name': 'cache-token',
        'ttl': 3600
    },
    'elasticsearch': {
        'endpoint': 'http://localhost:9200/'
    }
}


def load_middleman_config(location='/etc/middleman/middleman.conf'):
    return load_config('middleman.config', location, _DEFAULTS)


class LoggingConfiguration(ConfigurationPart):
    """
    Class mapping for the Middleman logging configuration section.
    ::
        # Logging section
        [logging]
    """
    @property
    def console(self):
        """
        Returns a boolean representing whether or not Middleman should write to
        stdout for logging purposes. This value may be either True of False. If
        unset this value defaults to False.
        ::
            console = True
        """
        return self.get('console')

    @property
    def logfile(self):
        """
        Returns the log file the system will write logs to. When set, Middleman
        will enable writing to the specified file for logging purposes If unset
        this value defaults to None.
        ::
            logfile = /var/log/middleman/middleman.log
        """
        return self.get('logfile')

    @property
    def verbosity(self):
        """
        Returns the type of log messages that should be logged. This value may
        be one of the following: DEBUG, INFO, WARNING, ERROR or CRITICAL. If
        unset this value defaults to WARNING.
        ::
            verbosity = DEBUG
        """
        return self.get('verbosity')


class KeystoneConfiguration(ConfigurationPart):
    """
    Class mapping for the Middleman configuration section 'keystone'
    """
    @property
    def auth_token(self):
        """
        Returns the Keystone auth_token
        """
        return self.get('auth_token')

    @property
    def timeout(self):
        """
        Returns the Keystone HTTP timeout
        """
        return self.getint('timeout')

    @property
    def insecure(self):
        """
        Returns whether to allow keystone client to perform "insecure"
        TLS (https) requests. The server's certificate will
        not be verified against any certificate authorities.
        This option should be used with caution.
        """
        return self.get('insecure')

    @property
    def endpoint(self):
        """
        Returns the Keystone server admin URL
        """
        return self.get('endpoint')

    @property
    def url_replacement(self):
        """
        Returns which part of the URL you want replaced, in the
        case of ElasticSearch this will be: _all
        """
        return self.get('url_replacement')


class CacheConfiguration(ConfigurationPart):
    """
    Class mapping for the Middleman configuration section 'cache'
    """

    @property
    def cache_name(self):
        """
        Returns the cache name
        """
        return self.get('cache_name')

    @property
    def ttl(self):
        """
        Returns the cache time to live (in seconds)
        """
        return self.getint('ttl')


class ElasticSearchConfiguration(ConfigurationPart):
    """
    Class mapping for the Middleman configuration section 'elasticsearch'
    """
    @property
    def endpoint(self):
        """
        Returns the ElasticSearch endpoint to forward Kibana requests
        """
        return self.get('endpoint')
