import hashlib
from app.utility.base_object import BaseObject

class artAbility(BaseObject):
	
	@property
	def unique(self):
		return hashlib.md5(b'{}{}{}'.format(self.technique, self.platform, self.command))

	@property
	def display(self):
		return self.clean(dict(id = self.unique, ability_id = self.ability_id, tactic = self.tactic, technique_id = self.technique_id,
								technique_name = self.technique_name, name = self.name, description = self.description,
								platform = self.platform, executor = self.executor, command = self.command))

	def __init__(self, ability_id, tactic, technique_id, technique_name, name, description, tactic, platform, executor, command):
		self.abiltiy_id = ability_id
		self.tactic = tactic
		self.technique_id = technique_id
		self.technique_name = technique_name
		self.name = name
		self.description = description
		self.platform = platform
		self.executor = executor
		self.command = command

	def store(self, ram):
		existing = self.retrieve(ram['artAbility'], self.unique)
		if not existing:
			ram['artAbility'].append(self)
			return self.retrieve(ram['artAbility'], self.unique)
		return existing
