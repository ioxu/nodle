"""beziers in pyglet"""
# based on http://pomax.github.io/bezierinfo/

import pyglet
from pyglet.gl import *
from pyglet.window import key
import node
import curves


class Application(object):
	"""docstring for App"""
	def __init__(self, *args, **kwargs):
		super(Application, self).__init__(*args, **kwargs)
		self.nodes = []
		self.edges = []
		self.window = None

		self.initialise()

		self.edge_creator = None
		self.fps_display = pyglet.clock.ClockDisplay()

	def initialise(self):
		WINDOW_CONFIG = Config(sample_buffers=1,
							samples=16,
							depth_size=16,
							double_buffer=True)
		self.window = pyglet.window.Window(config=WINDOW_CONFIG)
		# background colour
		pyglet.gl.glClearColor(0.3, 0.3, 0.3, 1)

		glEnable (GL_BLEND)
		glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


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
				x = 300,
				y = 350,
				colour = (0.5, 1, 0.5, 0.5))
				)

	def on_draw(self):
		self.window.clear()
		self.fps_display.draw()

		if self.edge_creator:
			self.edge_creator.draw()

		# nodes and edges
		for e in self.edges:
			e.draw()

		for n in self.nodes:
			n.draw()

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

# e1 = curves.Bezier( [ [0,0], [0,0], [0,0], [0,0] ], width = 20 )
# e2 = curves.Bezier( [ [0,0], [0,0], [0,0], [0,0] ], width = 20 )
e1 = app.edges.append( node.Edge( port1 = n1.ports[0], port2= n4.ports[2] ) )
e1 = app.edges.append( node.Edge( port1 = n1.ports[1], port2= n2.ports[2] ) )


app.nodes.extend([n2,n1,n3,n4])
#app.edges.extend([e1,e2])


app.run()

