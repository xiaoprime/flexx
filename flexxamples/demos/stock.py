"""
Simple web app to monitor the CPU and memory usage of the server process.
Requires psutil.

This app might be running at the demo server: http://flexx1.zoof.io
"""

from time import time

from flexx import flx

class StockView(flx.VBox):
    
    def init(self):
        self.start_time = time()
        
        self.status = flx.Label(text='')
        self.stock_plot = flx.PlotStock(flex=1, style='width: 640px; height: 320px;',
                                       dat={}, 
                                       otherseries=[])
    
    @flx.action
    def update_info(self, info):
        print('update_info')
        # Set connections
        n = info.sessions, info.total_sessions
        self.status.set_html(#'{}<br />'.format(n[0]) +
                             #'And in total we served %i connections.<br />' % n[1] +
                             '{}<br />'.format(info.stockname))
        
        self.stock_plot.set_data(info.dat, info.otherseries)

if __name__ == '__main__':
    a = flx.App(Monitor)
    a.serve()
    m = a.launch('browser')  # for use during development
    flx.start()
