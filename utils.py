import math

def distance(x1, y1, x2, y2):
	"""calc distance between (x1,y1) and (x2, y2)"""
	l = (x2 - x1) * (x2 - x1 ) + (y2 - y1) * (y2 - y1)
	return math.sqrt(l)


