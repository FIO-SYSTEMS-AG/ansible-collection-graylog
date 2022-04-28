#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, to_text
from ansible_collections.fio.graylog.plugins.module_utils import Stream, StreamParams
#from plugins.module_utils import Stream, StreamParams
import base64
import copy
import json


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
  stream_params = StreamParams(module.params)

  streams_response = get_streams(module)

  # check
  stream = None
  for item in streams_response['streams']:
    if (item['title'] == param_name):
      stream = Stream(item)
      break

  if module.check_mode:
    result['changed'] = (
      should_create_stream(param_state, stream)
      or should_update_stream(param_state, stream, stream_params)
      or should_delete_stream(param_state, stream)
    )    
    module.exit_json(**result)

  # execute
  if (should_create_stream(param_state, stream)):
    result['changed'] = create_stream(module, stream_params)
  elif (should_update_stream(param_state, stream, stream_params)):
    result['changed'] = update_stream(module, stream, stream_params)
  elif (should_delete_stream(param_state, stream)):
    result['changed'] = delete_stream(module, stream)

  module.exit_json(**result)


def get_streams(module: AnsibleModule) -> dict:
  response, info = fetch_url(module=module, url=("%s/streams" % (get_apiBaseUrl(module))), headers=get_apiRequestHeaders(module), method='GET')

  if info['status'] != 200:
    module.fail_json(msg=info['msg'])
  
  return json.loads(to_text(response.read(), errors='surrogate_or_strict'))


def should_create_stream(state: str, stream: Stream) -> bool:
  return state == "present" and stream is None


def create_stream(module: AnsibleModule, stream_params: StreamParams) -> bool: 
  response, info = fetch_url(
    module=module, url=("%s/streams" % (get_apiBaseUrl(module))),
    headers=get_apiRequestHeaders(module),
    method='POST',
    data=module.jsonify(stream_params.map_to_dto()))

  if info['status'] != 201:
    module.fail_json(msg=info['msg'])

  response_stream = json.loads(to_text(response.read(), errors='surrogate_or_strict'))
  stream_id = response_stream['stream_id']

  if module.params['started'] == True:
    resume_stream(module, stream_id)

  return True


def resume_stream(module: AnsibleModule, stream_id: str) -> None:
  _, info = fetch_url(module=module, url=("%s/streams/%s/resume" % (get_apiBaseUrl(module), stream_id)), headers=get_apiRequestHeaders(module), method='POST')

  if info['status'] != 204:
    module.fail_json(msg=info['msg'])


def pause_stream(module: AnsibleModule, stream_id: str) -> None:
  _, info = fetch_url(module=module, url=("%s/streams/%s/pause" % (get_apiBaseUrl(module), stream_id)), headers=get_apiRequestHeaders(module), method='POST')

  if info['status'] != 204:
    module.fail_json(msg=info['msg'])


def should_update_stream(state: str, stream: Stream, stream_params: StreamParams) -> bool:
  if state == "present" and stream is None:
    return False

  return (
    stream.properties_are_equal(stream_params) is False
    or stream.started_is_equal(stream_params) is False
    or stream.rules_are_equal(stream_params) is False
  )


def update_stream(module: AnsibleModule, stream: Stream, stream_params: StreamParams) -> None:
  data = copy.deepcopy(stream.dto)
  data = stream_params.map_to_dto(data)

  _, info = fetch_url(
    module=module, url=("%s/streams/%s" % (get_apiBaseUrl(module), data['id'])),
    headers=get_apiRequestHeaders(module),
    method='PUT',
    data=module.jsonify(data))  

  if info['status'] != 200:
    module.fail_json(msg=info['msg'])

  if stream.started_is_equal(stream_params) is False:
    update_stream_started(module, stream, stream_params)

  # update rules (can not be updated via PUT streams/<id>)
  update_rules(module, stream, stream_params)

  return True


def update_stream_started(module: AnsibleModule, stream: Stream, stream_params: StreamParams) -> None:
  if stream.started:
    if stream_params.started is False:
      pause_stream(module, stream.id)
  else:
    if stream_params.started:
      resume_stream(module, stream.id)


def update_rules(module: AnsibleModule, stream: Stream, stream_params: StreamParams) -> None:
  add, delete = stream.get_rules_changes(stream_params)

  for item in delete:
    delete_rule(module, stream, item)

  for item in add:
    add_rule(module, stream, item)


def delete_rule(module: AnsibleModule, stream: Stream, rule: dict) -> None:
  _, info = fetch_url(
    module=module, url=("%s/streams/%s/rules/%s" % (get_apiBaseUrl(module), stream.id, rule['id'])),
    headers=get_apiRequestHeaders(module),
    method='DELETE')

  if info['status'] != 204:
    module.fail_json(msg=info['msg'])

  return


def add_rule(module: AnsibleModule, stream: Stream,  rule: dict) -> None:
  _, info = fetch_url(
    module=module, url=("%s/streams/%s/rules" % (get_apiBaseUrl(module), stream.id)),
    headers=get_apiRequestHeaders(module),
    method='POST',
    data=module.jsonify(rule))

  if info['status'] != 201:
    module.fail_json(msg=info['msg'])

  return


def should_delete_stream(state: str, stream: Stream) -> bool:
  return state == "absent" and stream is not None


def delete_stream(module: AnsibleModule, stream: Stream) -> bool:
  _, info = fetch_url(
    module=module, url=("%s/streams/%s" % (get_apiBaseUrl(module), stream.id)),
    headers=get_apiRequestHeaders(module),
    method='DELETE')

  if info['status'] != 204:
    module.fail_json(msg=info['msg'])

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
