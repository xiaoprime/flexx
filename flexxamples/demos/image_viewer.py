# doc-export: VideoViewer
"""
This example demonstrates how static files can be served by making use
of a static file server.

If you intend to create a web application, note that using a static
server is a potential security risk. Use only when needed. Other options
that scale better for large websites are e.g. Nginx, Apache, or 3d party
services like Azure Storage or Amazon S3.

When exported, any links to local files wont work, but the remote links will.
"""

import os
import sys
sys.path.append(r'C:\Users\{}\Documents\GitHub\flexx'.format(os.environ['USERNAME']))
sys.path.append(r'C:\Users\{}\Documents\GitHub\flexx\flexxamples'.format(os.environ['USERNAME']))

from flexx import flx

from tornado.web import StaticFileHandler
import glob
from howtos import editor_ace, jquery
import pandas as pd

# The directory to load video's from
dirname = r'E:\rssi_mcc'
# Make use of Tornado's static file handler
tornado_app = flx.create_server().app
tornado_app.add_handlers(r".*", [
    (r"/videos/(.*)", StaticFileHandler, {"path": dirname}),
    ])

result_list = ['result_v1_0_final', 'result_v1_1_final', 'result_v1_6_final', 'result_v1_3_final']

df = {}
videos = {}
locations = {}

for sheet_name in result_list:
    df[sheet_name] = pd.read_excel(r'C:\Users\mtk13028\Desktop\{}.xlsx'.format(sheet_name))
    # Collect videos that look like they can be read in html5
    videos[sheet_name] = {}
    for index, row in df[sheet_name].iterrows():
        videos[sheet_name][row['figure'].split('\\')[-1] + '\t' + str(row['Correctness'])] = row['figure']
    locations[sheet_name] = ['ALL'] + sorted(list(set(df[sheet_name]['Location'])))

class VideoViewer(flx.PyComponent):
    """ A simple videoviewer that displays a list of videos found on the
    server's computer, plus a few online videos. Note that not all videos
    may be playable in HTML5.
    """

    def init(self):
        self.location_list = []
        self.location = {}
        self.correctness_list = []
        self.correctness = {}
        self.selector_list = []
        self.selector = {}
        self.console = {}
        self.player = {}
        self.nx = []
        for i in range(1, 12):
            self.nx.append({})

        with flx.TabLayout() as self.tabbar:
            for sheet_name in result_list:
                with flx.HBox(title=sheet_name):
                    with flx.VBox(flex=0):
                        self.location_list.append(flx.ComboBox(options=locations[sheet_name], selected_index=0, style='width: 100%'))
                        self.location[sheet_name] = self.location_list[-1]
                        self.correctness_list.append(flx.ComboBox(options=['ALL', 'False', 'True'], selected_index=0, style='width: 100%'))
                        self.correctness[sheet_name] = self.correctness_list[-1]
                        self.location[sheet_name].set_editable(True)
                        self.selector_list.append(flx.ComboBox(options=[row['figure'].split('\\')[-1] + '\t' + str(row['Correctness']) for index, row in df[sheet_name].iterrows()], selected_index=0, style='width: 100%'))
                        self.selector[sheet_name] = self.selector_list[-1]
                        self.selector[sheet_name].set_editable(True)
                        self.console[sheet_name] = flx.TextAreaEdit()
                        self.console[sheet_name].set_disabled(True)
                        flx.Widget(flex=1)

                    with flx.VBox(flex=1):
                        self.player[sheet_name] = flx.ImageWidget(flex=1)
                        with flx.HBox(flex=1):
                            self.nx[1][sheet_name] = flx.ImageWidget(flex=1)
                            self.nx[2][sheet_name] = flx.ImageWidget(flex=1)
                    with flx.VBox(flex=1):
                        with flx.HBox(flex=1):
                            self.nx[3][sheet_name] = flx.ImageWidget(flex=1)
                            self.nx[4][sheet_name] = flx.ImageWidget(flex=1)
                        with flx.HBox(flex=1):
                            self.nx[5][sheet_name] = flx.ImageWidget(flex=1)
                            self.nx[6][sheet_name] = flx.ImageWidget(flex=1)
                        with flx.HBox(flex=1):
                            self.nx[7][sheet_name] = flx.ImageWidget(flex=1)
                            self.nx[8][sheet_name] = flx.ImageWidget(flex=1)
                        with flx.HBox(flex=1):
                            self.nx[9][sheet_name] = flx.ImageWidget(flex=1)
                            self.nx[10][sheet_name] = flx.ImageWidget(flex=1)

    @flx.reaction('!tabbar.user_current')
    def tab_change(self, *events):
        flx.logger.info(str(events[0]['new_value'].title))
        flx.logger.info(self.tabbar.current.title)

    @flx.reaction('!location_list*.user_selected')
    def location_on_select(self, *events):
        flx.logger.info(events[0]['key'])
        sheet_name = self.tabbar.current.title
        correctness = self.correctness[sheet_name].selected_key
        location = events[0]['key']
        target_df = df[sheet_name]
        
        if correctness != 'ALL':
            target_df = target_df[target_df.Correctness == (correctness == 'True')]
        if location != 'ALL':
            target_df = target_df[target_df.Location == location]

        self.selector[sheet_name].set_options([row['figure'].split('\\')[-1] + '\t' + str(row['Correctness']) for index, row in target_df.iterrows()])

    @flx.reaction('!correctness_list*.user_selected')
    def correctness_on_select(self, *events):
        flx.logger.info(events[0]['key'])
        sheet_name = self.tabbar.current.title
        correctness = events[0]['key']
        location = self.location[sheet_name].selected_key
        target_df = df[sheet_name]
        
        if correctness != 'ALL':
            target_df = target_df[target_df.Correctness == (correctness == 'True')]
        if location != 'ALL':
            target_df = target_df[target_df.Location == location]

        self.selector[sheet_name].set_options([row['figure'].split('\\')[-1] + '\t' + str(row['Correctness']) for index, row in target_df.iterrows()])

    @flx.reaction('!selector_list*.user_selected')
    def on_select(self, *events):
        flx.logger.info(events[0]['key'])
        sheet_name = self.tabbar.current.title
        fname = events[0]['key']
        flx.logger.info(videos[sheet_name][fname])
        self.player[sheet_name].set_source('/videos/' + videos[sheet_name][fname])
        match_row = df[sheet_name][df[sheet_name].figure == videos[sheet_name][fname]]
        flx.logger.info(match_row['n1'].values[0])

        for i in range(1, 11):
            self.nx[i][sheet_name].set_source('/videos/' + match_row['n{}'.format(i)].values[0])

        self.console[sheet_name].set_disabled(False)
        text = ''
        for i in range(1, 11):
            text += 's{}:\t'.format(i)+match_row['n{}'.format(i)].values[0].split('.')[-3]+'\t'+str(match_row['s{}'.format(i)].values[0])+'\t'+str(match_row['b{}'.format(i)].values[0])+'\n'
        self.console[sheet_name].set_text(text)
        self.console[sheet_name].set_disabled(True)

if __name__ == '__main__':
    a = flx.App(VideoViewer)
    m = a.launch('browser')
    flx.run()
