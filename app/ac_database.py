#!/usr/bin/python

import asyncio, os
from app.database.relational import Sql

# The following class was shamelessly ripped from the core MITRE Caldera core_dao.py file.
# Credits to MITRE and the original authors.
class CoreDao:

	def __init__(self, database, schema):
		self.db = Sql(database)
		self.db.build(schema)

	async def build(self, schema):
		await self.db.build(schema)

	async def get(self, table, criteria=None):
		return await self.db.get(table, criteria)

	async def unique(self, column, table):
		return await self.db.unique(column, table)

	async def create(self, table, data):
		return await self.db.create(table, data)

	async def delete(self, table, data):
		return await self.db.delete(table, data)

	async def update(self, table, key, value, data):
		await self.db.update(table, key, value, data)

	async def get_in(self, table, field, elements):
		return await self.db.get_in(table, field, elements)

	async def raw_select(self, sql):
		return await self.db.raw_select(sql)

	async def raw_update(self, sql):
		return await self.db.raw_update(sql)

class ACDatabase:
	def __init__(self, dao):
		self.dao = dao
		self.dao.build(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/ac.sql'))

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
