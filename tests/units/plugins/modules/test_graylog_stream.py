#!/usr/bin/python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from tests.units.utils import ModuleTestCase
from plugins.modules.graylog_stream import should_update_stream_rules


class TestCheckMode():

  def test_sets_change_when_rule_value_changes(self):
    param_rules = [{
      'field': 'foo',
      'value': 'bar'
    }]

    current_rules = [{
      'field': 'foo',
      'value': 'baz'
    }]

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True

  
  def test_sets_change_when_rule_description_changes(self):
    param_rules = [{
      'field': 'foo',
      'value': 'bar',
      'description': 'baz'
    }]

    current_rules = [{
      'field': 'foo',
      'value': 'bar',
      'description': 'qux'
    }]

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True

  
  def test_sets_change_when_rule_description_changes(self):
    param_rules = [{
      'field': 'foo',
      'value': 'bar',
      'description': 'baz'
    }]

    current_rules = [{
      'field': 'foo',
      'value': 'bar',
      'description': 'qux'
    }]

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True


  def test_sets_change_when_new_rule(self):
    param_rules = [{
      'field': 'foo',
      'value': 'bar'
    }]

    current_rules = []

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True


  def test_sets_change_when_remove_rule(self):
    param_rules = []

    current_rules = [{
      'field': 'foo',
      'value': 'bar'
    }]

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True


  def test_sets_change_when_remove_and_add_rule(self):
    param_rules = [
      {
        'field': 'foo',
        'value': '1'
      }
    ]

    current_rules = [
      {
        'field': 'bar',
        'value': '1'
      }
    ]

    change = should_update_stream_rules(param_rules, current_rules)

    assert change is True
