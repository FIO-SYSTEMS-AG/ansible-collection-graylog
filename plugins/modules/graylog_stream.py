#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, to_text
import base64
import json
from typing import NoReturn

__metaclass__ = type

DOCUMENTATION = r'''
---
module: graylog_stream

short_description: Module to create/update/delete Graylog streams

version_added: "1.0.0"

description: 
  - Module ensures that the given streams exists on the target Graylog instance.

options:
  endpoint_url:
    description: Graylog endpoint URL.
    required: true
    type: str
  endpoint_token:
    description: Token which will be used for the API requests.
    required: true
    type: str
  validate_certs:
    description: Validate certs for endpoint_url.
    required: false
    type: bool
  state:
    description: The desired state.
    required: true
    default: present
    choices: [ "present", "absent" ]
    type: str
  name:
    description: The name of the stream.
    required: true
    type: str

notes:
  - Does not require any additional dependencies.


author:
  - FIO SYSTEMS AG (@FIO-SYSTEMS-AG)
'''

EXAMPLES = r'''
- name: Test with a message
  fio.graylog.graylog_stream:
    endpoint_url: http://localhost:9000
    endpoint_token: foobar:token
    validate_certs: false
    state: present
    name: myapp
'''

RETURN = r'''
#
'''


def run_module():
  module_args = dict(
    endpoint_url=dict(type='str', required=True),
    endpoint_token=dict(type='str', required=True),
    validate_certs=dict(type='bool', required=False),
    state=dict(type='str', required=True),
    name=dict(type='str', required=True),
  )

  result = dict(
    changed=False
  )

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True
  )

  param_state = module.params["state"]
  param_name = module.params["name"]

  streams_response = get_streams(module)

  # check
  existing_stream = None
  for item in streams_response['streams']:
    if (item['title'] == param_name):
      existing_stream = item  
  
  if module.check_mode:
    result['changed'] = should_create_stream(param_state, existing_stream) or should_update_stream(param_state, existing_stream) or should_delete_stream(param_state, existing_stream)
    module.exit_json(**result)

  # execute
  if (should_create_stream(param_state, existing_stream)):
    result['changed'] = create_stream(module)
  elif (should_update_stream(param_state, existing_stream)):
    result['changed'] = update_stream(module, existing_stream)
  elif (should_delete_stream(param_state, existing_stream)):
    result['changed'] = delete_stream(module, existing_stream)

  module.exit_json(**result)


def get_streams(module: AnsibleModule) -> dict:
  response, info = fetch_url(module=module, url=(get_apiBaseUrl(module) + "/api/streams"), headers=get_apiRequestHeaders(module), method='GET')

  if info['status'] != 200:
    module.fail_json(msg=info['msg'])
  
  return json.loads(to_text(response.read(), errors='surrogate_or_strict'))


def should_create_stream(state: str, existing_stream: dict) -> bool:
  return state == "present" and existing_stream is None


def create_stream(module: AnsibleModule) -> bool:
  print('create stream')
  return True


def should_update_stream(state: str, existing_stream: dict) -> bool:
  return state == "present" and existing_stream is not None


def update_stream(module: AnsibleModule, existing_stream: dict) -> bool:
  print('update stream')
  return True


def should_delete_stream(state: str, existing_stream: dict) -> bool:
  return state == "absent" and existing_stream is not None


def delete_stream(module: AnsibleModule, existing_stream: dict) -> bool:
  print('delete stream')
  return True


def get_apiBaseUrl(module: AnsibleModule) -> str:
  return module.params["endpoint_url"]


def get_apiRequestHeaders(module: AnsibleModule) -> dict:
  token = module.params["endpoint_token"] + ':token' 
  token_bytes = token.encode('utf-8')
  encoded_token = base64.b64encode(token_bytes).decode('utf-8')
  
  return { 
    'Authorization': 'Basic ' + encoded_token,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }


def main():
  run_module()


if __name__ == '__main__':
  main()
