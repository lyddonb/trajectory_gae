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
import unittest

from google.appengine.ext import testbed
from google.appengine.datastore import datastore_stub_util

HRD_POLICY_PROBABILITY = 1


class HRDataStoreAndMemcacheTestCase(unittest.TestCase):

    def setUp(self):
        super(HRDataStoreAndMemcacheTestCase, self).setUp()

        # Backup environ so it can be restored
        self.orig_environ = dict(os.environ)

        os.environ['TZ'] = "UTC"

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.setup_env(app_id="wf")

        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
            probability=HRD_POLICY_PROBABILITY)
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)

        self.testbed.init_memcache_stub()

    def tearDown(self):
        super(HRDataStoreAndMemcacheTestCase, self).tearDown()

        self.testbed.deactivate()

        # Restore os.environ
        os.environ = self.orig_environ
