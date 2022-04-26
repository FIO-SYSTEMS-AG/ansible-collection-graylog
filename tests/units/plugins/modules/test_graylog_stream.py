#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from plugins.modules.graylog_stream import *


class TestCheckMode():

  def test_sets_change_when_rule_value_changes(self):  
    current_rules = [{
      'field': 'foo',
      'value': 'baz',
      'type': 1,
    }]

    param_rules = [{
      'field': 'foo',
      'value': 'bar',
      'type': 1,
    }]

    change = should_update_stream_rules(current_rules, param_rules)

    assert change is True


  def test_sets_change_when_new_rule(self):
    current_rules = []

    param_rules = [{
      'field': 'foo',
      'value': 'bar',
      'type': 1,
    }]

    change = should_update_stream_rules(current_rules, param_rules)

    assert change is True


  def test_sets_change_when_remove_rule(self):   
    current_rules = [{
      'field': 'foo',
      'value': 'bar',
      'type': 1,
    }]

    param_rules = []

    change = should_update_stream_rules(current_rules, param_rules)

    assert change is True


  def test_sets_change_when_remove_and_add_rule(self):
    current_rules = [
      {
        'field': 'bar',
        'value': '1',
        'type': 1,
      }
    ]

    param_rules = [
      {
        'field': 'foo',
        'value': '1',
        'type': 1,
      }
    ]

    change = should_update_stream_rules(current_rules, param_rules)

    assert change is True


  def test_get_rules_changes_returns_correct_lists(self):

    current_rules = [
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

    param_rules = [
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

    add, delete = get_rules_changes(current_rules, param_rules)

    assert 2 == len(delete)
    assert any(x for x in delete if x['field'] == 'foo')
    assert any(x for x in delete if x['field'] == 'bar')
    assert 2 == len(add)
    assert any(x for x in add if x['field'] == 'baz')
    assert any(x for x in add if x['field'] == 'baz')


  def test_get_rules_changes_returns_correct_lists_a(self):

    current_rules = []

    param_rules = [
      {
        'field': 'foo',
        'value': 'bar',          
        'type': 1,
      }
    ]

    add, delete = get_rules_changes(current_rules, param_rules)

    assert 0 == len(delete)
    assert 1 == len(add)
