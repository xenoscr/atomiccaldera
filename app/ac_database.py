#!/usr/bin/python

import asyncio, os

class ACDatabase:
	def __init__(self, dao, utility_svc):
		self.dao = dao
		self.utility_svc = utility_svc
		self.log = utility_svc.create_logger('ac_data_svc')

	async def build_db(self, schema):
		with open(schema) as schema:
			await self.dao.build(schema.read())

	async def create_art_ability(self, ability):
		self.log.debug('Creating art ability.')
		try:
			await self.dao.create('art_ability', ability)
		except Exception as e:
			self.log.error(e)

	async def create_art_variable(self, variable):
		self.log.debug('Creating art variable.')
		try:
			await self.dao.create('art_var', variable)
		except Exception as e:
			self.log.error(e)

	async def check_art_ability(self, condition):
		self.log.debug('Condition checked: {}'.format(condition))
		try:
			data = await self.dao.get('art_ability', condition)
		except Exception as e:
			self.log.error(e)
			return False
		self.log.debug(data)
		if len(data) > 0:
			self.log.debug('Ability found.')
			return True
		else:
			self.log.debug('Ability not found.')
			return False

	async def explode_art_abilities(self, criteria=None):
		try:
			abilities =  await self.dao.get('art_ability', criteria=criteria)
			self.log.debug(abilities)
			for ab in abilities:
				ab['cleanup'] = '' if ab['cleanup'] is None else ab['cleanup']
		except Exception as e:
			self.log.error(e)
			return []
		return abilities

