# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import collections
import re


class PROVIDERS:
    GAE = "gae"


class STUBS:

    URLFETCH = 'urlfetch'
    DATASTORE = 'datastore_v3'
    TASKQUEUE = 'taskqueue'


DEFAULT_CONFIG = {
    "provider": PROVIDERS.GAE,
    "header_prefix": "my_company"
}


class _TRAJECTORY(object):

    def __init__(self, config, parent=None):
        self.__config = config
        self.__compile_regexes()
        self.__parent = parent

    def __compile_regexes(self):
        """
        Compile any regexes found in the config
        """
        for key in self.__config.keys():
            if '_regexes' in key:
                if self.__config[key]:
                    regexes = self.__config[key]
                    # make a tmp list that we can mutate
                    if isinstance(regexes, basestring):
                        regexes = [regexes]
                    else:
                        regexes = list(regexes)
                    # replace regex strings with compiled regexes
                    for i in range(len(regexes)):
                        if isinstance(regexes[i], basestring):
                            regexes[i] = re.compile(regexes[i])
                    # make it immutable
                    self.__config[key] = tuple(regexes)

    def __getattr__(self, name):
        """Over written __getattr__ that handles some cases
        Args:
            name: name as a str
        """
        lname = name.lower()
        value = None

        if lname not in self.__config and self.__parent:
            return getattr(self.__parent, name)

        elif lname in self.__config:
            value = self.__config[lname]

            if isinstance(value, dict):
                value = _TRAJECTORY(value, parent=self)

            setattr(self, lname, value)

            return value

        raise AttributeError()

    def __iter__(self):
        return self.__config.iteritems()

    def __str__(self):
        return str(self.__config)


def _update(d, u):
    """Updates the mapping d with u
        Args:
            d: dict d
            u: info to use for update
    """
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = _update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]

    return d


def _build_config(config=None, import_from_settings=True):
    """ Builds the config
    Args:
        config: config as an iterable
        import_from_settings: import_from_settings as a bool
    """
    options = {}

    _update(options, DEFAULT_CONFIG)

    if config:
        _update(options, config)

    if import_from_settings:
        _import_from_settings(options)

    return _TRAJECTORY(options)


def _import_from_settings(options):
    """Updates options with Trajectory config
    Args:
        options: options as a dict
    """
    try:
        import settings
        _update(options, getattr(settings, 'TRAJECTORY_CONFIG', {}))
    except ImportError:
        pass


OPTIONS = _build_config()
