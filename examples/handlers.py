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
import os
import urllib2

import webapp2

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

MODULE = "default"


class MenuHandler(webapp2.RequestHandler):

    def get(self):
        content = [
            '<div><h3>Examples</h3>',
            '<div><a href="/examples/main">Main</a> - Pass in query string ',
            'arguments: task_depth (number of task layers, defaults to 1), ',
            'tasks_per (number of tasks to run per layer, defaults to 1), ',
            'url_fetch_per (number of url fetches to make within the task, ',
            'defaults to 1).</div>',
            '<div><a href="/examples/main?task_depth=5&tasks_per=5&',
            'url_fetch_per=5">Nested process</a> - Depth of 5, 5 tasks per ',
            'level, with 5 urlfetches.',
            '<div><a href="/examples/urlfetch">Urlfetch</a></div>',
            '<div><a href="/examples/urllib">Urllib</a></div>',
            '<div><a href="/examples/urlparent">Url Nested</a></div>',
            '<div><a href="/examples/taskqueue">Taskqueue</a> - Pass in ',
            'query string arguments: depth (number of task layers, defaults ',
            'to 0), count (number of tasks to insert at each layer, defaults ',
            'to 1)</div>',
            '<div><a href="/examples/error">Error</a></div>',
            '</div><div><h3>Requests</h3>',
            '<div><a href="/trajectory/requests/parents">Parent Requests</a>',
            '</div><div><a href="/trajectory/requests/all">All Requests</a>',
            '</div>',
            '</div>'
        ]
        self.response.write(''.join(content))


class MainHandler(webapp2.RequestHandler):

    def get(self):
        task_depth = int(self.request.GET.get("task_depth", 1))
        tasks_per = int(self.request.GET.get("tasks_per", 1))
        url_fetch_per = int(self.request.GET.get("url_fetch_per", 1))

        if task_depth:
            if task_depth > 1:
                logging.info("Do %s tasks at a depth of %s" % (
                    tasks_per, task_depth))
                for cnt in xrange(tasks_per):
                    taskqueue.add(url='/examples/taskqueue',
                                  params={'count': tasks_per, 'depth':
                                          task_depth - 1},
                                  target=MODULE)
            else:
                logging.info("Do %s tasks" % (tasks_per,))
                for cnt in xrange(tasks_per):
                    taskqueue.add(url='/examples/urlfetch', target=MODULE)

        logging.info("Do %s url fetches" % (min([url_fetch_per, 20]),))
        if url_fetch_per:
            for _ in xrange(min([url_fetch_per, 20])):
                taskqueue.add(url='/examples/urlfetch', target=MODULE)

        _write_info(self.response)


class TaskqueueHandler(webapp2.RequestHandler):

    def get(self):
        self.handle_tasks(self.request.GET)

    def post(self):
        self.handle_tasks(self.request.POST)

    def handle_tasks(self, args):
        depth = int(args.get("depth", 0))
        count = int(args.get("count", 1))

        for cnt in xrange(count):
            if depth == 0:
                logging.info("do %s fetch(s)" % (cnt,))
                taskqueue.add(url='/examples/urlfetch', target=MODULE)
            else:
                logging.info("do more %s task(s)" % (cnt,))
                taskqueue.add(url='/examples/taskqueue',
                              params={'count': 1, 'depth': depth - 1},
                              target=MODULE)

        logging.info("Depth %s, count %s" % (depth, count))

        _write_info(self.response)


class UrlfetchHandler(webapp2.RequestHandler):

    def get(self):
        url = "http://www.google.com/"
        urlfetch.fetch(url)

        _write_info(self.response)

    def post(self):
        logging.info("Do url fetches")

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
        url = "http://" + os.environ.get(
            "HTTP_HOST", "localhost") + "/examples/urlchild"
        urlfetch.fetch(url)
        _write_info(self.response)


class HeirarchyURLChildHandler(webapp2.RequestHandler):

    def get(self):
        _write_info(self.response)


class ErrorHandler(webapp2.RequestHandler):

    def get(self):
        self.render_page()

    def render_page(self):
        raise Exception("Let's see an error.")


def _write_info(response):
    from trajectory.request import get_request_id
    request_id = get_request_id()

    response.write(
        '<a href="/trajectory/requests/jobs/%s">Job Id: %s ' % (
            request_id, request_id) +
        '(Click to view the job request tree)</a>')
