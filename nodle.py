"""node graphs in pyglet"""
# based on http://pomax.github.io/bezierinfo/

import pyglet
from pyglet.gl import *
from pyglet.window import key
import node
import curves

class Mouse(object):
	"""docstring for Mouse"""
	def __init__(self):
		super(Mouse, self).__init__()
		self.x = 0.0
		self.y = 0.0
		self.dx = 0.0
		self.dy = 0.0

		self.colour = (1, 0.75, 0.2, 0.65)
		self.size = 5

	def update(self, x, y, dx = 0.0, dy = 0.0):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

class Application(object):
	"""docstring for App"""
	def __init__(self, *args, **kwargs):
		super(Application, self).__init__(*args, **kwargs)
		self.nodes = []
		self.edges = []
		self.window = None

		self.initialise()

		self.edge_creator = None
		#self.fps_display = pyglet.clock.ClockDisplay()
		self.fps_display = pyglet.window.FPSDisplay(self.window)

		self.mouse = Mouse()

	def initialise(self):
		"""initialises app and window configuration"""
		# window config
		WINDOW_CONFIG = Config(sample_buffers=1,
							samples=16,
							depth_size=16,
							double_buffer=True,
							)
		
		# window
		self.window = pyglet.window.Window(config=WINDOW_CONFIG, resizable=True)
		self.window.set_size(1024, 600)
		self.window.set_mouse_visible(False)

		# background colour
		#pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)
		pyglet.gl.glClearColor(0.2, 0.2, 0.2, 1)

		glEnable (GL_BLEND)
		glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		# events
		if self.window:
			print("subscribing %s to %s's events"%(self, self.window))
			self.window.push_handlers(self)

	def run(self):
		pyglet.app.run()

	def on_key_press(self, symbol, modifiers):
		if symbol == key.A:
			self.nodes.append(
				node.SimpleNode(name = "nadd",
				window = app.window,
				parent = app,
				size = 15,
				x = self.mouse.x,
				y = self.mouse.y,
				colour = (0.5, 1, 0.5, 0.5))
				)

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse.update(x,y,dx,dy)

	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		self.mouse.update(x,y,dx,dy)

	def on_draw(self):
		self.window.clear()
		self.fps_display.draw()

		if self.edge_creator:
			self.edge_creator.draw()

		# nodes and edges
		# loop nodes, draw edges on input ports
		ports = [p for n in self.nodes for p in n.ports]
		ports = [p for p in ports if p.style == node.PORTDIRECTION_INPUT or p.style == node.PORTDIRECTION_ADIRECTED]
		edges = [p.edge for p in ports if p.edge ]
		for e in edges:
			e.draw()

		for n in self.nodes:
			n.draw()

		# mouse
		glColor4f(*self.mouse.colour)
		glPointSize(self.mouse.size)

		pyglet.graphics.draw(1, pyglet.gl.GL_POINTS,
							('v2f', (self.mouse.x, self.mouse.y))
							)

	def create_edge(self, pfrom):
		"""interactive edges creator"""
		print(self, "create_edge", pfrom)
		self.edge_creator = node.Edge_Creator(port_from = pfrom, application = self)

###################
app = Application()
###################

# nodes and edges

n1 = node.SimpleNode(name = "n1",
		window = app.window,
		parent = app,
		size = 15,
		x = 100,
		y = 100,
		colour = (0.5, 1, 0.5, 0.5))

n2 = node.SimpleNode(name = "n2",
		window = app.window,
		parent = app,
		size = 15,
		x = 300,
		y = 300,
		colour = (0.5, 1, 0.5, 0.5))

n3 = node.SimpleNode(name = "n3",
		window = app.window,
		parent = app,
		size = 15,
		x = 500,
		y = 400,
		colour = (0.5, 1, 0.5, 0.5))

n4 = node.SimpleNode(name = "n4",
		window = app.window,
		parent = app,
		size = 15,
		x = 50,
		y = 350,
		colour = (0.5, 1, 0.5, 0.5))

app.nodes.extend([n2,n1,n3,n4])


app.run()

