from plugins.atomiccaldera.app.atomic_caldera import AtomicCaldera
from plugins.atomiccaldera.app.ac_database import ACDatabase
from app.database.core_dao import CoreDao

name = 'AtomicCaldera'
description = 'A plugin for MITRE\'s Caldera to convert and manage Red Canaries Atomic Red Team tests for use with stockpile and chain.'
address = '/plugin/atomiccaldera/gui'

async def initialize(app, services):
	ac_data_svc = ACDatabase(CoreDao('ac.db'), services.get('utility_svc'))
	ac_api = AtomicCaldera(services, ac_data_svc)
	data_svc = services.get('data_svc')
	app.router.add_route('*', '/plugin/atomiccaldera/gui', ac_api.landing)
	app.router.add_route('*', '/plugin/atomiccaldera/rest', ac_api.rest_api)
