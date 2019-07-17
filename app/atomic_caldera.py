import asyncio, logging, os, sys, re, uuid, yaml

from plugins.atomiccaldera.app.artyaml import ARTyaml
from plugins.atomiccaldera.app.ac_database import CoreDao
from plugins.atomiccaldera.app.ac_database import ACDatabase
from app.utility.logger import Logger

from aiohttp import web
from aiohttp_jinja2 import template
from stix2 import FileSystemSource
from stix2 import Filter

class AtomicCaldera:

	def __init__(self, services):
		self.data_svc = services.get('data_svc')
		self.auth_svc = services.get('auth_svc')
		self.log = Logger('atomiccaldera')
		self.log.debug('Atomic-Caldera Plugin Logging started.')
		self.get_conf()
		self.fs = FileSystemSource(self.ctipath)

	@asyncio.coroutine
	async def setupDB():
		self.dao = CoreDao(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../ac.db'))
		self.ac_data_svc = ACDatabase(self.dao)
		

	def get_conf(self):
		confPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/artconf.yml')
		try:
			with open(confPath, 'r') as c:
				conf = yaml.load(c, Loader=yaml.Loader)
			self.ctipath = os.path.expanduser(os.path.join(conf['ctipath'], 'enterprise-attack/'))
			self.artpath = os.path.expanduser(conf['artpath'])
			self.log.debug(self.ctipath)
			self.log.debug(self.artpath)
		except:
			pass

	@template('atomiccaldera.html')
	async def landing(self, request):
		self.log.debug('Landing started')
		await self.auth_svc.check_permissions(request)
		return web.json_response(await self.get_art(request))

	async def getMITREPhase(attackID):
		filter = [
					Filter('type', '=', 'attack-pattern'),
					Filter('external_references.external_id', '=', attackID)
				]
		result = self.fs.query(filter)
		if result:
			return result[0].kill_chain_phases[0].phase_name
		else:
			return 'unknown'

	async def get_art(self, request):
		self.log.debug('Landed in get_art.')
		atomics = await get_atomics()
		return atomics
		#artAbilities = {'abilities': []}
		#if (os.path.exists(self.ctipath) and os.path.exists(self.artpath)):
		#	for root, dirs, files in os.walk(self.artpath):
		#		for procFile in files:
		#			fullFile = os.path.join(root, procFile)
		#			self.log.debug('Processing {}'.format(fullFile))
		#			if os.path.splitext(fullFile)[-1].lower() == '.yaml':
		#				try:
		#					artObj = ARTyaml()
		#				except:
		#					continue
		#				with open(fullFile, 'r') as yamlFile:
		#					try:
		#						artObj.load(yamlFile)
		#					except:
		#						continue
		#				artAbilities['abilities'].append(artObj.yamlData)
		#else:
		#	self.log.debug('Paths are not valid')
		#	return None
		#return artAbilities

	async def import_art_abilities(self, request):
		atomics = get_atomics()
		for ability in atomics['abilities']:
			self.ac_data_svc.create_art_ability(ability)

	async def get_atomics(self):
		self.log.debug('Landed in get_atomics')
		artAbilities = []
		artVars = []
		if os.path.exists(self.artpath):
			for root, dirs, files in os.walk(self.artpath):
				for procFile in files:
					fullFile = os.path.join(root, procFile)
					self.log.debug('Processing {}'.format(fullFile))
					if os.path.splitext(fullFile)[-1].lower() == '.yaml':
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
						for atomic in artObj.atomicTests:
							attack_name = atomic['name']
							description = atomic['description']
							if 'command' in atomic['executor'].keys():
								command = re.sub(r'x07', r'a', repr(atomic['executor']['command'])).strip().encode('utf-8')
								executor = atomic['executor']['name']
							else:
								command = ''
								executor = ''
							
							checkUnique = { 'technique': artObj.attackTech[1:],
								'command': b64encode(command)}
							
							# Check to see if the command has been added to the database
							if (command != '' and not self.ac_data_svc.check_art_ability(checkUnique)):
								uuidBool = True
								while(uuidBool):
									ability_id = uuid.uuid4()
									if len(await self.dao.get('ac_ability', { 'ability_id': ability_id })) == 0:
										uuidBool = False

								# Add the new ability to export
								artAbilities.append({'ability_id': ability_id,
									'technique': artObj.attackTech[1:],
									'name': name,
									'description': description,
									'tactic': await getMITREPhase(artObj.attackTech),
									'attack_name': attack_name,
									'executor': executor,
									'command': b64eincode(command)})

								if 'input_arguments' in atomic.keys():
									for arguent in atomic['input_argument'].keys():
										try:
											curVar = re.sub(r'x07', r'a', repr(atomic['input_arguments'][argument]['default']))
										except:
											pass
										artVar.append({'ability_id': ability_id,
											'var_name': arguent,
											'value': curVar})
		else:
			self.log.debug('Paths are not valid')
			return {'abilities': [], 'variables': []}
		return {'abilities': artAbilities, 'variables': artVar}

	async def rest_api(self, request):
		await self.auth_svc.check_permissions(request)
		data = dict(await request.json())
		index = data.pop('index')
		
		options = dict(
			PUT=dict(
				ac_ability=lambda d: self.create_art_ability(**d)
			),
			POST=dict(
				ac_ability=lambda d: self.explode_art_abilities(**d)
			)
		)
		output = await options[request.method][index](data)
		return web.json_response(output)

