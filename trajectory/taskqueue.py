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

from trajectory.config import STUBS
from trajectory.request import get_item
from trajectory.request import JOB_ID
from trajectory.request import PARENT_ID
from trajectory.request import REQUEST_ID

# Whether the trajectory taskqueue hook is installed.
installed = False


def _install_trajectory(config):

    def check(service, name, request, response):
        """Called before hitting the taskqueue stub."""
        assert service == STUBS.TASKQUEUE

        try:
            for task_request in request.add_request_list():
                for head in (JOB_ID, REQUEST_ID):
                    header = PARENT_ID if head == REQUEST_ID else head

                    header_proto = task_request.add_header()
                    header_proto.set_key(header)
                    header_proto.set_value(str(get_item(head)))
        except Exception, e:
            logging.info("Unable to apply trajectory to taskqueue request.", e)

    return check


def install_hook(config):
    from google.appengine.api.apiproxy_stub_map import apiproxy

    global installed

    if installed:
        return

    config = {}

    apiproxy.GetPreCallHooks().Append(
        'trajectory_taskqueue_hook', _install_trajectory(config),
        STUBS.TASKQUEUE)

    installed = True


def uninstall_hook():
    from google.appengine.api.apiproxy_stub_map import apiproxy

    global installed

    apiproxy.GetPreCallHooks().Clear()

    installed = False
