################################################################################
# Name: hook.py
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

from plugins.atomiccaldera.app.atomic_caldera import AtomicCaldera
from plugins.atomiccaldera.app.ac_database import ACDatabase
from app.database.core_dao import CoreDao

name = 'AtomicCaldera'
description = 'A plugin for MITRE\'s Caldera to convert and manage Red Canaries Atomic Red Team tests for use with stockpile and chain.'
address = '/plugin/atomiccaldera/gui'

async def initialize(app, services):
	ac_data_svc = ACDatabase(CoreDao('ac.db', False), services.get('utility_svc'))
	ac_api = AtomicCaldera(services, ac_data_svc)
	data_svc = services.get('data_svc')
	app.router.add_static('/atomiccaldera', 'plugins/atomiccaldera/static', append_version=True)
	app.router.add_route('*', '/plugin/atomiccaldera/gui', ac_api.landing)
	app.router.add_route('*', '/plugin/atomiccaldera/rest', ac_api.rest_api)
