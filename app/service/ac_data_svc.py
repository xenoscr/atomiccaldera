import asyncio
import glob
import json
import pickle
import os
import sys
import re
import uuid
import yaml
from base64 import b64encode
from collection import defaultdict

from plugins.atomiccaldera.app.objects.c_ability import artAbility
from app.service.base_svc import BaseService

class cmdStr(str):
	pass

def cmd_presenter(dumper, data):
	return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

class artDataService(BaseService):

	def __init__(self, conf):
		self.log = self.add_service('ac_data_svc', self)
		self.conf = conf
		self.ctipath = os.path.expanduser(os.path.join(self.conf['ctipath'], 'enterprise-attack/'))
		self.artpath = os.path.expanduser(self.conf['artpath'])
		self.log.debug(self.ctipath)
		self.log.debug(self.artpath)
		self.cti_svc = CTIService(self.ctipath)
		self.ac_ram = dict(ac_abilities = [], ac_variables = [])

	async def save_ac_state(self):
		"""
		Save RAM database to file
		:return"
		"""
		with open('plugins/atomiccaldera/data/object_store', 'wb') as objects:
			pickle.dump(self.ac_ram, objects)

	async def restore_ac_state(self):
		"""
		Restore the Atomic Caldera object database
		:return:
		"""
		if os.path.exists('plugins/atomiccaldera/data/object_store'):
			await asyncio.sleep(3)
			with open('plugin/atomiccaldera/data/object_store', 'rb') as objects:
				ram = pickle.load(objects)
				for key in ram.keys():
					for c_object in ram[key]:
						await self.store(c_object)
			self.log.debug('Restored ac object')

	async def ac_apply(self, collection):
		"""
		Add a new collection to RAM
		:param collection:
		:return:
		"""
		self.ac_ram[collection] = []

	async def load_data(self):
		"""
		Read all the data sources to populate the object store
		:param dirctory:
		:param schema:
		:return: None
		"""
		self.log.debug('Loading Atomic-Red-Team data.')
		await self._load_art())

	async def ac_store(self, c_object):
		"""
		Accept any c_object type and store it (create/update) in RAM
		:parmam c_object:
		:return: a single c_object
		"""
		try:
			return c_object.store(self.ac_ram)
		except Exception as e:
			self.log.error('[!] can only store first-class objects: {}'.format(e))

	async def ac_locate(self, object_name, match=None):
		"""
		Find all c_objects which match a search. Return all c_objects if no match.
		:param object_name:
		:param match: dict()
		:return: a list of c_object types
		"""
		try:
			return [obj] for obj in self.ac_ram[object_name] if obj.match(match)]
		except Exception as e:
			self.log.error('[!] LOCATE: {}'.format(e))

	async def ac_remove(self, object_name, match):
		"""
		Remove any c_objects which match a search
		:param object_name:
		:param match: dict()
		:return:
		"""
		try:
			self.ac_ram[object_name][:] = [obj for obj in self.ac_ram[object_name] if not obj.match(match)]
		except Exception as e:
			self.log.error('[!] REMOVE: {}'.format(e))

	async def _load_art(self):
		artAbilities = []
		artVars = []
		if os.path.exists(self.artpath):
			for root, dirs, files in os.walk(self.artpath):
				for procFile in files:
					fullFile = os.path.join(root, procFile)
					if os.path.splitext(fullFile)[-1].lower() == '.yaml':
						self.log.debug('Processing {}'.format(fullFile))
						try:
							artObj = ARTyaml()
						except:
							continue
						with open(fullFile, 'r') as yamlFile:
							try:
								artObj.load(yamlFile)
							except:
								continue
						# Loop through the tests
						if artObj.atomicTests:
							for atomic in artObj.atomicTests:
								for platform in atomic['supported_platforms']:
									if platform.lower() in ['windows', 'linux', 'macos']:
										name = atomic['name']
										description = atomic['description']
										if 'command' in atomic['executor'].keys():
											command = re.sub(r'x07', r'a', repr(atomic['executor']['command'])).strip()
											command = command.encode('utf-8').decode('unicode_escape')
											executor = atomic['executor']['name']
											if command[0] == '\'':
												command = command.strip('\'')
											elif command[0] == '\"':
												command = command.strip('\"')
										else:
											command = ''
											executor = ''
										
										try:
											if command != '':
												checkUnique = { 'technique': int(artObj.attackTech[1:]),
													'command': b64encode(command.encode('utf-8')).decode('utf-8')}
										except Exception as e:
											print(e)
										
										# Check to see if the command has been added to the database
										if (command != '' and not await self.ac_data_svc.check_art_ability(checkUnique)):
											uuidBool = True
											while(uuidBool):
												ability_id = str(uuid.uuid4())
												if not await self.ac_data_svc.check_art_ability({ 'ability_id': ability_id }):
													uuidBool = False

											try:
												# Add the new ability to export
												self._create_ac_ability(ability_id, await self.cti_svc.getMITREPhase(artObj.attackTech),
																		artObj.attackTech, artObj.displayName,
																		name, description,
																		platform, executor,  
																		b64encode(command.encode('utf-8')).decode('utf-8'))
											except Exception as e:
												print(e)

											if 'input_arguments' in atomic.keys():
												for argument in atomic['input_arguments'].keys():
													try:
														curVar = re.sub(r'x07', r'a', repr(atomic['input_arguments'][argument]['default'])).strip()
														if curVar[0] == '\'':
															curVar = curVar.strip('\'')
														elif curVar[0] == '\"':
															curVar = curVar.strip('\"')
														curVar = curVar.replace('\\\\', '\\')
														self._create_ac_variable(ability_id, argument, b64encode(curVar.encode('utf-8')).decode('utf-8'))
													except:
														pass
		else:
			self.log.debug('Paths are not valid')
			return 'Failed to load the Atomic Red Team tests.'
		self.log.debug('Got to the end.')
	

	async def export_all_to_stockpile(self):
		try:
			abilities = await self.ac_locate('art_abilities')
		except Exception as e:
			self.log.error(e)
		try:
			variables = await self.ac_locate('art_variables')
		except Exception as e:
			self.log.error(e)
		if await self.export_to_stockpile(abilities, variables):
			return 'Abilities successfully exported.'
		else:
			return 'Failed to export abilities.'

	async def export_to_stockpile(self, abilities, variables):
		# String representer foy PyYAML to format the command string
		yaml.add_representer(cmdStr, cmd_presenter)

		for ability in abilities:
			executor = ability['executor']
			platform = ability['platform']
			payload = ''

			# Fix the command formatting
			command = b64decode(ability['command'])
			command = command.decode('utf-8')
			if command[0] == '\'':
				command = command.strip('\'')
			elif command[0] == '\"':
				command = command.strip('\"')

			# Determin the executor
			# Fill in the variables
			for variable in variables:
				if variable['ability_id'] == ability['ability_id']:
					value = b64decode(variable['value']).decode('utf-8')
					if value[0] == '\'':
						value = value.strip('\'')
					elif value[0] == '\"':
						value = value.strip('\"')

					value = value.replace('\\\\', '\\')
					command = re.sub(r"\#{{{argName}}}".format(argName = str(variable['var_name'])), value.encode('unicode-escape').decode(), command)

			if (executor.lower() == 'sh' or executor.lower() == 'bash'):
				if platform.lower() == 'linux':
					platform = 'linux'
				elif platform.lower() == 'macos':
					platform = 'darwin'
			elif (executor.lower() == 'command_prompt' or executor.lower() == 'powershell'):
				if (executor.lower() == 'command_prompt'):
					executor = 'cmd'	
				else:
					executor = 'psh'	
			command = command.replace('\\n','\n')

			# Future additions
			parserName = ''
			parserProperty = ''
			parserScript = ''

			# Build the YAML data
			#newYaml = [{ 'id': ability['ability_id'],
			#	'name': ability['name'],
			#	'description': ability['description'],
			#	'tactic': ability['tactic'],
			#	'technique': { 'attack_id': 'T{}'.format(str(ability['technique'])), 'name': ability['attack_name'] },
			#	'platforms': { platform: { executor.lower(): { 'command': cmdStr(command), 'payload': payload, 'parser': { 'name': parserName, 'property': parserProperty, 'script': parserScript }}}}}]

			newYaml = [{ 'id': ability['ability_id'],
				'name': ability['name'],
				'description': ability['description'],
				'tactic': ability['tactic'],
				'technique': { 'attack_id': 'T{}'.format(str(ability['technique'])), 'name': ability['attack_name'] },
				'platforms': { platform: { executor.lower(): { 'command': cmdStr(command), 'payload': payload }}}}]

			payloadPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../stockpile/data/payloads/')
			abilityPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../stockpile//data/abilities/')

			# Check and create payloads folder if it does not exist
			try:
				if not os.path.exists(payloadPath):
					os.makedirs(payloadPath)
			except Exception as e:
				self.log.error(e)
				return False

			# Write the BAT file if needed
			if payload != '':
				with open(os.path.join(payloadPath, payload), 'w') as payloadFile:
					payloadFile.write(batCommand)

			# Check and create ability folder if it does not exist
			try:
				if not os.path.exists(os.path.join(abilityPath, ability['tactic'])):
					os.makedirs(os.path.join(abilityPath, ability['tactic']))
			except Exception as e:
				self.log.error(e)
				return False

			# Write the YAML file to the correct directory
			try:
				with open(os.path.join(abilityPath, ability['tactic'], '{}.yml'.format(ability['ability_id'])), 'w') as newYAMLFile:
					dump = yaml.dump(newYaml, default_style = None, default_flow_style = False, allow_unicode = True, encoding = None, sort_keys = False)
					newYAMLFile.write(dump)
			except Exception as e:
				self.log.error(e)
				return False
		return True

	async def _create_ac_ability(self, ability_id, tactic, technique_id, technique_name, name, description, platform, executor, command):
		await self.ac_store(artAbility(ability_id = ability_id, tactic = tactic, technique_id = technique_id, technique_name = technique_name, name = name, description = description, platform = platform, executor = executor, command = command))

	async def _create_ac_variable(self, ability_id, name, value):
		await self.ac_store(artVariable(ability_id = ability_id, name = name, value = value))
