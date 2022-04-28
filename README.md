# ansible-collection-graylog

## Usage

### Undocumented fields

#### Stream-Rules object

| Field | Description | Allowed values | Sample value |
|---|---|---|---|
| `description` | Description for the rule | any `string` | `foo` |
| `field` | Field name | any `string` | `bar` |
| `value` | Field value | any `string` | `baz` |
| `type` | Matching type | `integer`: <br/>`1` match exactly <br/>`2` match regular expression <br/>`3` greater than <br/>`4` smaller than <br/>`5` field presence <br/>`6` contain <br/>`7` always match <br/>`8` match input | 1 |
| `inverted` | Rule inversion | `boolean` | false |



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


Docs:
- ...


Testing single module with a stub: `PYTHONPATH=$(pwd) python plugins/modules/graylog_stream.py tests/stubs/graylog_streams.json`

Unit-Testing single module: `python -m pytest -r a --fulltrace --color yes tests/units/plugins/modules/test_graylog_stream.py`
