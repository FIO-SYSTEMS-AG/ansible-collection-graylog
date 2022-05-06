# ansible-collection-graylog

This repository contains plugins to interact with the Graylog-API in a declarative manner.


## Usage

You can include the collection in a `requirements.yml` file and install it via `ansible-galaxy collection install -r collections/requirements.yml`:
```yaml
---
collections:
  - name: fio.graylog
    type: git
    source: https://github.com/FIO-SYSTEMS-AG/ansible-collection-graylog.git
    version: 1.0.0
...
```

### Content

Click on the name of the module to jump to an example.

#### Modules
Name | Supports Check-Mode | Description
--- | --- | ---
[fio.graylog.graylog_stream](https://github.com/FIO-SYSTEMS-AG/ansible-collection-graylog/blob/main/plugins/modules/graylog_stream.md) | yes | CRUD stream with rules and shares

For more non-obvious fields, visit [wiki/type-definitions](https://github.com/FIO-SYSTEMS-AG/ansible-collection-graylog/wiki/type-definitions).


## Local development


### Clone project

- clone project into a path which is in your extraPaths (vscode) or PYTHONPATH variable
- directory structure should be `./ansible_collections/fio/graylog`


### Prepare development environment

```sh
$ pip install virtualenv
$ python -m venv venv
$ source venv/bin/activate 
$ pip install -r requirements.txt
```


### Test your module


Testing single module with a stub: `python plugins/modules/graylog_stream.py tests/stubs/graylog_streams.json`

Unit-Testing single module: `python -m pytest -r a --fulltrace --color yes tests/units/plugins/module_utils/test_stream.py`
