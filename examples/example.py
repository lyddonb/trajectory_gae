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

import webapp2

from handlers import ErrorHandler
from handlers import HeirarchyURLChildHandler
from handlers import HeirarchyURLParentHandler
from handlers import MainHandler
from handlers import MenuHandler
from handlers import TaskqueueHandler
from handlers import UrlfetchHandler
from handlers import UrllibHandler

config = {}

app = webapp2.WSGIApplication([
    ('/examples/', MenuHandler),
    ('/examples/main', MainHandler),
    ('/examples/urlfetch', UrlfetchHandler),
    ('/examples/urllib', UrllibHandler),
    ('/examples/urlparent', HeirarchyURLParentHandler),
    ('/examples/urlchild', HeirarchyURLChildHandler),
    ('/examples/taskqueue', TaskqueueHandler),
    ('/examples/error', ErrorHandler),
], config=config)

# TODO: Add settings flag to enable trajectory.
from trajectory import install
app = install(app, with_middleware=True)
