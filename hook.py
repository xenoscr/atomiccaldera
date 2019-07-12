from plugins.atomiccaldera.app.atomic_caldera import AtomicCaldera

name = 'AtomicCalera'
description = 'A plugin for MITRE\'s Caldera to convert and manage Red Canaries Atomic Red Team tests for use with stockpile and chain.'
address = '/plugin/atomiccaldera/gui'

async def initialize(app, services):
	ac_api = AtomicCaldera(services)
	data_svc = services.get('data_svc')
	app.router.add_route('GET', '/plugin/atomiccaldera/gui', ac_api.landing)
