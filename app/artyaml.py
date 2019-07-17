#!/usr/bin/python

import asyncio
import os, sys, yaml

class ARTyaml:
	def __init__(self):
		self.yamlData = None
		self.displayName = None
		self.attackTech = None
		self.atomicTests = None
		
	def load(self, yamlFile):
		self.yamlData = yaml.load(yamlFile, Loader=yaml.Loader)
		if 'atomic_tests' in self.yamlData.keys():
			self.displayName = self.get_displayName()
			self.attackTech = self.get_attackTech()
			self.atomicTests = self.get_atomicTests()

	def get_displayName(self):
		if self.yamlData:
			return self.yamlData['display_name']
				
	def get_attackTech(self):
		if self.yamlData:
			return self.yamlData['attack_technique']

	def get_atomicTests(self):
		if self.yamlData:
			return self.yamlData['atomic_tests']
