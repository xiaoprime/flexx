""" PlotStock

The plot widget provides rudimentary plotting functionality, mostly to
demonstrate how plots can be embedded in a Flexx GUI. It may be
sufficient for simple cases, but don't expect it to ever support
log-plotting, legends, and other fancy stuff. For real plotting, see
e.g. ``BokehWidget``. There might also be a Plotly widget at some point. 


Simple example:

.. UIExample:: 200
    
    p = ui.PlotStock(xdata=range(5), ydata=[1,3,4,2,5], 
                      line_width=4, line_color='red', marker_color='',
                      minsize=200)

Also see examples: :ref:`sine.py`, :ref:`twente.py`, :ref:`monitor.py`.

"""

from ... import flx

from pscript import window

from ... import event
from ._canvas import CanvasWidget

import sys

import math

import time

import platform

if platform.system() == 'Windows':
    import ctypes

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    screenshift = 1
else:
    import AppKit

    screensize = [(int(screen.frame().size.width), int(screen.frame().size.height)) for screen in AppKit.NSScreen.screens()][0]
    screenshift = 1

class PlotSmartMS(CanvasWidget):
    """ Widget to show a plot of x vs y values. Enough for simple
    plotting tasks.
    """
    
    DEFAULT_MIN_SIZE = 300, screensize[1]*5.0/24

    background = event.DictProp({}, settable=True, doc="""

        """) 

    bandindicator = event.DictProp({}, settable=True, doc="""

        """) 

    mark = event.DictProp({}, settable=True, doc="""

        """) 

    label = event.DictProp({}, settable=True, doc="""

        """) 

    line = event.DictProp({}, settable=True, doc="""

        """)

    hint = event.DictProp({}, settable=True, doc="""

        """)

    cross = event.DictProp({}, settable=True, doc="""

        """)

    dot = event.DictProp({}, settable=True, doc="""

        """)
    
    def init(self):
        super().init()
        self._context = self.node.getContext('2d')

        self.time = time()

        self.serving = False
        self.pending = False
        

        self._last_pos = {}
        # Set mouse capturing mode
        self.set_capture_mouse(1)
        # Label to show info about the event
        #self.plotlabel = flx.Label()
    
    def create_rectangle(self, x1, y1, x2, y2, fill):
        ctx = self._context
        ctx.fillStyle = fill
        ctx.fillRect(x1, y1, x2-x1, y2-y1)

    def create_text(self, location, text, anchor='center'):
        ctx = self._context
        ctx.fillStyle = 'black'
        ctx.textAlign = anchor
        ctx.fillText(text, *location)

    def create_line(self, xs, ys, fill):
        ctx = self._context
        ctx.beginPath()
        ctx.lineWidth= 1
        ctx.strokeStyle = fill
        ctx.moveTo(xs[0], ys[0])
        for x, y in zip(xs, ys):
            ctx.lineTo(x, y)
        ctx.stroke()

    def create_hint(self, location, text, anchor='center'):
        ctx = self._context
        ctx.fillStyle = 'black'
        ctx.textAlign = anchor
        ctx.fillText(text, *location)

    def create_cross(self, crosstype, x1, y1, x2, y2, fill):
        ctx = self._context
        if crosstype == 'oval':
            ctx.beginPath()
            ctx.arc((x1+x2)/2.0, (y1+y2)/2.0, (x2-x1)/2.0, 0, 2*window.Math.PI, False)
            ctx.fillStyle = fill
            ctx.fill()
        else:
            self.create_line([x1, x2], [y1, y2], fill)

    def create_dot(self, x, y, fill):
        ctx = self._context
        ctx.beginPath()
        ctx.arc(x, y, 2, 0, 2*window.Math.PI, False)
        ctx.fillStyle = fill
        ctx.fill()

    @event.reaction('background', 'bandindicator', 'mark', 'label', 'line', 'hint', 'cross')
    def update(self, *events):
        if not self.serving:
            #print('call:'+time())
            self.serving = True
            self.pending = False
            window.requestAnimationFrame(self._update)
        else:
            #print('pending:'+time())
            self.pending = True

    def _update(self):
        w, h = self.node.clientWidth, self.node.clientHeight

        ctx = self._context
        ctx.clearRect(0, 0, w, h)

        for key, values in self.background.items():
            self.create_rectangle(*values)

        for key, values in self.bandindicator.items():
            self.create_text(*values)

        for key, values in self.mark.items():
            self.create_rectangle(*values)

        for key, values in self.label.items():
            self.create_text(*values)

        for key, values in self.line.items():
            self.create_line(*values)

        for key, values in self.hint.items():
            self.create_hint(*values)

        for key, values in self.cross.items():
            self.create_cross(*values)

        for key, values in self.dot.items():
            self.create_dot(*values)

        if self.pending:
            #print('recall')
            self.serving = True
            self.pending = False
            window.requestAnimationFrame(self._update)

        self.serving = False
 
    def show_event(self, ev):
        if -1 in ev.touches:  # Mouse
            t = 'mouse pos: {:.0f} {:.0f}  buttons: {}'
            self.plotlabel.set_text(t.format(ev.pos[0], ev.pos[1], ev.buttons))
        else:  # Touch
            self.plotlabel.set_text('Touch ids: {}'.format(ev.touches.keys()))
    
    @flx.reaction('pointer_move')
    def on_move(self, *events):
        for ev in events:
            #self.show_event(ev)
            ctx = self._context
            # Effective way to only draw if mouse is down, but disabled for
            # sake of example. Not necessary if capture_mouse == 1.
            # if 1 not in ev.buttons:
            #     return
            
            # One can simply use ev.pos, but let's support multi-touch here!
            # Mouse events also have touches, with a touch_id of -1.
            
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
            
                ctx.beginPath()
                ctx.strokeStyle = '#080'
                ctx.lineWidth = 3
                ctx.lineCap = 'round'
                ctx.moveTo(*self._last_pos[touch_id])
                ctx.lineTo(x, y)
                ctx.stroke()
                
                self._last_pos[touch_id] = x, y
    
    @flx.reaction('pointer_down')
    def on_down(self, *events):
        ctx = self._context
        for ev in events:
            #self.show_event(ev)
            
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
                
                ctx.beginPath()
                ctx.fillStyle = '#f00'
                ctx.arc(x, y, 3, 0, 6.2831)
                ctx.fill()
                
                self._last_pos[touch_id] = x, y
        
    @flx.reaction('pointer_up')
    def on_up(self, *events):
        ctx = self._context
        for ev in events:
            #self.show_event(ev)
            
            for touch_id in ev.touches:
                x, y, force = ev.touches[touch_id]
                
                ctx.beginPath()
                ctx.fillStyle = '#00f'
                ctx.arc(x, y, 3, 0, 6.2831)
                ctx.fill()
