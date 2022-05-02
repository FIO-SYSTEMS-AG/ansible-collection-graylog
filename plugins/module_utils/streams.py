from __future__ import annotations
from typing import Tuple
import re


class StreamBase():

  def __init__(self):
    self._title = ""
    self._description = ""
    self._index_set_id = ""
    self._started = False
    self._rules = []
    self._shares = []


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


  @property
  def shares(self) -> "list[StreamShare]":
    return self._shares


  @shares.setter
  def shares(self, value) -> None:
    self._shares = value


  def equals(self, stream: "StreamBase") -> bool:    
    return (
      self.properties_are_equal(stream)
      and self.started_is_equal(stream)
      and self.rules_are_equal(stream)
      and self.shares_are_equal(stream)
    )


  def properties_are_equal(self, stream: "StreamBase") -> bool:
    return (
      self.title == stream.title
      and self.description == stream.description
      and self.index_set_id == stream.index_set_id
    )


  def started_is_equal(self, stream: "StreamBase") -> bool:
    return self.started == stream.started


  def rules_are_equal(self, stream: "StreamBase") -> bool:
    add, delete = self.get_rules_changes(stream)
    return len(add) == 0 and len(delete) == 0


  def shares_are_equal(self, stream: "StreamBase") -> bool:
    add, delete = self.get_shares_changes(stream)
    return len(add) == 0 and len(delete) == 0


  # returns tuple(add, delete) lists
  def get_rules_changes(self, stream_params: "StreamBase") -> "Tuple[list, list]":   
    add_list = []
    delete_list = []

    for item in self.rules:
      if len(stream_params.rules) == 0 or any(x for x in stream_params.rules if self._rule_equals(x, item)) is False:
        delete_items = [x for x in self.rules if self._rule_equals(x, item)]
        for delete_item in delete_items:
          if (any(x for x in delete_list if x == delete_item) is False):
            delete_list.append(delete_item)

    for item in stream_params.rules:
      existing_items = [x for x in self.rules if self._rule_equals(x, item)]
      if (len(existing_items) == 0):
        add_list.append(item)
      elif (len(existing_items) > 1):
        for existing_item in existing_items[1:]:
          delete_list.append(existing_item)

    return add_list, delete_list


  # returns tuple(add, delete) lists
  def get_shares_changes(self, stream_params: "StreamBase") -> "Tuple[list[StreamShare], list[StreamShare]]":   
    add_list = []
    delete_list = []

    for item in self.shares:
      if len(stream_params.shares) == 0 or any(x for x in stream_params.shares if self._share_equals(x, item)) is False:
        delete_items = [x for x in self.shares if self._share_equals(x, item)]
        for delete_item in delete_items:
          if (any(x for x in delete_list if x == delete_item) is False):
            delete_list.append(delete_item)

    for item in stream_params.shares:
      existing_items = [x for x in self.shares if self._share_equals(x, item)]
      if (len(existing_items) == 0):
        add_list.append(item)
      elif (len(existing_items) > 1):
        for existing_item in existing_items[1:]:
          delete_list.append(existing_item)

    return add_list, delete_list


  def _rule_equals(self, a: dict, b: dict) -> bool:
    return (a.get('field') == b.get('field')
      and a.get('value') == b.get('value')
      and a.get('type') == b.get('type')
      and a.get('inverted') == b.get('inverted'))


  def _share_equals(self, a: StreamShare, b: StreamShare) -> bool:   
    return (a.type == b.type
      and a.id == b.id
      and a.capability == b.capability)


  def __str__(self) -> str:
    return ("Title: %s | Description: %s | Index-Set ID: %s | Started: %s | Rules: [%s]" % (self.title, self.description, self.index_set_id, self.started, self._str_rules()))


  def _str_rules(self) -> str:
    ret = ""
    for rule in self.rules:
      ret += " { Field: %s | Value: %s | Type: %s | Inverted: %s }" % (rule.get('field'), rule.get('value'), rule.get('type'), rule.get('inverted'))
    
    ret += " "
    return ret



class StreamParams(StreamBase):
  
  def __init__(self, params: dict):
    super().__init__()
    self.title = params.get('name', '')
    self.description = params.get('name', '')
    self.index_set_id = params.get('index_set_id', '')
    self.rules = params.get('rules', [])
    self.shares = [StreamShare().load_from_params(x) for x in params.get('shares', [])]


  def map_to_dto(self, destination: dict = None) -> dict:
    if destination is None:
      destination = {}
  
    destination['title'] = self.title
    destination['description'] = self.description
    destination['remove_matches_from_default_stream'] = True
    destination['index_set_id'] = self.index_set_id
    destination['rules'] = self.rules

    return destination



class Stream(StreamBase):

  def __init__(self, dto: dict):
    super().__init__()
    self._dto = dto
    self._shares_dto = None
    self._id = dto.get('id', '')
    self.title = dto.get('title', '')
    self.description = dto.get('description', '')
    self.index_set_id = dto.get('index_set_id', '')
    self.rules = dto.get('rules', [])


  @property
  def dto(self) -> dict:
    return self._dto


  @dto.setter
  def dto(self, value) -> None:
    self._dto = value


  @property
  def shares_dto(self) -> dict:
    return self._shares_dto


  @shares_dto.setter
  def shares_dto(self, value) -> None:
    self._shares_dto = value


  @property
  def id(self) -> str:
    return self._id


  @id.setter
  def id(self, value) -> None:
    self._id = value



class StreamShare():
  
  def __init__(self, type: str = "", id: str = "", capability: str = ""):
    self._type = type
    self._id = id
    self._capability = capability


  @property
  def type(self) -> str:
    return self._type


  @type.setter
  def type(self, value) -> None:
    self._type = value


  @property
  def id(self) -> str:
    return self._id


  @id.setter
  def id(self, value) -> None:
    self._id = value


  @property
  def capability(self) -> str:
    return self._capability


  @capability.setter
  def capability(self, value) -> None:
    self._capability = value


  def load_from_dto(self, dto: dict) -> "StreamShare":
    grantee_match = re.search('grn::::(.+):(.+)', dto.get('grantee', ''))
    if grantee_match is None:
      raise ValueError('could not parse grantee')
    
    self.type = grantee_match.group(1)
    self.id = grantee_match.group(2)
    self.capability = dto.get('capability')
    return self


  def load_from_params(self, params: dict) -> "StreamShare":
    self.__init__(params.get('type'), params.get('id'), params.get('capability'))
    return self


  def get_grn_key(self) -> str:
    return 'grn::::%s:%s' % (self.type, self.id)
