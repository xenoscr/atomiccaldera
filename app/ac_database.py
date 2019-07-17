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
		await self.dao.create('art_ability', ability)

	async def check_art_ability(self, condition):
		data = await self.dao.get('art_ability', condition)
		if len(data) > 0:
			return True
		else:
			return False

	async def create_art_variable(self, variable):
		await self.dao.create('art_var', variable)
