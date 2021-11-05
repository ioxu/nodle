"""directed node graphs"""

from pyglet.gl import *
from pyglet.window import mouse
import utils, curves

# port constants
PORTDIRECTION_INPUT = 0
PORTDIRECTION_OUTPUT = 1
PORTDIRECTION_ADIRECTED = 2


class Edge_Creator(object):
	"""docstring for Edge_Creator"""
	def __init__(self, port_from = None, application = None):
		super(Edge_Creator, self).__init__()
		self.port_from = port_from
		self.application = application
		self.window = application.window
		self.window.push_handlers(self)
		self.bezier = curves.Bezier( [ [0,0], [0,0], [0,0], [0,0] ], width = 5 )
		self.candidates = None
		print(self, "init", "DRAG")

		# find candidates to drop onto (implicitly avoids dropping onto port_from)
		# get ports
		ports = [p for n in self.application.nodes for p in n.ports]
		# remove ports on same parent node
		ports = [p for p in ports if p not in self.port_from.parent.ports]
		
		# find candidate drop ports
		if self.port_from.style == PORTDIRECTION_INPUT:
			self.candidates = [p for p in ports if p.style == PORTDIRECTION_OUTPUT ]
		
		if self.port_from.style == PORTDIRECTION_OUTPUT:
			self.candidates = [p for p in ports if p.style == PORTDIRECTION_INPUT ]

		if self.port_from.style == PORTDIRECTION_ADIRECTED:
			self.candidates = [p for p in ports if p.style == PORTDIRECTION_ADIRECTED ]

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		
		if self.port_from.style == PORTDIRECTION_OUTPUT:
			self.bezier.update( [ x, y ],
								[self.port_from.absx,
								self.port_from.absy] )
		
		elif self.port_from.style == PORTDIRECTION_INPUT:
			self.bezier.update([self.port_from.absx,
								self.port_from.absy],
								[ x, y ])
		
		elif self.port_from.style == PORTDIRECTION_ADIRECTED:
			self.bezier.update([self.port_from.absx,
								self.port_from.absy],
								[ x, y ])


	def on_mouse_release(self, x, y, button, modifiers):
		print(self, "on_mouse_release", "DROP")
		for p in self.candidates:
			if p.in_hit(x,y):
				edge = self.port_from.connect( p )

		# destroy self
		self.remove()


	def remove(self):
		print("destroying", self)
		self.window.pop_handlers()
		self.bezier = None
		del(self)
		#print(self)

	def draw(self):
		if self.bezier:
			self.bezier.draw(hull=False)

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
		print(self, "REMOVE")
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
			colour = (0.39,0.39,0.39,1), #(0.5,0.5,0.5,0.5),
			parent = None,
			style = PORTDIRECTION_INPUT,
			window = None,
			tangent_v = (0.0, 1.0, 0.0), # outgoing edge vector
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

		# remove existing edge on PORTDIRECTION_INPUT port if one exists
		if port.edge and port.style == PORTDIRECTION_INPUT:
			port.disconnect()

		# connect ports
		if self.style == PORTDIRECTION_INPUT and port.style == PORTDIRECTION_OUTPUT :
			self.edge = Edge( port1 = self, port2 = port )
			port.edge = self.edge
		
		elif self.style == PORTDIRECTION_OUTPUT and port.style == PORTDIRECTION_INPUT:
			self.edge = Edge( port1 = port, port2 = self )
			port.edge = self.edge
		
		elif self.style == PORTDIRECTION_ADIRECTED and port.style == PORTDIRECTION_ADIRECTED:
			print("ADIRECTED on ADIRECTED")
			self.edge = Edge( port1 = port, port2 = self )
			port.edge = self.edge

		print(port.edge, "port.edge")
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
		if self.in_hit(x, y):
			self.highlight = True
		else:
			self.highlight = False

	def on_mouse_press(self, x, y, buttons, modifiers):
		if buttons & mouse.LEFT:
			if self.in_hit(x, y):
				self.selected = True
				
				print(self, "drag init")
				self.parent.parent.create_edge(self)

	def on_mouse_release(self, x, y, button, modifiers):
		if self.selected:
			self.selected = False
			self.highlight = False
			print(self, "on_mouse_release")

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		if self.in_hit(x, y):
			self.highlight = True
		else:
			self.highlight = False

		if buttons & mouse.LEFT:
			if self.selected:
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

				# consume to avoid other nodes recieving select
				return True

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


# concrete implementations

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
				style = PORTDIRECTION_INPUT,
				tangent_v = (0.0, 1.0, 0.0),
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		self.attach_port(
				Port( name = "p2",
				x = p_spacing,
				y = p_spacing,
				style = PORTDIRECTION_INPUT,
				tangent_v = (0.0, 1.0, 0.0),
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		self.attach_port(
				Port( name = "p3",
				x = 0.0,
				y = -p_spacing * 1.2,
				style = PORTDIRECTION_OUTPUT,
				tangent_v = (0.0, -1.0, 0.0),
				window = self.window,
				parent = kwargs["parent"]
				)
				)

		adp_size = 5
		self.attach_port(
				Port( name = "p4",
				x = -p_spacing * 1.2,
				y = 0.0,
				size = adp_size,
				style = PORTDIRECTION_ADIRECTED,
				tangent_v = (-1.0, 0.0, 0.0),
				window = self.window,
				parent = kwargs["parent"]
				)
				)


		for p in self.ports:
			p.push_handlers(self.window)
