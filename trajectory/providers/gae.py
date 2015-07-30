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
import json

from collections import defaultdict

from google.appengine.ext import ndb


class Node(ndb.Model):
    """A trajectory node.

    Key: request_id `Class` :string:
    """
    def __init__(self, *args, **kwargs):
        self.children = []

        super(Node, self).__init__(*args, **kwargs)

    job_id = ndb.StringProperty(name="jid", indexed=True, required=True)
    parent_id = ndb.StringProperty(name="pid", indexed=True)
    path = ndb.StringProperty(indexed=True)
    host = ndb.StringProperty(indexed=True)
    status = ndb.IntegerProperty(indexed=True)
    extra = ndb.JsonProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


def send_request(payload):
    payload = json.loads(payload)

    add_node(payload["request_id"],
             payload["job_id"],
             payload["parent_id"],
             payload["path"],
             payload["host"],
             payload["status"],
             payload["extra"])


def get_request(request_id):
    return Node.get_by_id(request_id)


def add_node_async(request_id, job_id, parent_id, path, host, status, extra):
    return Node(id=request_id,
                job_id=job_id,
                parent_id=parent_id,
                path=path,
                host=host,
                status=status,
                extra=extra).put_async()


def add_node(request_id, job_id, parent_id, path, host, status, extra):
    return add_node_async(request_id, job_id, parent_id, path, host, status,
                          extra).get_result()


def get_all_requests(limit=100, curs=None):
    return Node.query().order(-Node.timestamp).fetch_page(
        limit, start_cursor=curs)


def get_all_requests_for_job(job_id, limit=100, curs=None):
    node_map = {}
    nodes_not_yet_in_map = defaultdict(list)

    parents = []

    for node in Node.query(Node.job_id == job_id).order(-Node.timestamp):
        if node.key.id() not in node_map:
            node_map[node.key.id()] = node

            if node.key.id() in nodes_not_yet_in_map:
                node.children.extend(nodes_not_yet_in_map.pop(node.key.id()))

        if not node.parent_id:
            parents.append(node)
            continue

        if node.parent_id not in node_map:
            nodes_not_yet_in_map[node.parent_id].append(node)
        else:
            node_map[node.parent_id].children.append(node)

    return parents


def get_all_parent_requests(limit=100, curs=None):
    return Node.query(Node.parent_id == "").order(-Node.timestamp).fetch_page(
        limit, start_cursor=curs)
