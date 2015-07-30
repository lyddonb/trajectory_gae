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

import os

import webapp2

from . import requests

TRAJECTORY_PREFIX = '/trajectory'

config = {
    'webapp2_extras.jinja2': {
        'template_path': os.path.join(os.path.dirname(__file__), 'templates')
    }
}


def get_app(prefix='', **options):
    url_prefix = "%s%s" % (prefix, TRAJECTORY_PREFIX)

    config['trajectory.options'] = options

    return webapp2.WSGIApplication([
        webapp2.Route("%s/%s" % (url_prefix, "requests/parents"),
                      handler=requests.RequestListHandler,
                      name="parent_request_list_handler"),
        webapp2.Route("%s/%s" % (url_prefix, "requests/all"),
                      handler=requests.RequestListWithParentHandler,
                      name="all_request_list_handler"),
        webapp2.Route("%s/%s" % (url_prefix, "requests/jobs/<job_id>"),
                      handler=requests.JobRequestListHandler,
                      name="job_request_list_handler"),
        webapp2.Route("%s/%s" % (url_prefix, "requests/<request_id>"),
                      handler=requests.RequestHandler,
                      name="request_handler"),
    ], config=config)
