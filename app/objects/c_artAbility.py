import hashlib
from app.utility.base_object import BaseObject

class artAbility(BaseObject):
	
	@property
	def unique(self):
		return hashlib.md5(b'{}{}{}'.format(self.technique, self.platform, self.command)).hexdigest()

	@property
	def display(self):
		return self.clean(dict(id = self.unique,
								ability_id = self.ability_id,
								tactic = self.tactic,
								technique_id = self.technique_id,
								technique_name = self.technique_name,
								name = self.name,
								description = self.description,
								platform = self.platform,
								executor = self.executor,
								command = self.command,
								unique = self.unique,
								file_name = self.file_name))

	def __init__(self, ability_id, tactic, technique_id, technique_name, name, description, tactic, platform, executor, command, file_name):
		self.abiltiy_id = ability_id
		self.tactic = tactic
		self.technique_id = technique_id
		self.technique_name = technique_name
		self.name = name
		self.description = description
		self.platform = platform
		self.executor = executor
		self.command = command
		self.file_hash = file_name

	def store(self, ram):
		existing = self.retrieve(ram['art_abilities'], self.unique)
		if not existing:
			ram['art_abilities'].append(self)
			return self.retrieve(ram['art_abilities'], self.unique)
		existing.update('tactic', self.tactic)
		existing.update('technique_id', self.technique_id)
		existing.update('technique_name', self.technique_name)
		existing.update('name', self.name)
		existing.update('description', self.description)
		existing.update('platform', self.platform)
		existing.update('executor', self.executor)
		existing.update('command', self.command)
		existing.update('file_name', self.file_name)
		return existing
