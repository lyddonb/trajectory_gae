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

from trajectory.request import send_trajectory
from trajectory.request import setup_trajectory


class TrajectoryDjangoMiddleware(object):
    """Django Middleware to install trajectory instrumentation.

    To start recording your app's RPC statistics, add

        'trajectory.middleware.TrajectoryDjangoMiddleware',

    to the MIDDLEWARE_CLASSES entry in your Django settings.py file.
    It's best to insert it in front of any other middleware classes,
    since some other middleware may make RPC calls and those won't be
    recorded if that middleware is invoked before this middleware.

    See http://docs.djangoproject.com/en/dev/topics/http/middleware/.
    """

    def process_request(self, request):
        """Called by Django before deciding which view to execute.

        Args:
            request: request to be processed
        """
        # Inject our correlation id in the headers if not already there.
        logging.info(30 * "^")
        logging.info(30 * "^")
        logging.info(30 * "^")
        logging.info(os.environ)
        logging.info(30 * "^")
        logging.info(30 * "^")
        logging.info(30 * "^")
        setup_trajectory()

    def process_response(self, request, response):
        """Called by Django just before returning a response.

        Args:
            request: request to be processed
            response: response to the issued request
        """

        # send our data off to trajectory.

        path_info = ''
        if request and request.META and 'PATH_INFO' in request.META:
            path_info = request.META['PATH_INFO']

        status_code = -1
        if response:
            status_code = getattr(response, 'status_code', -1)

        send_trajectory(path_info, int(status_code))

        return response


def trajectory_wsgi_middleware(app):

    def trajectory_wsgi_wrapper(environ, start_response):
        """Outer wrapper function around the WSGI protocol.

        The top-level trajectory_wsgi_middleware() function returns this
        function to the caller instead of the app class or function passed
        in.  When the caller calls this function (which may happen
        multiple times, to handle multiple requests) this function
        instantiates the app class (or calls the app function), sandwiched
        between calls to start_recording() and end_recording() which
        manipulate the recording state.

        The signature is determined by the WSGI protocol.
        """
        logging.info(30 * "*")
        logging.info("Start Middleware")
        logging.info(environ)
        logging.info(os.environ)
        logging.info(start_response)
        logging.info(30 * "*")
        setup_trajectory(environ)
        save_status = [-1]

        path_info = environ.get('PATH_INFO', '')

        def trajectory_start_response(status, headers, exc_info=None):
            if isinstance(status, basestring):
                st_sp = status.split(" ")
                if st_sp:
                    save_status.append(int(st_sp[0]))

            return start_response(status, headers, exc_info=exc_info)

        try:
            result = app(environ, trajectory_start_response)
        except Exception:
            send_trajectory(path_info, save_status[-1])
            raise

        if result is not None:
            for value in result:
                yield value

        send_trajectory(path_info, save_status[-1])

        if hasattr(result, 'close'):
            result.close()

    return trajectory_wsgi_wrapper
