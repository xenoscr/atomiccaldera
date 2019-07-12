import asyncio, logging, os, sys, re, uuid, yaml

from plugins.atomiccaldera.app.artyaml import ARTyaml
from app.utility.logger import Logger

from aiohttp import web
from aiohttp_jinja2 import template

class AtomicCaldera:

	def __init__(self, services):
		self.data_svc = services.get('data_svc')
		self.auth_svc = services.get('auth_svc')
		self.log = Logger('atomiccaldera')
		self.log.debug('Logging started')
		self.get_conf()

	def get_conf(self):
		#try:
		#	with open('plugins/atomiccaldera/conf/artconf.yml', 'r') as c:
		#		conf = yaml.load(c, Loader=yaml.Loader)
		#	self.ctipath = conf['citpath']
		#	self.artpath = conf['artpath']
		#	self.log.debug('Art YAML loaded')
		#except:
		#	self.log.debug('Art YAML not loaded')
		#	pass
		self.ctipath = '/home/conor/working/atomic-caldera/cti'
		self.artpath = '/home/conor/working/forks/atomic-red-team/atomics'


	@template('atomiccaldera.html')
	async def landing(self, request):
		self.log.debug('Landing started')
		await self.auth_svc.check_permissions(request)
		return dict(abilities=await self.get_art(request))

	async def get_art(self, request):
		self.log.debug('Get ART started.')
		artAbilities = []
		if (os.path.exists(self.ctipath) and os.path.exists(self.artpath)):
			self.log.debug('Paths are valid.')
			for root, dirs, files in os.walk(self.artpath):
				for procFile in files:
					fullFile = os.path.join(root, procFile)
					self.log.debug('Processing {}'.format(fullFile))
					if os.path.splitext(fullFile)[-1].lower() == '.yaml':
						try:
							artObj = ARTyaml()
						except:
							self.log.debug('what the actual....')
						self.log.debut('Starting Processing')
						with open(fullFile, 'r') as yamFile:
							try:
								artObj.load(yamlFile)
								self.log.debug('Yaml loaded.')
								self.log.debug(artObj.atomicTests)
							except:
								self.log.degug('Yaml Data not loaded')
		else:
			self.log.debug('Paths are not valid')
			return None
		return web.json_response(dict(abilities=artAbilities))

