from stix2 import FileSystemSource
from stix2 import Filter

from app.service.base_svc import BaseService

class CTIService(BaseService):

	def __init__(self, conf):
		self.log = self.add_service('cti_scv', self)
		self.fs = FileSystemSource(conf.ctipath)

	async def getMITREPhase(self, attackID):
		filter = [
					Filter('type', '=', 'attack-pattern'),
					Filter('external_references.external_id', '=', attackID)
				]
		result = self.fs.query(filter)
		if result:
			return result[0].kill_chain_phases[0].phase_name
		else:
			return 'unknown'
