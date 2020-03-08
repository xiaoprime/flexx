"""
Simple web app to monitor the CPU and memory usage of the server process.
Requires psutil.

This app might be running at the demo server: http://flexx1.zoof.io
"""

from time import time

from flexx import flx

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

class SmartMSView(flx.VBox):
    
    def init(self):
        self.start_time = time()
        
        #self.status = flx.Label(text='')
        self.canvas = {}
        self.canvas['nr_canvas'] = flx.PlotSmartMS(flex=1, style='width: 640px; height: 1000px;')
        self.canvas['lte_canvas'] = flx.PlotSmartMS(flex=1, style='width: 640px; height: 1000px;')
        with flx.HBox(flex=0):

            with flx.VBox(flex=1):
                self.canvas['umts_canvas'] = flx.PlotSmartMS(flex=1, style='width: 400px; height: 1000px;', minsize=(screensize[0]/5, screensize[1]*5.0/24))

                self.canvas['gsm_canvas'] = flx.PlotSmartMS(flex=1, style='width: 400px; height: 1000px;', minsize=(screensize[0]/5,screensize[1]*5.0/24))
            
            self.console = flx.TextAreaEdit(flex=2, minsize=(screensize[0]/5,100))
            self.console.set_disabled(True)
        flx.Widget(flex=1)
        self.background = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.bandindicator = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.mark = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.label = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.line = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.hint = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.cross = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

        self.dot = {'nr_canvas':{}, 'lte_canvas':{}, 'umts_canvas':{}, 'gsm_canvas':{}}

    '''
    @flx.action
    def titleas(self, title):
        print('update_title')
        # Set connections
        self.status.set_html('{}<br />'.format(title))
        
        #self.stock_plot.set_data(info.dat, info.otherseries)
    '''

    @flx.action
    def setbackground(self, canvas_name, objID, x1, y1, x2, y2, fill):
        if self.background[canvas_name].get(objID, ()) == (x1, y1, x2, y2, fill):
            return
        self.background[canvas_name].update({objID: (x1, y1, x2, y2, fill)})
        self.canvas[canvas_name].set_background(self.background[canvas_name])

    @flx.action
    def setbandindicator(self, canvas_name, objID, location, text, font):
        #TODO: font
        if self.bandindicator[canvas_name].get(objID, ()) == (location, text):
            return
        self.bandindicator[canvas_name].update({objID: (location, text)})
        self.canvas[canvas_name].set_bandindicator(self.bandindicator[canvas_name])

    @flx.action
    def setmark(self, canvas_name, objID, x1, y1, x2, y2, fill, outline):
        #TODO: outline
        if self.mark[canvas_name].get(objID, ()) == (x1, y1, x2, y2, fill):
            return
        self.mark[canvas_name].update({objID: (x1, y1, x2, y2, fill)})
        self.canvas[canvas_name].set_mark(self.mark[canvas_name])

    @flx.action
    def setlabel(self, canvas_name, objID, location, text, font, anchor):
        #TODO: font
        if self.label[canvas_name].get(objID, ()) == (location, text, anchor):
            return
        self.label[canvas_name].update({objID: (location, text, anchor)})
        self.canvas[canvas_name].set_label(self.label[canvas_name])

    @flx.action
    def setline(self, canvas_name, objID, xs, ys, fill):
        if self.line[canvas_name].get(objID, ()) == (xs, ys, fill):
            return
        self.line[canvas_name].update({objID: (xs, ys, fill)})
        self.canvas[canvas_name].set_line(self.line[canvas_name])

    @flx.action
    def sethint(self, canvas_name, objID, location, text, font, anchor):
        #TODO: font
        if self.hint[canvas_name].get(objID, ()) == (location, text, anchor):
            return
        self.hint[canvas_name].update({objID: (location, text, anchor)})
        self.canvas[canvas_name].set_hint(self.hint[canvas_name])

    @flx.action
    def setcross(self, canvas_name, objID, crosstype, x1, y1, x2, y2, fill):
        #TODO: font
        if self.cross[canvas_name].get(objID, ()) == (crosstype, x1, y1, x2, y2, fill):
            return
        self.cross[canvas_name].update({objID: (crosstype, x1, y1, x2, y2, fill)})
        self.canvas[canvas_name].set_cross(self.cross[canvas_name])

    @flx.action
    def setdot(self, canvas_name, objID, x, y, fill):
        if self.dot[canvas_name].get(objID, ()) == (x, y, fill):
            return
        self.dot[canvas_name].update({objID: (x, y, fill)})
        self.canvas[canvas_name].set_dot(self.dot[canvas_name])        

    @flx.action
    def resetline(self):
        for canvas_name in ['nr_canvas', 'lte_canvas', 'umts_canvas', 'gsm_canvas']:
            self.line[canvas_name] = {}
            self.canvas[canvas_name].set_line(self.line[canvas_name])
            self.dot[canvas_name] = {}
            self.canvas[canvas_name].set_dot(self.dot[canvas_name])

    @flx.action
    def resetcross(self):
        for canvas_name in ['nr_canvas', 'lte_canvas', 'umts_canvas', 'gsm_canvas']:
            self.cross[canvas_name] = {}
            self.canvas[canvas_name].set_cross(self.cross[canvas_name])

    @flx.action
    def resethint(self):
        for canvas_name in ['nr_canvas', 'lte_canvas', 'umts_canvas', 'gsm_canvas']:
            self.hint[canvas_name] = {}
            self.canvas[canvas_name].set_hint(self.hint[canvas_name])

    @flx.action
    def removecross(self, canvas_name, objID):
        if objID in self.cross[canvas_name]:
            del self.cross[canvas_name][objID]
            self.canvas[canvas_name].set_cross(self.cross[canvas_name])

    @flx.action
    def setconsole(self, text):
        self.console.set_disabled(False)
        self.console.set_text(self.console.text + text + '\n')
        self.console.set_disabled(True)

    @flx.action
    def resetconsole(self):
        self.console.set_disabled(False)
        self.console.set_text('')
        self.console.set_disabled(True)

if __name__ == '__main__':
    a = flx.App(SmartMSView)
    a.serve()
    m = a.launch('browser')  # for use during development
    flx.start()
