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
import logging
import os
import re

from trajectory.providers import provider
from trajectory.config import OPTIONS

JOB_ID = OPTIONS.HEADER_PREFIX.upper() + "_JOB_ID"
PARENT_ID = OPTIONS.HEADER_PREFIX.upper() + "_PARENT_ID"
REQUEST_ID = OPTIONS.HEADER_PREFIX.upper() + "_REQUEST_ID"
HTTP_PREFIX = "HTTP_"
HTTP_JOB_ID = HTTP_PREFIX + JOB_ID
HTTP_PARENT_ID = HTTP_PREFIX + PARENT_ID
HTTP_REQUEST_ID = HTTP_PREFIX + REQUEST_ID


def get_request_id():
    request_id = os.environ.get('REQUEST_LOG_ID', 'NO_REQUEST'),

    if isinstance(request_id, (list, tuple, set)):
        return request_id[0]

    return request_id


def get_env_info():
    # TODO: If in task grab task headers.

    return {
        'app_id': _get_env_info('APPLICATION_ID'),
        'version': _get_env_info('CURRENT_VERSION_ID'),
        'module': _get_env_info('CURRENT_MODULE_ID'),
        'instance_id': _get_env_info('INSTANCE_ID')
    }


def _get_env_info(env_id):
    """Return the string with special characters removed.
    Args:
        env_id: env_id as a str"""
    return clean_string(os.environ.get(env_id, ''))


def clean_string(string):
    return re.sub('[^a-zA-Z0-9\n]', '_', string.strip()).strip('_')


def _check_item_and_set_if_empty(env, key, value):
    if not env.get(key, env.get(HTTP_PREFIX + key)):
        env[key] = value
        os.environ[key] = value


def get_item(key):
    return os.environ.get(key, os.environ.get(HTTP_PREFIX + key))


def _build_payload(path_info, status):
    return {
        "path": path_info,
        "status": status,
        "job_id": get_item(JOB_ID),
        "parent_id": get_item(PARENT_ID),
        "request_id": get_item(REQUEST_ID),
    }


def setup_trajectory(env=None):
    # TODO: Pull info from headers if exist.
    if env is None:
        env = os.environ

    request_id = get_request_id()

    _check_item_and_set_if_empty(env, JOB_ID, request_id)
    _check_item_and_set_if_empty(env, PARENT_ID, "")
    _check_item_and_set_if_empty(env, REQUEST_ID, request_id)


def send_trajectory(path_info, req_body="", headers=None, status_code=0,
                    response=None, traceback=None):
    payload = build_payload(path_info, status_code)
    payload["headers"] = _cleanup_headers(headers) if headers else {}
    payload["body"] = req_body
    payload["traceback"] = traceback or ""
    payload["response"] = response if response else []
    payload = json.dumps(payload)

    provider.send(payload)


def _cleanup_headers(headers):
    if isinstance(headers, (list, tuple, set)):
        cleaned = {}

        for header in headers:
            try:
                cleaned[header[0]] = str(header[1])
            except:
                pass

        return cleaned

    return _cleanup_dict


def _cleanup_dict(dct):
    cleaned = {}

    for k, v in dct.iteritems():
        try:
            cleaned[k] = str(v)
        except:
            pass

    return cleaned


def build_payload(path_info, status_code=0):
    # TODO: Track all task and url requests made.
    payload = _build_payload(path_info, status_code)

    payload["host"] = os.environ.get("HTTP_HOST")
    # TODO: Add flag for custom info.
    payload["extra"] = get_env_info()

    return payload
