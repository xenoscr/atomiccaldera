################################################################################
# Name: atomic_caldera.py
# Author: Conor Richard (@xenosCR)
#
# Description: This is the plugin version of the original Atomic-Caldera script
# the purpose of this plugin is to simplify the task of importing Red Canary's
# Atomic Red Team tests into MITRE's Caldera testing framework. With this plugin
# you can quickly build a library of abilities that can be used to create custom
# adversaries to use with Caldera.
#
# Instructions: See the README.md file.
#
# Credits:
# Red Canary's Atomic Red Team - https://github.com/redcanaryco/atomic-red-team
# MITRE's Caldera - https://github.com/mitre/caldera
################################################################################

import asyncio, json, logging, os, sys, re, uuid, yaml

from plugins.atomiccaldera.app.artyaml import ARTyaml
from app.utility.logger import Logger

from pathlib import Path
from base64 import b64encode, b64decode
from aiohttp import web
from aiohttp_jinja2 import template
from stix2 import FileSystemSource
from stix2 import Filter

class cmdStr(str):
	pass

def cmd_presenter(dumper, data):
	return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

class AtomicCaldera:

	def __init__(self, services, ac_data_svc):
		self.ac_data_svc = ac_data_svc
		self.data_svc = services.get('data_svc')
		self.auth_svc = services.get('auth_svc')
		self.log = Logger('atomiccaldera')
		self.log.debug('Atomic-Caldera Plugin Logging started.')
		self.get_conf()
		self.art_data_svc = artDataService(self.conf)

	def get_conf(self):
		confPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/artconf.yml')
		try:
			with open(confPath, 'r') as c:
				self.conf = yaml.load(c, Loader=yaml.Loader)
			self.ctipath = os.path.expanduser(os.path.join(self.conf['ctipath'], 'enterprise-attack/'))
			self.artpath = os.path.expanduser(self.conf['artpath'])
			self.log.debug(self.ctipath)
			self.log.debug(self.artpath)
		except:
			pass

	@template('atomiccaldera.html')
	async def landing(self, request):
		await self.auth_svc.check_permissions(request)
		abilities = []
		tactics = []
		variables = []
		try:
			abilities = await self.ac_data_svc.explode_art_abilities()
			for ab in abilities:
				if not ab['tactic'] in tactics:
					tactics.append(ab['tactic'])
		except Exception as e:
			self.log.error(e)

		try:
			variables = await self.ac_data_svc.explode_art_variables()
		except Exception as e:
			self.log.error(e)
		return { 'abilities': json.dumps(abilities), 'tactics': tactics, 'variables': json.dumps(variables) }

	async def getMITREPhase(self, attackID):
		filter = [
					Filter('type', '=', 'attack-pattern'),
					Filter('external_references.external_id', '=', attackID)
				]
		result = self.fs.query(filter)
		if result:
			return result[0].kill_chain_phases[0].phase_name
		else:
			return 'unknown'

	async def get_atomics(self):
		await self.ac_data_svc.build_db(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/ac.sql'))
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
												artAbilities.append({'ability_id': ability_id,
													'technique': artObj.attackTech[1:],
													'name': name,
													'description': description,
													'tactic': await self.getMITREPhase(artObj.attackTech),
													'attack_name': artObj.displayName,
													'platform': platform,
													'executor': executor,
													'command': b64encode(command.encode('utf-8')).decode('utf-8')})
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
														artVars.append({'ability_id': ability_id,
															'var_name': argument,
															'value': b64encode(curVar.encode('utf-8')).decode('utf-8')})
													except:
														pass
		else:
			self.log.debug('Paths are not valid')
			return {'abilities': [], 'variables': []}
		self.log.debug('Got to the end.')
		return {'abilities': artAbilities, 'variables': artVars}

	async def export_all_to_stockpile(self, data):
		try:
			abilities = await self.ac_data_svc.explode_art_abilities()
		except Exception as e:
			self.log.error(e)
		try:
			variables = await self.ac_data_svc.explode_art_variables()
		except Exception as e:
			self.log.error(e)
		if await self.export_to_stockpile(abilities, variables):
			return 'Abilities successfully exported.'
		else:
			return 'Failed to export abilities.'
	
	async def export_one_to_stockpile(self, data):
		abilities = []
		variables = []
		ability_id = { 'ability_id': data.pop('ability_id') }
		try:
			abilities = await self.ac_data_svc.get_art_ability(ability_id)
		except Exception as e:
			self.log.error(e)
		try:
			variables = await self.ac_data_svc.get_art_variable(ability_id)
		except Exception as e:
			self.log.error(e)
		if await self.export_to_stockpile(abilities, variables):
			return 'Ability successfully exported.'
		else:
			return 'Failed to export ability.'

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

	async def get_art(self, request):
		self.log.debug('Landed in get_art.')
		try:
			atomics = await self.get_atomics()
		except Exception as e:
			self.log.error(e)
			pass
		return atomics

	async def import_art_abilities(self):
		try:
			atomics = await self.get_atomics()
		except Exception as e:
			self.log.error(e)
			return 'Failed to load abilities.'
		for ability in atomics['abilities']:
			await self.ac_data_svc.create_art_ability(ability)
		for variable in atomics['variables']:
			await self.ac_data_svc.create_art_variable(variable)
		return 'Successfully imported new abilities.'
	
	async def save_art_ability(self, data):
		key = data.pop('key')
		value = data.pop('value')
		updates = data.pop('data')
		if await self.ac_data_svc.update_art_ability(key, value, updates):
			return 'Updated ability: {}'.format(value)
		else:
			return 'Update failed for ability: {}'.format(value)

	async def save_art_variables(self, data):
		updates = data.pop('data')
		if await self.ac_data_svc.update_art_variables(updates):
			return 'Updated variables successfully.'
		else:
			return 'Updates to variables failed.'
	
	async def delete_all(self):
		abilities = []
		payloadPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../stockpile/data/payloads/')
		abilityPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../stockpile/data/abilities/')
		try:
			abilities = await self.ac_data_svc.explode_art_abilities()
		except Exception as e:
			self.log.error(e)

		for ability in abilities:
			if os.path.exists(os.path.join(abilityPath, ability['tactic'], '{}.yml'.format(ability['ability_id']))):
				os.remove(os.path.join(abilityPath, ability['tactic'], '{}.yml'.format(ability['ability_id'])))
			if os.path.exists(os.path.join(payloadPath, '{}.bat'.format(ability['ability_id']))):
				os.remove(os.path.join(payloadPath, '{}.bat'.format(ability['ability_id'])))
		status = await self.ac_data_svc.delete_all()
		await self.ac_data_svc.build_db(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/ac.sql'))
		return status
			

	async def rest_api(self, request):
		self.log.debug('Starting Rest call.')
		await self.auth_svc.check_permissions(request)
		data = dict(await request.json())
		index = data.pop('index')
		self.log.debug('Index: {}'.format(index))
		
		options = dict(
			PUT=dict(
				ac_ability=lambda d: self.import_art_abilities(**d)
			),
			POST=dict(
				ac_ability=lambda d: self.ac_data_svc.explode_art_abilities(**d),
				ac_ability_save=lambda d: self.save_art_ability(data=d),
				ac_variables_save=lambda d: self.save_art_variables(data=d),
				ac_export_all=lambda d: self.export_all_to_stockpile(**d),
				ac_export_one=lambda d: self.export_one_to_stockpile(data=d)
			),
			DELETE=dict(
				delete_all=lambda d: self.delete_all(**d)
			)
		)
		try:
			output = await options[request.method][index](data)
		except Exception as e:
			self.log.debug('Stopped at api call.')
			self.log.error(e)
		return web.json_response(output)

