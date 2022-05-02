#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from ansible_collections.fio.graylog.plugins.module_utils.streams import StreamBase, StreamShare


class TestComparison():
  
  @pytest.mark.parametrize("a,b,expected", [ 
    ("foo", "foo", True),
    ("foo", "bar", False)
  ])
  def test_properties_are_equal_compares_title(self, a: str, b: str, expected: bool):
    stream_a = StreamBase()
    stream_a.title = a

    stream_b = StreamBase()
    stream_b.title = b

    assert stream_a.properties_are_equal(stream_b) is expected


  @pytest.mark.parametrize("a,b,expected", [ 
    ("foo", "foo", True),
    ("foo", "bar", False)
  ])
  def test_properties_are_equal_compares_description(self, a: str, b: str, expected: bool):
    stream_a = StreamBase()
    stream_a.description = a

    stream_b = StreamBase()
    stream_b.description = b

    assert stream_a.properties_are_equal(stream_b) is expected


  @pytest.mark.parametrize("a,b,expected", [ 
    ("foo", "foo", True),
    ("foo", "bar", False)
  ])
  def test_properties_are_equal_compares_index_set_id(self, a: str, b: str, expected: bool):
    stream_a = StreamBase()
    stream_a.index_set_id = a

    stream_b = StreamBase()
    stream_b.index_set_id = b

    assert stream_a.properties_are_equal(stream_b) is expected


  @pytest.mark.parametrize("a,b,expected", [ 
    ([], [ { "field": "foo" } ], False),
    ([ { "field": "foo" } ], [], False),
    ([ { "field": "foo" } ], [ { "field": "foo" } ], True),
    ([ { "field": "foo" } ], [ { "field": "bar" } ], False)
  ])
  def test_rules_are_equal(self, a: list, b: list, expected: bool):
    stream_a = StreamBase()
    stream_a.rules = a

    stream_b = StreamBase()
    stream_b.rules = b

    assert stream_a.rules_are_equal(stream_b) is expected



class TestChangeDetector():

  def test_get_rules_changes_returns_correct_lists(self):

    stream = StreamBase()
    stream.rules = [
      {
        'field': 'foo',
        'value': '1',
        'type': 1,
      },
      {
        'field': 'bar',
        'value': '1',        
        'type': 1,
      }
    ]

    stream_params = StreamBase()
    stream_params.rules = [
      {
        'field': 'bar',
        'value': '2',          
        'type': 1,
      },
      {
        'field': 'baz',
        'value': '1',        
        'type': 1,
      }
    ]

    add, delete = stream.get_rules_changes(stream_params)

    assert 2 == len(delete)
    assert any(x for x in delete if x['field'] == 'foo')
    assert any(x for x in delete if x['field'] == 'bar')
    assert 2 == len(add)
    assert any(x for x in add if x['field'] == 'baz')
    assert any(x for x in add if x['field'] == 'baz')


  def test_get_rules_changes_returns_correct_lists_a(self):

    stream = StreamBase()
    stream.rules = []

    stream_params = StreamBase()
    stream_params.rules = [
      {
        'field': 'foo',
        'value': 'bar',          
        'type': 1,
      }
    ]

    add, delete = stream.get_rules_changes(stream_params)

    assert 0 == len(delete)
    assert 1 == len(add)


  def test_get_rules_changes_removes_duplicates(self):
    stream = StreamBase()
    stream.rules = [
      {
        'id': 'abc0',
        'field': 'foo',
        'value': '1',          
        'type': 1,
      },
      {
        'id': 'abc1',
        'field': 'bar',
        'value': 'baz',          
        'type': 1,
      },
      {
        'id': 'abc2',
        'field': 'bar',
        'value': 'baz',
        'type': 1,
      }
    ]

    stream_params = StreamBase()
    stream_params.rules = [
      {
        'field': 'foo',
        'value': '1',
        'type': 1,
      },
      {
        'id': 'abc1',
        'field': 'bar',
        'value': 'baz',          
        'type': 1,
      },
    ]

    add, delete = stream.get_rules_changes(stream_params)

    assert sum(1 for x in delete if x['field'] == 'bar') == 1
    assert 0 == len(add)


  def test_get_share_changes_returns_correct_lists(self):

    stream = StreamBase()
    stream.shares = [ StreamShare("user", "foo", "view"), StreamShare("user", "bar", "view") ]

    stream_params = StreamBase()
    stream_params.shares = [ StreamShare("user", "baz", "view"), StreamShare("user", "bar", "manage") ]

    add, delete = stream.get_shares_changes(stream_params)

    assert 2 == len(delete)
    assert any(x for x in delete if x.id == 'foo')
    assert any(x for x in delete if x.id == 'bar')
    assert 2 == len(add)
    assert any(x for x in add if x.id == 'baz' and x.capability == 'view')
    assert any(x for x in add if x.id == 'bar' and x.capability == 'manage')



class TestShareParsing():

  def test_can_parse_user_from_dto(self):    
    dto = {
      "grantee":"grn::::user:626a6d4ab61ee103107f1c60",
      "capability":"view"
    }

    stream_share = StreamShare().load_from_dto(dto)

    assert "user" == stream_share.type
    assert "626a6d4ab61ee103107f1c60" == stream_share.id
    assert "view" == stream_share.capability
