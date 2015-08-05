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
from webapp2 import uri_for

from .base import BaseHandler

from trajectory.providers.gae import get_all_request_parts
from trajectory.providers.gae import get_all_requests
from trajectory.providers.gae import get_all_requests_for_job
from trajectory.providers.gae import get_all_parent_requests
from trajectory.providers.gae import Node
from trajectory.providers.gae import NodeRequestBody
from trajectory.providers.gae import NodeRequestHeaders
from trajectory.providers.gae import NodeResponseBody
from trajectory.providers.gae import NodeTracebackBody


class RequestListHandler(BaseHandler):

    def get(self):
        self.render_page()

    def render_page(self):
        nodes, next_curs, more = get_all_parent_requests()

        context = {
            'requests': nodes,
        }

        self.render_template('requests/list.html', **context)


class RequestListWithParentHandler(BaseHandler):

    def get(self):
        self.render_page()

    def render_page(self):
        nodes, next_curs, more = get_all_requests()

        context = {
            'requests': nodes,
        }

        self.render_template('requests/list_with_parent.html', **context)


class RequestHandler(BaseHandler):

    def get(self, request_id):
        self.render_page(request_id)

    def render_page(self, request_id):
        node, headers, request, response, traceback = get_all_request_parts(
            request_id)

        node = node or Node()
        node.environment = node.environment or {}
        node.extra = node.extra or {}

        headers = headers or NodeRequestHeaders()
        headers.headers = headers.headers or {}

        response = response or NodeResponseBody()
        response.response = response.response or []

        request = request or NodeRequestBody()
        request.body = request.body or ""

        traceback = traceback or NodeTracebackBody()
        traceback.traceback = traceback.traceback or []

        context = {
            'request': node,
            'headers': headers,
            'request_body': request,
            'response': response,
            'traceback': traceback,
        }

        self.render_template('requests/request.html', **context)


class JobRequestListHandler(BaseHandler):

    def get(self, job_id):
        self.render_page(job_id)

    def render_page(self, job_id):
        if not job_id:
            raise Exception("Need job id.")

        nodes = get_all_requests_for_job(job_id)

        graph = []

        for node in nodes:
            if node:
                _get_graph_node(graph, node)

        context = {
            'graph': "".join(graph)
        }

        self.render_template('requests/graph.html', **context)


def _get_graph_node(graph, node, first=True, second=False):
    margin = 20
    if first:
        margin = 0
    if second:
        margin = 2

    graph.append('<div style="margin-left: ')
    graph.append(str(margin))
    graph.append('px" title="')
    graph.append(str(node.status) + '">')
    if not first:
        graph.append("&#8618;")
    graph.append('<a href="')
    graph.append(uri_for("request_handler", request_id=node.key.id()))
    graph.append('" style="margin-left: 2px">')
    graph.append(node.path)
    graph.append('</a>')
    graph.append('<span style="margin-left: 10px; font-size: 9pt">')
    graph.append(str(node.timestamp))
    graph.append('</span>')
    for n in node.children:
        _get_graph_node(graph, n, False, True if first else False)
    graph.append("</div>")
