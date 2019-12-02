from epics import caput, caget

class laser_shutter:
	def __init__(self, Id, z_undulator=None, description=None):
		self.Id = Id

	def __repr__(self):
		return self.get_status()
    
	def get_status(self):
		Id = self.Id
		status = caget(Id+":SET_BO02")
		if status == 0:
			return 'open'
		elif status == 1:
			return 'close'
		else:
			return "unknown"

	def open(self):
		caput(self.Id+":SET_BO02",0)

	def close(self):
		caput(self.Id+":SET_BO02",1)

		
