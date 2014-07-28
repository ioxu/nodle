"""curve drawers
test of glEvalCoord1f to draw a bezier curve
some from http://nullege.com/codes/show/src@p@y@PythonOpenGLSuperBible4-HEAD@chapt10@bezier.py"""
import pyglet
from pyglet.gl import *
import node

class Edge_Creator(object):
	"""docstring for Edge_Creator"""
	def __init__(self, port_from = None, application = None):
		super(Edge_Creator, self).__init__()
		self.port_from = port_from
		self.application = application
		self.window = application.window
		self.window.push_handlers(self)
		self.bezier = Bezier( [ [0,0], [0,0], [0,0], [0,0] ], width = 5 )



	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		#print self, "on_mouse_drag"
		#self.port_from.highlight = True

		self.bezier.update( [ x,
							y ],
							[self.port_from.absx,
							self.port_from.absy] )

		
		# CONSUME
		#return True

	def on_mouse_release(self, x, y, button, modifiers):	
		print(self, "on_mouse_release")
		
		for n in self.application.nodes:
			for p in n.ports:
				if p.in_hit(x,y):
					#self.application.edges.append( node.Edge( port1 = self.port_from, port2 = p ) )
					self.application.edges.append( node.Edge( port2 = self.port_from, port1 = p ) )



		self.remove()
		#return True


	def remove(self):
		print("destroying", self)
		self.window.pop_handlers()
		self.bezier = None
		del(self)
		#print(self)

	def draw(self):
		#print(self, "on_draw", self.bezier.cpoints[3][0])
		#self.bezier.draw(hull = True)
		if self.bezier:
			#self.bezier.draw(hull=True)
			self.bezier.draw(hull=False)
		#return True

class Bezier(object):
	def __init__(self,
				cpoints = [ [0,0], [0,0], [0,0], [0,0] ],
				width = 3,
				colour = (0.4, 0.4, 0.9, 0.75),
				steps = 20):
		"""bezier class, hold control points, and control point colours"""
		print("glevaluator.init()")
		self.colour = colour
		self.hilightcolour = colour#(1.0, 1.0, 0.0, 0.5)
		self.width = width
		self.hull_width = 1.5
		self.steps = steps

		self.tangent_ext = 100

		self.cpoints = cpoints

		self.cpoints = (GLfloat * 3 * 4)((self.cpoints[0][0], self.cpoints[0][1], 0.0),
										(self.cpoints[1][0], self.cpoints[1][1], 0.0),
										(self.cpoints[2][0], self.cpoints[2][1], 0.0),
										(self.cpoints[3][0], self.cpoints[3][1], 0.0))
		
		# self.ccolour = (GLfloat * 4 * 4)(self.hilightcolour,
		# 								self.colour,
		# 								self.colour,
		# 								self.colour)

		self.ccolour = (GLfloat * 4 * 4)(self.colour,
										self.colour,
										self.colour,
										self.colour)


	def update( self, c1, c2 ):
		"""update endpoint coords
		c1: [x1, y1]
		c2: [x2, y2]
		deals with tangent (inner) coords
		"""
		# ratio tangents
		# tangent cv is a ratio of y distance
		height = c2[1] - c1[1]
		ty = max(50,  height * 0.65)

		# cp1 : endpoint one
		self.cpoints[0][0] = c1[0]
		self.cpoints[0][1] = c1[1]

		# t1 : tangent one (cp2)
		self.cpoints[1][0] = c1[0] #self.cpoints[0][0]
		self.cpoints[1][1] = c1[1] + ty #self.tangent_ext

		# t2 : tangent two (cp3)
		self.cpoints[2][0] = c2[0]
		self.cpoints[2][1] = c2[1] - ty #self.tangent_ext

		# cp4
		self.cpoints[3][0] = c2[0]
		self.cpoints[3][1] = c2[1]

	def draw(self, hull = False, hull_points = False):
		"""enable, eval and draw the bezier"""

		##
		## CONVERT TO VERTEX LISTS, remove evaluator, draw to batch in app.
		##

		#print(self, self.draw)

		if hull:
			glLineWidth(self.hull_width)
			glColor4f(0.5, 0.5, 0.5, 0.15)
			pyglet.graphics.draw_indexed(4, pyglet.gl.GL_LINE_STRIP,
			    [0, 1, 2, 3],
			    ('v2f', (self.cpoints[0][0], self.cpoints[0][1],
			    			self.cpoints[1][0], self.cpoints[1][1],
			    			self.cpoints[2][0], self.cpoints[2][1],
			    			self.cpoints[3][0], self.cpoints[3][1],))
			)

		# enable, eval and draw
		glLineWidth(self.width)

		# set up bezier (should be in an update method)
		glMap1f(GL_MAP1_VERTEX_3, 0.0, 1.0, 3 , 4, self.cpoints[0] )
		glMap1f(GL_MAP1_COLOR_4, 0.0, 1.0, 4 , 4, self.ccolour[0] )

		glEnable(GL_MAP1_VERTEX_3)
		glEnable(GL_MAP1_COLOR_4)			

		# stipple
		#glLineStipple(1, 0x00FF)
		glEnable(GL_LINE_STIPPLE)
		glBegin(GL_LINE_STRIP)
		for i in range(0,self.steps+1):
			glEvalCoord1f(i/float(self.steps))
		glEnd()
		


		# end stipple
		#glDisable(GL_LINE_STIPPLE)

