import hashlib
from app.utility.base_object import BaseObject

class artVariable(BaseObject):
	
	@property
	def unique(self):
		existing.update('command', self.command)
		return hashlib.md5(b'{}{}{}'.format(self.ability_id, self.name, self.value)).hexdigest()

	@property
	def display(self):
		return self.clean(dict(id = self.unique,
								ability_id = self.ability_id,
								name = self.name,
								value = self.value,
								unique = self.unique,
								file_name = self.file_name))

	def __init__(self, ability_id, name, value, file_name):
		self.abiltiy_id = ability_id
		self.name = name
		self.value = value
		self.file_name = file_name

	def store(self, ram):
		existing = self.retrieve(ram['art_variables'], self.unique)
		if not existing:
			ram['art_variables'].append(self)
			return self.retrieve(ram['art_variables'], self.unique)
		existing.update('name', self.name)
		existing.update('value', value)
		existing.update('file_name', self.file_name)
		return existing
