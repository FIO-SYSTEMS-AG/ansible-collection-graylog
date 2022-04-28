from typing import Tuple


class StreamBase():

  def __init__(self):
    self._title = ""
    self._description = ""
    self._index_set_id = ""
    self._started = False
    self._rules = []


  @property
  def title(self) -> str:
    return self._title


  @title.setter
  def title(self, value) -> None:
    self._title = value


  @property
  def description(self) -> str:
    return self._description


  @description.setter
  def description(self, value) -> None:
    self._description = value


  @property
  def index_set_id(self) -> str:
    return self._index_set_id


  @index_set_id.setter
  def index_set_id(self, value) -> None:
    self._index_set_id = value


  @property
  def started(self) -> list:
    return self._started


  @started.setter
  def started(self, value) -> None:
    self._started = value


  @property
  def rules(self) -> list:
    return self._rules


  @rules.setter
  def rules(self, value) -> None:
    self._rules = value


  def properties_are_equal(self, stream: "StreamBase") -> bool:
    return (
      self.title == stream.title
      and self.description == stream.description
      and self.index_set_id == stream.index_set_id
    )


  def started_is_equal(self, stream: "StreamBase") -> bool:
    return self.started == stream.started


  def rules_are_equal(self, stream: "StreamBase") -> bool:
    if len(self.rules) != len(stream.rules):
      return False

    for item in self.rules:
      if (any(x for x in stream.rules if self._rule_equals(x, item) is False)):
        return False

    return True


  # returns tuple(add, delete) lists
  def get_rules_changes(self, stream: "StreamBase") -> Tuple[list, list]:
    rules = stream.rules
    add = []
    delete = []

    for item in self.rules:
      if len(rules) == 0 or any(x for x in rules if self._rule_equals(x, item)) is False:
        delete.append(item)

    for item in rules:
      if len(self.rules) == 0 or any(x for x in self.rules if self._rule_equals(x, item) is False):
        add.append(item)

    return add, delete


  def _rule_equals(self, a: dict, b: dict) -> bool:
    return (a.get('field') == b.get('field')
      and a.get('value') == b.get('value')
      and a.get('type') == b.get('type')
      and a.get('inverted') == b.get('inverted'))


  def __str__(self) -> str:
    return ("Title: %s | Description: %s | Index-Set ID: %s | Started: %s | Rules: [%s]" % (self.title, self.description, self.index_set_id, self.started, self._str_rules()))


  def _str_rules(self) -> str:
    ret = ""
    for rule in self.rules:
      ret += " { Field: %s | Value: %s | Type: %s | Inverted: %s }" % (rule.get('field'), rule.get('value'), rule.get('type'), rule.get('inverted'))
    
    ret += " "
    return ret
