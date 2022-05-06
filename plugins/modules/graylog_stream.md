# graylog_stream

## Create a stream with rules and shares
```yaml
- name: Create Graylog stream
  fio.graylog.graylog_stream:
    endpoint_url: https://graylog.company.com
    endpoint_token: foobar
    validate_certs: True
    name: My Stream
    state: present
    started: True
    index_set_id: qux
    rules:
      - field: source
        value: myapp
        type: 1
        inverted: False          
    shares:
      - type: user
        id: itsme
        capability: view   
```
