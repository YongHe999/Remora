# Program to perform Data Analysis on Gcode files
# Compatible with Simplify3D gcodes 4.X
# Sample test files: midsizefile, benchy in the attachments
# Module 1: Distance traveled by the toolhead during Extrusion and Travel
# Module 2: Material usage per feature (infill, outlines etc) and Overall Material used
# Data can be obtained for the specified layer range (1 to N)

import pandas as pd
from pandas import DataFrame
import re
import math
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# to display the dataframe in one page while testing
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1500)

class Application():


    def __init__(self):

        self.inputfilepath = Path("C:/Users/Dinesh/PycharmProjects/learning/midsizefile.gcode")
        # alternate gcode files for testing: benchy_simple.gcode

        self.startlayer = 1        # must be greater than 1
        self.endlayer = 50         # enter a large number like 999999 if you want to go until the end

        # regex codes to extract different types of Gcode lines
        self.gepattern = re.compile(r"G1\sX\d+\.\d+\sY\d+\.\d+\sE\d+\.\d+")
        self.gonepattern = re.compile(r"G1\sX\d+\.\d+\sY\d+\.\d+\sE\d+\.\d+\sF\d+")
        self.gtrpattern = re.compile(r"G1\sX\d+\.\d+\sY\d+\.\d+\sF\d+")
        self.ftpattern = re.compile(r";\sfeature\s\w+")
        self.layerpattern = re.compile(r";\slayer\s")
        self.toolcompattern = re.compile(r";\stool\s")
        self.resetextpattern = re.compile(r"G92\sE0")
        self.zpattern = re.compile(r"G1\sZ\d+\.\d+")

        # Dataframe to store the gcode lines
        self.tablelist = []
        self.newdataframe = DataFrame(columns=['Xc', 'Yc', 'Zc', 'E', 'F', 'FT', 'EW', 'LH', 'Layer'])

        # initializing column variables
        self.gc_summary_dt = {}
        self.ft_var = str
        self.tc_ew = 0.0
        self.tc_lh = 0.0
        self.gc_z = 0.0
        self.cmt_layer = int

        # ------------- Program execution begins --------------- #

        # parse the gcode into a dataframe
        self.gcodetodf()

        # Module 1: uncomment to calculate the distance traveled
        self.distancetraveled()
        self.distanceGraphs()

        # Module 2: uncomment to calculate the extrusion amounts for each feature
        # self.extByFeature()
        # self.extrusionGraphs()

    def gc_g1xyef(self):
        self.tablelist.append({'Xc': float(self.tlist[1][1:]), 'Yc': float(self.tlist[2][1:]), 'Zc': self.gc_z,
             'E': float(self.tlist[3][1:]), 'F': float(self.tlist[4][1:]),
             'FT': self.ft_var, 'EW': self.tc_ew, 'LH': self.tc_lh, 'Layer': self.cmt_layer})

    def gc_g1xye(self):
        self.tablelist.append({'Xc': float(self.tlist[1][1:]), 'Yc': float(self.tlist[2][1:]), 'Zc': self.gc_z,
             'E': float(self.tlist[3][1:]), 'F': None, 'FT': self.ft_var, 'EW': self.tc_ew,
             'LH': self.tc_lh, 'Layer': self.cmt_layer})

    def gc_g1xyf(self):
        self.tablelist.append({'Xc': float(self.tlist[1][1:]), 'Yc': float(self.tlist[2][1:]),
                               'Zc': self.gc_z, 'E': None, 'F': float(self.tlist[3][1:]),
                               'FT': self.ft_var, 'EW': self.tc_ew, 'LH': self.tc_lh, 'Layer': self.cmt_layer})

    def gc_g92e0(self):
        if self.tablelist:
            self.tablelist.append({'Xc': self.tablelist[-1]['Xc'], 'Yc': self.tablelist[-1]['Yc'],
                 'Zc': self.gc_z, 'E': 0.0, 'F': None, 'FT': self.ft_var, 'EW': self.tc_ew, 'LH': self.tc_lh,
                 'Layer': self.cmt_layer})
        else:
            return

    def gc_ftype(self):
        self.ft_var = self.clist[3]

    def gc_laycmt(self):
        self.cmt_layer = float(self.tlist[2][:-1])

    def gc_toolcmt(self):
        self.tc_ew = float(self.tlist[3][1:])
        self.tc_lh = float(self.tlist[2][1:-1])

    def gc_g1z(self):
        self.gc_z = float(self.tlist[1][1:])

    def contd(self):
        return

    def gcodetodf(self):

        with open(self.inputfilepath, 'r') as ifile:

            lflag = False
            for item in ifile:

                layermatch = self.layerpattern.match(item)
                self.tlist = item.split(' ')
                self.clist = re.split(r"(\w+)", item)

                if layermatch and (str(self.tlist[2][:-1]) == 'end' or int(self.tlist[2][:-1]) == (self.endlayer + 1)):
                    break

                if (layermatch and int(self.tlist[2][:-1]) == self.startlayer) or lflag is True:
                    lflag = True
                    # clist = re.split(r"(\w+)", item)

                    map_gcpat = {bool(self.gonepattern.match(item)): self.gc_g1xyef,
                                 bool(self.gepattern.match(item)): self.gc_g1xye,
                                 bool(self.gtrpattern.match(item)): self.gc_g1xyf,
                                 bool(self.resetextpattern.match(item)): self.gc_g92e0,
                                 bool(self.ftpattern.match(item)): self.gc_ftype,
                                 bool(self.toolcompattern.match(item)): self.gc_toolcmt,
                                 bool(self.layerpattern.match(item)): self.gc_laycmt,
                                 bool(self.zpattern.match(item)): self.gc_g1z}

                    map_gcpat.get(True, self.contd)()

        self.newdataframe = pd.DataFrame(self.tablelist)

        # purge the list as it is no longer required
        del self.tablelist[:]

        # for testing purposes
        # print(self.newdataframe)

    def distancetraveled(self):

        self.dist_total = 0.0
        self.dist = {'extrusion': 0.0, 'travel': 0.0}

        for i, row in self.newdataframe.iterrows():

            if i < 1:
                # skip the first line as there is no previous coordinate to calculate from
                # print(self.newdataframe.iloc[i]['E'])
                continue

            self.distance_tup = (pd.isnull(self.newdataframe.iloc[i]['E']), pd.isnull(self.newdataframe.iloc[i-1]['E']))

            # distance between 2 points formula
            edist = math.sqrt(math.pow((row['Xc']-self.newdataframe.iloc[i-1]['Xc']), 2)
                              + math.pow((row['Yc']-self.newdataframe.iloc[i-1]['Yc']), 2))
            self.dist_total += edist

            # categorize into travel and extrusion based on the current and previous E values
            if self.distance_tup in ((False, False), (False, True)):
                self.dist['extrusion'] += edist
            elif self.distance_tup in ((True, True), (True, False)):
                self.dist['travel'] += edist

        print(f'Total extrusion distance: ', float(format(self.dist['extrusion'], '.4f')), 'mm')
        print(f'Total travel distance: ', float(format(self.dist['travel'], '.4f')), 'mm')
        print(f'Total distance traveled by the Toolhead: ', float(format(self.dist_total, '.4f')), 'mm')

    def distanceGraphs(self):

        ax = sns.barplot(x=['Travel', 'Extrusion'], y=[self.dist['travel'], self.dist['extrusion']],
                         palette=None)
        ax.set(xlabel='Movement Type', ylabel='Distance Traveled (mm)')
        plt.subplots_adjust(left=0.15, bottom=0.15)
        plt.show(block=True)

    def extByFeature(self):

        self.map_ext = {'outer': 0.0, 'inner': 0.0, 'solid': 0.0, 'infill': 0.0, 'gap': 0.0,
                        'support': 0.0, 'skirt': 0.0, 'raft': 0.0, 'prime': 0.0, 'ooze': 0.0,
                        'other': 0.0}

        self.ext_total = 0.0
        self.ftypes = [x for x in self.map_ext.keys() if x != 'other']

        for i, row in self.newdataframe.iterrows():

            if i < 1 is True or pd.isnull(self.newdataframe.iloc[i]['E']) is True or self.newdataframe.iloc[i]['E'] == 0:
                continue

            edist = self.newdataframe.iloc[i]['E'] - self.newdataframe.iloc[i - 1]['E']
            self.ext_total += edist
            self.map_ext[self.newdataframe.iloc[i]['FT'] if self.newdataframe.iloc[i]['FT'] in self.ftypes else 'other'] += edist

        print(f'outline extrusion amount: ', float(format((self.map_ext['outer'] + self.map_ext['inner']), '.4f')), 'mm')
        print(f'infill extrusion amount: ', float(format(self.map_ext['infill'], '.4f')), 'mm')
        print(f'support extrusion amount: ', float(format(self.map_ext['support'], '.4f')), 'mm')
        print(f'solid layer extrusion amount: ', float(format(self.map_ext['solid'], '.4f')), 'mm')
        print(f'other extrusion amount: ', float(format(self.map_ext['other'], '.4f')), 'mm')
        print(f'total extrusion amount: ', float(format(self.ext_total, '.4f')), 'mm')

    def extrusionGraphs(self):

        total_outlines = self.map_ext['outer'] + self.map_ext['inner']
        total_infill = self.map_ext['infill'] + self.map_ext['gap']
        total_additions = self.map_ext['prime'] + self.map_ext['ooze'] + self.map_ext['skirt'] + \
                          self.map_ext['support'] + self.map_ext['raft']

        self.materialusage = {'Outlines': total_outlines, 'Solid Layers': self.map_ext['solid'],
                              'Infill': total_infill, 'Support Structures': self.map_ext['support'],
                              'Skirt/Brim': self.map_ext['skirt'], 'Raft': self.map_ext['raft'],
                              'Prime Pillar': self.map_ext['prime'], 'Ooze Shield': self.map_ext['ooze'],
                              'other': self.map_ext['other']}

        fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(aspect="equal"))

        pieslices = [float(x) for x in self.materialusage.values() if x > 0.0]
        piekeys = [x for x in self.materialusage.keys() if self.materialusage[x] > 0.0]
        pieshares= [(a*100)/self.ext_total for x, a in self.materialusage.items() if a > 0.0]
        pielabels = ['{0:1.1f}% {1}'.format(x, y) for x, y in zip(pieshares, piekeys)]

        plt.style.use('seaborn-deep')

        wedges, texts = ax.pie(pieslices, wedgeprops=dict(width=0.5), startangle=45)

        bbox_props = dict(boxstyle="square,pad=0.5", fc="w", ec="grey", lw=0.5)
        kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(pielabels[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                        horizontalalignment=horizontalalignment, **kw)

        ax.set_title("Material usage per feature", pad=-1.0)
        ax.title.set_position([.5, 1.1])

        plt.subplots_adjust(top=0.85, bottom=0.1)
        plt.show(block=True)


app = Application()
