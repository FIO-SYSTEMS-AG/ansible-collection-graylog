# ansible-collection-graylog

## Local Development

### Prepare Development Environment

```sh
$ pip install virtualenv
$ python -m venv venv
$ source venv/bin/activate 
$ pip install -r requirements.txt
```

### Test your module

`python plugins/modules/graylog_stream.py tests/stubs/graylog_streams.json`
