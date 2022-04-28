from plugins.module_utils import StreamBase


class StreamParams(StreamBase):
  
  def __init__(self, params: dict):
    super().__init__()
    self.title = params.get('name', '')
    self.description = params.get('name', '')
    self.index_set_id = params.get('index_set_id', '')
    self.rules = params.get('rules', [])


  def map_to_dto(self, destination: dict = None) -> dict:
    if destination is None:
      destination = {}
  
    destination['title'] = self.title
    destination['description'] = self.description
    destination['remove_matches_from_default_stream'] = True
    destination['index_set_id'] = self.index_set_id
    destination['rules'] = self.rules

    return destination
