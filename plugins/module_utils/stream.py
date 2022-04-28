from plugins.module_utils import StreamBase

class Stream(StreamBase):

  def __init__(self, dto: dict):
    super().__init__()
    self._dto = dto
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
  def id(self) -> str:
    return self._id


  @id.setter
  def id(self, value) -> None:
    self._id = value
