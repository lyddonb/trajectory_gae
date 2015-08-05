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

from cStringIO import StringIO
from sys import exc_info
from traceback import format_tb

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

        req_body = ""

        status_code = -1
        if response:
            status_code = getattr(response, 'status_code', -1)

        send_trajectory(path_info, req_body, request.META, int(status_code),
                        response, None)

        return response


def trajectory_wsgi_middleware(app):

    def trajectory_wsgi_wrapper(environ, start_response):
        """Outer wrapper function around the WSGI protocol.

        The top-level trajectory_wsgi_middleware() function returns this
        function to the caller instead of the app class or function passed
        in.  When the caller calls this function (which may happen
        multiple times, to handle multiple requests) this function
        instantiates the app class (or calls the app function).

        The signature is determined by the WSGI protocol.
        """
        setup_trajectory(environ)
        save_status = [-1]

        path_info = environ.get('PATH_INFO', '')
        headers_list = [{}]

        req_body = request_body(environ)

        tb_catch = TBCatch()
        for err in xrange(400, 600):
            app.error_handlers[err] = tb_catch.catch_error

        def trajectory_start_response(status, headers, exc_info=None):
            if isinstance(status, basestring):
                st_sp = status.split(" ")
                if st_sp:
                    save_status.append(int(st_sp[0]))

            headers_list.append(headers)

            return start_response(status, headers, exc_info=exc_info)

        try:
            result = app(environ, trajectory_start_response)
        except:
            send_trajectory(path_info, req_body, headers_list[-1],
                            save_status[-1], result, tb_catch.traceback)
            raise

        if result is not None:
            for value in result:
                yield value

        send_trajectory(path_info, req_body, headers_list[-1], save_status[-1],
                        result, tb_catch.traceback)

        if hasattr(result, 'close'):
            result.close()

    return trajectory_wsgi_wrapper


class TBCatch(object):

    def __init__(self):
        self.traceback = []

    def catch_error(self, request, response, e):
        self.traceback = []
        e_type, e_value, tb = exc_info()
        traceback = ['Traceback (most recent call last):']
        traceback += format_tb(tb)
        name = e_type.__name__ if e_type else "Unknown"
        traceback.append('%s: %s' % (name, e_value))
        self.traceback = traceback
        raise e


def request_body(environ):
    content_length = environ.get('CONTENT_LENGTH',
                                 environ.get('HTTP_CONTENT_LENGTH'))

    if not content_length:
        # This is a special case, where the content length is basically
        # undetermined.
        body = environ['wsgi.input'].read(-1)
    else:
        body = environ['wsgi.input'].read(int(content_length))

    # reset request body for the nested app
    environ['wsgi.input'] = StringIO(body)
    return body
