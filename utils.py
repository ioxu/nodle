import math

def distance(x1, y1, x2, y2):
	"""calc distance between (x1,y1) and (x2, y2)"""
	l = (x2 - x1) * (x2 - x1 ) + (y2 - y1) * (y2 - y1)
	return math.sqrt(l)

def distance2(x1, y1, x2, y2):
	"""calc distance between (x1,y1) and (x2, y2)
	without sqrt of result - faster for length comparisons"""
	l = (x2 - x1) * (x2 - x1 ) + (y2 - y1) * (y2 - y1)
	return l

