#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from typing import NoReturn
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, to_text
import base64
import json

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
  index_set_id:
    description: The Index-Set Id.
    required: true
    type: str
  rules:
    description: Rules for the stream.
    required: false
    type: list
    default: []
  started:
    description: Flag indicating if the stream should be in started state.
    required: false
    type: bool
    default: false

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
    validate_certs: False
    state: present
    name: myapp
    started: True
    index_set_id: abcde
    rules:
      - description: myrule
        field: foo
        value: bar
        type: 1
        inverted: False
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
    index_set_id=dict(type='str', required=True),
    rules=dict(type='list', required=False),
    started=dict(type='bool', required=False, default=False),
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
      break
  
  # test
  module.check_mode = True

  if module.check_mode:
    result['changed'] = should_create_stream(param_state, existing_stream) or should_update_stream(module, param_state, existing_stream) or should_delete_stream(param_state, existing_stream)
    module.exit_json(**result)

  # execute
  if (should_create_stream(param_state, existing_stream)):
    result['changed'] = create_stream(module)
  elif (should_update_stream(module, param_state, existing_stream)):
    result['changed'] = update_stream(module, existing_stream)
  elif (should_delete_stream(param_state, existing_stream)):
    result['changed'] = delete_stream(module, existing_stream)

  module.exit_json(**result)


def get_streams(module: AnsibleModule) -> dict:
  response, info = fetch_url(module=module, url=("%s/streams" % (get_apiBaseUrl(module))), headers=get_apiRequestHeaders(module), method='GET')

  if info['status'] != 200:
    module.fail_json(msg=info['msg'])
  
  return json.loads(to_text(response.read(), errors='surrogate_or_strict'))


def should_create_stream(state: str, existing_stream: dict) -> bool:
  return state == "present" and existing_stream is None


def create_stream(module: AnsibleModule) -> bool:
  data = {
    'title': module.params['name'],
    'description': module.params['name'],
    'remove_matches_from_default_stream': True,
    'index_set_id': module.params['index_set_id'],
    'rules': module.params['rules'],
  }

  response, info = fetch_url(module=module, url=("%s/streams" % (get_apiBaseUrl(module))), headers=get_apiRequestHeaders(module), method='POST', data=module.jsonify(data))

  if info['status'] != 201:
    module.fail_json(msg=info['msg'])

  response_stream = json.loads(to_text(response.read(), errors='surrogate_or_strict'))
  stream_id = response_stream['stream_id']

  if module.params['started'] == True:
    resume_stream(module, stream_id)

  return True


def resume_stream(module: AnsibleModule, stream_id: str) -> NoReturn:
  _, info = fetch_url(module=module, url=("%s/streams/%s/resume" % (get_apiBaseUrl(module), stream_id)), headers=get_apiRequestHeaders(module), method='POST')

  if info['status'] != 204:
    module.fail_json(msg=info['msg'])


def should_update_stream(module: AnsibleModule, state: str, existing_stream: dict) -> bool:
  if state == "present" and existing_stream is None:
    return False

  return (
    module.params['name'] != existing_stream['title'] 
    or module.params['name'] != existing_stream['description']
    or module.params['index_set_id'] != existing_stream['index_set_id']
    or should_update_stream_rules(module.params['rules'], existing_stream['rules'])
  )


def should_update_stream_rules(param_rules, current_rules) -> bool:
  if len(param_rules) != len(current_rules):
    return True
  
  for item in current_rules:
    return (next((x for x in param_rules
      if x['field'] == item['field']
        and x['value'] == item['value']
        and x['description'] == item['description']
        and x['type'] == item['type']
        and x['inverted'] == item['inverted']), None)
      is None)

  return False


def update_stream(module: AnsibleModule, existing_stream: dict) -> bool:
  print('update stream')
  return True


def should_delete_stream(state: str, existing_stream: dict) -> bool:
  return state == "absent" and existing_stream is not None


def delete_stream(module: AnsibleModule, existing_stream: dict) -> bool:
  print('delete stream')
  return True


def get_apiBaseUrl(module: AnsibleModule) -> str:
  return module.params["endpoint_url"] + '/api'


def get_apiRequestHeaders(module: AnsibleModule) -> dict:
  token = module.params["endpoint_token"] + ':token' 
  token_bytes = token.encode('utf-8')
  encoded_token = base64.b64encode(token_bytes).decode('utf-8')
  
  return { 
    'Authorization': 'Basic ' + encoded_token,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-By': 'ansible'
  }


def main():
  run_module()


if __name__ == '__main__':
  main()
