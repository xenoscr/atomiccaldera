#!/usr/bin/python
################################################################################
# Name: ac_database.py
# Author: Conor Richard (@xenosCR)
#
# Description: The ACDatabase class is used to perform the database functions 
# required for the Atomic Caldera plugin to work.
#
# Instructions: See the README.md file.
#
# Credits:
# Red Canary's Atomic Red Team - https://github.com/redcanaryco/atomic-red-team
# MITRE's Caldera - https://github.com/mitre/caldera
################################################################################

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
		try:
			await self.dao.create('art_ability', ability)
		except Exception as e:
			self.log.error(e)

	async def create_art_variable(self, variable):
		try:
			await self.dao.create('art_var', variable)
		except Exception as e:
			self.log.error(e)

	async def check_art_ability(self, condition):
		try:
			data = await self.dao.get('art_ability', condition)
		except Exception as e:
			self.log.error(e)
			return False
		if len(data) > 0:
			return True
		else:
			return False

	async def get_art_ability(self, condition):
		data = None
		try:
			data = await self.dao.get('art_ability', condition)
		except Exception as e:
			self.log.error(e)
			return None
		return data

	async def get_art_variable(self, condition):
		data = None
		try:
			data = await self.dao.get('art_var', condition)
		except Exception as e:
			self.log.error(e)
			return None
		return data

	async def explode_art_abilities(self, criteria=None):
		try:
			abilities =  await self.dao.get('art_ability', criteria=criteria)
			for ab in abilities:
				ab['cleanup'] = '' if ab['cleanup'] is None else ab['cleanup']
		except Exception as e:
			self.log.error(e)
			return []
		return abilities
	
	async def explode_art_variables(self, criteria=None):
		try:
			variables = await self.dao.get('art_var', criteria=criteria)
		except Exception as e:
			self.log.error(e)
			return []
		return variables

	async def update_art_ability(self, key, value, data):
		try:
			status = await self.dao.update('art_ability', key, value, data)
		except Exception as e:
			self.log.error(e)
			return False
		return True

	async def update_art_variables(self, data):
		try:
			for variable in data:
				updates = { 'var_name': variable['var_name'], 'value': variable['value'] }
				status = await self.dao.update('art_var', 'id', variable['id'], updates)
				self.log.debug(status)
		except Exception as e:
			self.log.error(e)
			return False
		return True

	async def delete_all(self):
		try:
			status = await self.dao.raw_update('DROP TABLE art_ability;')
			status = await self.dao.raw_update('DROP TABLE art_var;')
		except Exception as e:
			self.log.error(e)
			return 'Deletion failed.'
		return 'Deletion succeded.'
