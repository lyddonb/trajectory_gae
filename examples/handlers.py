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
import logging
import urllib2

import webapp2

from google.appengine.api import urlfetch


class TaskqueuHandler(webapp2.RequestHandler):

    def get(self):
        from google.appengine.api import taskqueue
        taskqueue.add(url='/examples/urlfetch', params={})

        _write_info(self.response)


class UrlfetchHandler(webapp2.RequestHandler):

    def get(self):
        url = "http://www.google.com/"
        urlfetch.fetch(url)

        _write_info(self.response)

    def post(self):
        url = "http://www.google.com/"
        urlfetch.fetch(url)

        _write_info(self.response)


class UrllibHandler(webapp2.RequestHandler):

    def get(self):
        url = "http://www.google.com/"
        try:
            urllib2.urlopen(url)
        except urllib2.URLError:
            pass

        _write_info(self.response)


# TODO: Add example that calls other example.

class HeirarchyURLParentHandler(webapp2.RequestHandler):

    def get(self):
        url = "http://localhost:8080/examples/urlchild"
        result = urlfetch.fetch(url)
        logging.info(result.status_code)
        logging.info(result.content)
        _write_info(self.response)


class HeirarchyURLChildHandler(webapp2.RequestHandler):

    def get(self):
        _write_info(self.response)


def _write_info(response):
    from trajectory.request import get_request_id
    request_id = get_request_id()

    response.write(request_id)
