from pyglet.gl import *
from pyglet.window import mouse
import utils, curves

class Edge_Creator(object):
	"""docstring for Edge_Creator"""
	def __init__(self, port_from = None, application = None):
		super(Edge_Creator, self).__init__()
		self.port_from = port_from
		self.application = application
		self.window = application.window
		self.window.push_handlers(self)
		self.bezier = curves.Bezier( [ [0,0], [0,0], [0,0], [0,0] ], width = 5 )
		print self, "init", "DRAG"

		# find candidates to drop onto (implicitly avoids dropping onto port_from)
		ports = [p for n in self.application.nodes for p in n.ports]
		if self.port_from.style == "in":
			self.candidates = [p for p in ports if p.style == "out" ]
		if self.port_from.style == "out":
			self.candidates = [p for p in ports if p.style == "in" ]


	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.port_from.style == "out":
			self.bezier.update( [ x, y ],
								[self.port_from.absx,
								self.port_from.absy] )
		elif self.port_from.style == "in":
			self.bezier.update([self.port_from.absx,
								self.port_from.absy],
								[ x, y ])
		
		# CONSUME
		#return True

	def on_mouse_release(self, x, y, button, modifiers):	
		print self, "on_mouse_release", "DROP"
		for p in self.candidates:
			if p.in_hit(x,y):
				edge = self.port_from.connect( p )
				# if remove != None :
				# 	print "REMOVE", self.application.edges[remove], remove
				# 	self.application.edges.remove( remove )
				self.application.edges.append( edge )

				# if self.port_from.style == "out":
				# 	self.application.edges.append( Edge( port1 = p, port2 = self.port_from ) )

				# elif self.port_from.style == "in":
				# 	self.application.edges.append( Edge( port1 = self.port_from, port2 = p ) )

		# destroy self
		self.remove()


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

class Edge(object):
	"""docstring for Edge"""
	def __init__(self,
				port1 = None,
				port2 = None,
				curve = curves.Bezier() ):
		super(Edge, self).__init__()
		self.port1 = port1
		self.port2 = port2
		self.curve = curve

	def draw(self):
		self.curve.update([self.port1.absx, self.port1.absy], [self.port2.absx, self.port2.absy])
		#self.curve.draw(hull=True)
		self.curve.draw(hull=False)

	def remove(self):
		"""remove an edge from ports"""
		print self, "REMOVE"
		self.port1.edge = None
		self.port2.edge = None
		del(self)

class Port(object):
	"""docstring for Port"""
	def __init__(self,
			name = "port",
			x = 0.0,
			y= 0.0,
			size = 10,
			colour = (0.5,0.5,0.5,0.5),
			parent = None,
			style = "in",
			window = None,
			**kwargs):
		super(Port, self).__init__()
		self.name = name
		self.x = x
		self.y = y
		self.size = size
		self.colour = colour
		self.parent = parent
		self.style = style
		self.edge = None

		# interaction
		self.hit_size = self.size*2

		self.highlight = False
		self.highlight_colour = self.colour

		self.selected = False
		self.selected_colour = (1.0, 0.75, 0.5, 0.5)

		#self.edge_creator = None

	@property
	def absx(self):
		return self.parent.x + self.x

	@property
	def absy(self):
		return self.parent.y + self.y

	def attach(self, parent):
		"""attach port to parent"""
		self.parent = parent

	def connect(self, port):
		"connect to a port"
		print port.edge, "port.edge"

		if port.edge:
			port.disconnect()

		if self.style == "in" and port.style == "out" :
			self.edge = Edge( port1 = self, port2 = port )
			port.edge = self.edge
		elif self.style == "out" and port.style == "in":
			self.edge = Edge( port1 = port, port2 = self )
			port.edge = self.edge
		return self.edge

	def disconnect(self):
		self.edge.remove()

	def draw(self):
		#print self, self.selected

		if self.selected:
			glColor4f(*self.selected_colour)
			glPointSize(self.hit_size)
		
		elif self.highlight: # highlighted
			glColor4f(*self.highlight_colour)
			glPointSize(self.hit_size)
		
		else:
			glColor4f(*self.colour)
			glPointSize(self.size)


		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
    		('v2f', (self.x + self.parent.x, self.y + self.parent.y))
		)

	# events
	def push_handlers(self, window):
		window.push_handlers(self.on_mouse_drag,
							self.on_mouse_press,
							self.on_mouse_motion,
							self.on_mouse_release)

	def on_mouse_motion( self, x, y, dx, dy ):
		#print self, "on_mouse_motion"


		if self.in_hit(x, y):
			self.highlight = True
		else:
			self.highlight = False

	def on_mouse_press(self, x, y, buttons, modifiers):
	    if buttons & mouse.LEFT:
			if self.in_hit(x, y):
				self.selected = True
				
				print(self, "drag init")
				#self.edge_creator = self.parent.parent.create_edge(self)
				self.parent.parent.create_edge(self)

	def on_mouse_release(self, x, y, button, modifiers):
		#if self.selected and not self.in_hit(x, y):
		if self.selected:
			self.selected = False
			self.highlight = False
			print self, "on_mouse_release"

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		
		##
		#print("port on_mouse_drag", self.edge_creator)
		##

		if self.in_hit(x, y):
			self.highlight = True
		else:
			self.highlight = False

		if buttons & mouse.LEFT:
			if self.selected:
				#print self, "on_mouse_drag"
				pass
			else:
				pass

	def in_hit(self, x, y):
		d = utils.distance( x, y, self.x + self.parent.x, self.y + self.parent.y )
		return d < self.hit_size/2

class Node(object):
	"""docstring for Node"""
	def __init__(self,
			x = 0.0,
			y = 0.0,
			size = 30,
			colour = (0.5,0.5,0.5,0.5),
			window = None,
			name = "Node",
			parent = None,
			**kwargs):

		self.name = name
		self.x = x
		self.y = y
		self.size = size
		self.hit_size = self.size *2
		self.colour = colour
		self.window = window

		self.parent = parent

		self.highlight = False
		self.highlight_colour = self.colour

		self.selected = False
		self.selected_colour = (1.0, 0.75, 0.5, 0.5)

		# ports
		self.ports = []

		# register
		self.window.push_handlers(self.on_mouse_drag,
		  						self.on_mouse_press,
		  						self.on_mouse_motion,
		  						self.on_mouse_release)

		# label
		self.label = pyglet.text.Label(self.name,
                          font_name=None,#'Times New Roman',
                          font_size=7,
                          x=0.0, y=0.0,
                          anchor_x='left', anchor_y='center')


	def attach_port(self, port):
		"""attach port to self"""
		if port not in self.ports:
			self.ports.append(port)
			port.attach( self )

	def draw(self):
		if not self.highlight:
			glColor4f(*self.colour)
			glPointSize(self.size)
		elif self.selected:
			glColor4f(*self.selected_colour)
			glPointSize(self.hit_size)
		else:
			glColor4f(*self.highlight_colour)
			glPointSize(self.hit_size)

		# draw
		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
    		('v2i', (self.x, self.y))
		)
		self.label.x = self.x +10
		self.label.y = self.y
		self.label.draw()

		for p in self.ports:
			p.draw()

	def on_mouse_motion( self, x, y, dx, dy ):
		if self.in_hit(x, y):
			self.highlight = True
		else:
			self.highlight = False

	def on_mouse_press(self, x, y, buttons, modifiers):
	    if buttons & mouse.LEFT:
			if self.in_hit(x, y):
				self.selected = True

	def on_mouse_release(self, x, y, button, modifiers):
	    if self.selected:
	    	self.selected = False


	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
	    if buttons & mouse.LEFT:
			if self.selected:
				self.x += dx
				self.y += dy
			else:
				pass

	def in_hit(self, x, y):
		d = utils.distance( x, y, self.x, self.y )
		return d < self.hit_size/2


class SimpleNode(Node):
	"""docstring for SimpleNode"""
	def __init__(self, *args, **kwargs):
		super(SimpleNode, self).__init__( *args, **kwargs)

		# ports
		# ports have their events pushed onto the stack
		# after its parent node
		p_spacing = 15
		self.attach_port(
				Port( name = "p1",
				x = -p_spacing,
				y = p_spacing,
				style = "in",
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		self.attach_port(
				Port( name = "p2",
				x = p_spacing,
				y = p_spacing,
				style = "in",
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		self.attach_port(
				Port( name = "p3",
				x = 0.0,
				y = -p_spacing * 1.2,
				style = "out",
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		for p in self.ports:
			p.push_handlers(self.window)
