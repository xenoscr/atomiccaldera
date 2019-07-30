#!/usr/bin/python
################################################################################
# Name: artyaml.py
# Author: Conor Richard (@xenosCR)
#
# Description: The ARTyaml class is a simple class that is used to read and
# parse the contents of Red Canary's Atomic Red Team (ART) YAML files.
#
# Instructions: See the README.md file.
#
# Credits:
# Red Canary's Atomic Red Team - https://github.com/redcanaryco/atomic-red-team
# MITRE's Caldera - https://github.com/mitre/caldera
################################################################################

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
