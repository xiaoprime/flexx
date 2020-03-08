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

import datetime

class PlotStock(CanvasWidget):
    """ Widget to show a plot of x vs y values. Enough for simple
    plotting tasks.
    """
    
    DEFAULT_MIN_SIZE = 300, 500
    
    dat = event.DictProp({}, doc="""
            A list of values for the x-axis. Set via the ``set_data()`` action.
            """)
    
    otherseries = event.ListProp([], doc="""
            A list of values for the y-axis. Set via the ``set_data()`` action.
            """)
    
    @event.action
    def set_data(self, dat, otherseries):
        """ Set the xdata and ydata.
        """
        '''
        xdata = [float(i) for i in xdata]
        ydata = [float(i) for i in ydata]
        if len(xdata) != len(ydata):
            raise ValueError('xdata and ydata must be of equal length.')
        '''
        self._mutate('dat', dat)
        self._mutate('otherseries', otherseries)
        
    yrange = event.FloatPairProp((0, 0), settable=True, doc="""
        The range for the y-axis. If (0, 0) (default) it is determined
        from the data.
        """)
    
    line_color = event.ColorProp('#5af', settable=True, doc="""
        The color of the line. Set to the empty string to hide the line.
        """)
    
    marker_color = event.ColorProp('#5af', settable=True, doc="""
        The color of the marker. Set to the empty string to hide the marker.
        """)
    
    line_width = event.FloatProp(2, settable=True, doc="""
        The width of the line, in pixels.
        """)
    
    marker_size = event.FloatProp(6, settable=True, doc="""
        The size of the marker, in pixels. 
        """)
    
    xlabel = event.StringProp('', settable=True, doc="""
        The label to show on the x-axis.
        """)
    
    ylabel = event.StringProp('', settable=True, doc="""
        The label to show on the y-axis.
        """)
    
    def init(self):
        super().init()
        self._context = self.node.getContext('2d')
        
        # create tick units
        self._tick_units = []
        for e in range(-10, 10):
            for i in [10, 20, 25, 50]:
                self._tick_units.append(i*10**e)
    
    
    @event.reaction('dat', 'otherseries', 'yrange', 'line_color', 'line_width',
                    'marker_color', 'marker_size', 'xlabel', 'ylabel',
                    'title', 'size')
    def update(self, *events):
        window.requestAnimationFrame(self._update)

    def _update(self):
        #raise SyntaxError('for debug')
        if 'index' not in self.dat:
            return
        if 'rec' not in self.dat:
            return

        xx, yy = self.dat['index'], self.dat['rec']['Close']
        yrange = self.yrange
        lc, lw = self.line_color, self.line_width
        mc, ms = self.marker_color, self.marker_size
        title, xlabel, ylabel = self.title, self.xlabel, self.ylabel
            
        # Prepare
        ctx = self._context
        w, h = self.node.clientWidth, self.node.clientHeight
        
        # Get range
        x1, x2 = self.dat['min']['index'], self.dat['max']['index']
        #
        if xx:
            x1 -= (x2-x1) * 0.02
            x2 += (x2-x1) * 0.02
        else:
            x1, x2 = 0, 1

        all_data = []
        for data_type in ['Open', 'Close', 'High', 'Low']+self.otherseries:
            all_data.append(self.dat['min'][data_type])
            all_data.append(self.dat['max'][data_type])

        y1, y2 = min(all_data), max(all_data)
        #
        y1 -= (y2-y1) * 0.02
        y2 += (y2-y1) * 0.02

        # Convert to screen coordinates
        # 0.5 offset so we land on whole pixels with axis
        lpad = rpad = bpad = tpad = 25.5
        lpad += 30
        bpad += 50
        if title:
            tpad += 10
        if xlabel:
            bpad += 20
        if ylabel:
            lpad += 20
        scale_x = (w-lpad-rpad) / (x2-x1)
        scale_y = (h-bpad-tpad) / (y2-y1)
        sxx = [lpad + (x-x1)*scale_x for x in xx]
        syy = [bpad + (y-y1)*scale_y for y in yy]
        
        # Define ticks
        #x_ticks = self._get_ticks(scale_x, x1, x2)
        x_ticks = self.dat['label']
        y_ticks = self._get_ticks(scale_y, y1, y2)
        sx_ticks = [lpad + (x-x1)*scale_x for x in xx]
        sy_ticks = [bpad + (y-y1)*scale_y for y in y_ticks]
        
        ctx.clearRect(0, 0, w, h)
        
        # Draw inner background
        ctx.fillStyle = 'white'
        ctx.fillRect(lpad, tpad, w-lpad-rpad, h-bpad-tpad)
        
        # Draw ticks
        ctx.beginPath()
        ctx.lineWidth= 1
        ctx.strokeStyle = "#444"
        for sx in sx_ticks:
            ctx.moveTo(sx, h-bpad)
            ctx.lineTo(sx, h-bpad+5)
        for sy in sy_ticks:
            ctx.moveTo(lpad, h-sy)
            ctx.lineTo(lpad-5, h-sy)
        ctx.stroke()
        
        # Draw gridlines
        ctx.beginPath()
        ctx.lineWidth= 1
        ctx.setLineDash([2, 2])
        ctx.strokeStyle = "#ccc"
        for sx in sx_ticks:
            ctx.moveTo(sx, h-bpad)
            ctx.lineTo(sx, tpad)
        for sy in sy_ticks:
            ctx.moveTo(lpad, h-sy)
            ctx.lineTo(w-rpad, h-sy)
        ctx.stroke()
        ctx.setLineDash([])
        
        # Draw tick labels
        ctx.font = '11px verdana'
        ctx.fillStyle = 'black'
        ctx.textAlign = "center"
        ctx.textBaseline = 'top'
        ctx.rotate(-window.Math.PI/2);
        for x, sx in zip(x_ticks, sx_ticks):
            ctx.fillText(x, -(h-bpad+40), sx-7)
        ctx.rotate(window.Math.PI/2);
        ctx.textAlign = "end"
        ctx.textBaseline = 'middle'
        for y, sy in zip(y_ticks, sy_ticks):
            ctx.fillText(round(y*100)/100, lpad-8, h-sy)
        
        # Draw labels
        ctx.textAlign = "center"
        if title:
            ctx.font = '20px verdana'
            ctx.textBaseline = 'top'
            ctx.fillText(title, w/2, 5)
        if xlabel:
            ctx.font = '16px verdana'
            ctx.textBaseline = 'bottom'
            ctx.fillText(xlabel, w/2, h-5)
        if ylabel:
            ctx.save()
            ctx.translate(0, h/2)
            ctx.rotate(-window.Math.PI/2)
            ctx.textBaseline = 'top'
            ctx.fillText(ylabel, 0, 5)
            ctx.restore()
        
        # Draw axis
        ctx.beginPath()
        ctx.lineWidth= 1
        ctx.strokeStyle = "#444"
        ctx.moveTo(lpad, tpad)
        ctx.lineTo(lpad, h-bpad)
        ctx.lineTo(w-rpad, h-bpad)
        ctx.stroke()
        
        '''
        # Draw line
        if lc.alpha and lw:
            ctx.beginPath()
            ctx.lineWidth= lw
            ctx.strokeStyle = lc.css
            ctx.moveTo(sxx[0], h-syy[0])
            for x, y in zip(sxx, syy):
                ctx.lineTo(x, h-y)
            ctx.stroke()

        # Draw markers
        if mc.alpha and ms:
            ctx.fillStyle = mc.css
            for x, y in zip(sxx, syy):
                ctx.beginPath()
                ctx.arc(x, h-y, ms/2, 0, 2*window.Math.PI)
                ctx.fill()
        '''

        self._candlestick(ctx, w, h, x1, y1, scale_x, scale_y, lpad, rpad, bpad, tpad)

        ### for debug ###
        #ctx.fillText(y2, 200, 20)
        #ctx.fillText(y1, 200, 10)
        ###
    
    def _get_ticks(self, scale, t1, t2, min_tick_dist=40):
        # Get tick unit
        for tick_unit in self._tick_units:
            if tick_unit * scale >= min_tick_dist:
                break
        else:
            return []
        # Calculate tick values
        first_tick = window.Math.ceil(t1 / tick_unit) * tick_unit
        last_tick = window.Math.floor(t2 / tick_unit) * tick_unit
        ticks = []
        t = first_tick
        while t <= last_tick:
            ticks.append(t)
            t += tick_unit
        '''
        for i in range(len(ticks)):
            t = ticks[i].toPrecision(4)
            if '.' in t:
                t = t.replace(window.RegExp("[0]+$"), "")
            if t[-1] == '.':    
                t += '0'
            ticks[i] = t
        '''
            
        return ticks

    def _candlestick(ctx, w, h, x1, y1, scale_x, scale_y, lpad, rpad, bpad, tpad, \
                     width=0.5, colorup='#FF0000', colordown='#00FF00', alpha=1.0):
        
        OFFSET = width / 2.0

        scale_dat = {}

        scale_dat['index'] = [lpad + (x-x1)*scale_x for x in self.dat['index']]

        for data_type in ['Open', 'Close', 'High', 'Low']+self.otherseries:
            scale_dat[data_type] = [bpad + (y-y1)*scale_y for y in self.dat['rec'][data_type]]

        lines = []
        patches = []

        for t, open, close, high, low in zip(scale_dat['index'], \
                                             scale_dat['Open'], \
                                             scale_dat['Close'], \
                                             scale_dat['High'], \
                                             scale_dat['Low']):

            if close >= open:
                color = colorup
                higher = close
                height = close - open
            else:
                color = colordown
                higher = open
                height = open - close
            '''
            vline = Line2D(
                xdata=(t, t), ydata=(low, high),
                color=color,
                linewidth=0.5,
                antialiased=True,
            )
            '''
            ctx.beginPath()
            ctx.moveTo(t, h-high)
            ctx.lineTo(t, h-low)
            ctx.strokeStyle = '#000000'
            ctx.stroke()

            '''
            rect = Rectangle(
                xy=(t - OFFSET, lower),
                width=width,
                height=height,
                facecolor=color,
                edgecolor=color,
            )
            '''
            ctx.fillStyle=color
            ctx.fillRect(t-OFFSET*scale_x, h-higher, width*scale_x, height)
            
            '''
            rect.set_alpha(alpha)
    
            lines.append(vline)
            patches.append(rect)
            ax.add_line(vline)
            ax.add_patch(rect)
            ''' 
        color = ['red', 'green', 'blue']
        color_idx = 0
        for tp in self.otherseries:
            first = True
            ctx.beginPath()
            ctx.lineWidth= 2
            ctx.strokeStyle = color[color_idx]
            color_idx = (color_idx + 1) % len(color)
            for t, avgline in zip(scale_dat['index'], scale_dat[tp]):
                if not (isinstance(avgline, float) or isinstance(avgline, int)):
                    continue
                if first:
                    ctx.moveTo(t, h-avgline)
                    first = False
                ctx.lineTo(t, h-avgline)
                ctx.stroke()

