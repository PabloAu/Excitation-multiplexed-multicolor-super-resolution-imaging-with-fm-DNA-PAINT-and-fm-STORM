# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 13:25:45 2017

@author: egarbacik
"""

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as ttkfd
import importlib
import os
import unified_demod_localize as udl

class App:
    def __init__(self, parent):
        self.parent = parent
        self.initdir = '.'

        self.block_size = 6
        self.lasers = [False, True, True]

    def constructGUI(self):
        self.mainFrame = ttk.Frame(self.parent, padding=(5,5,5,5))
        self.secondMainFrame = ttk.Frame(self.parent, padding=(5,5,5,5))

        self.constructSubFrames()
        self.constructInterface()
        self.constructGrid()

        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]

        self.localizer = udl.DemodLocalizer(lasers, int(2*self.n_lasers))
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])

    def constructSubFrames(self):
        # Set up the individual application frames
        self.frameOne = ttk.Frame(self.mainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
#        self.frameOne.bind('<Button-3>', lambda e:self.get_file_list(self.strDataName.get()))
        self.frameTwo = ttk.Frame(self.mainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
        self.frameThree = ttk.Frame(self.mainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
        self.frameFour = ttk.Frame(self.mainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
        self.frameFive = ttk.Frame(self.mainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
        self.frameSix = ttk.Frame(self.secondMainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))
        self.frameSeven = ttk.Frame(self.secondMainFrame,
                            borderwidth=5,
                            relief='ridge',
                            padding=(5,5,5,5))

    def constructInterface(self):
        # Build the directory and filename interfaces
        self.spinNumBins = tk.Spinbox(self.frameOne,
                                   from_=1,
                                   to=4,
                                   width=4,
                                   state='readonly',
                                   command=lambda:self.spinNumBinsClick('<Button-1>'))
        self.n_lasers = int(self.spinNumBins.get())
        self.labelDataDir = ttk.Label(self.frameOne, text='Data directory')
        self.strDataDir = tk.StringVar()

        self.labelSpecCalDirs = [ttk.Label(self.frameSix, text='SPECTRAL calibration directory '+str(i+1)) for i in range(4)]
        self.strSpecCalDirs = [tk.StringVar() for i in range(4)]
        self.labelZCalDirs = [ttk.Label(self.frameSeven, text='Z-POSITION calibration directory '+str(i+1)) for i in range(4)]
        self.strZCalDirs = [tk.StringVar() for i in range(4)]

        self.app_dir = os.listdir('.')
        if 'config.cfg' in self.app_dir:
            f = open('config.cfg', 'r')
            for line in f:
                vals = line.split('=')
                if vals[0].strip() == 'data directory':
                    initdir = vals[1].strip()
                    self.strDataDir.set(initdir)
                elif vals[0].strip() == 'cal1dye directory':
                    initdir = vals[1].strip()
                    self.strSpecCalDirs[0].set(initdir)
                elif vals[0].strip() == 'cal2dye directory':
                    initdir = vals[1].strip()
                    self.strSpecCalDirs[1].set(initdir)
                elif vals[0].strip() == 'cal3dye directory':
                    initdir = vals[1].strip()
                    self.strSpecCalDirs[2].set(initdir)
                elif vals[0].strip() == 'cal4dye directory':
                    initdir = vals[1].strip()
                    self.strSpecCalDirs[3].set(initdir)
                elif vals[0].strip() == 'cal1z directory':
                    initdir = vals[1].strip()
                    self.strZCalDirs[0].set(initdir)
                elif vals[0].strip() == 'cal2z directory':
                    initdir = vals[1].strip()
                    self.strZCalDirs[1].set(initdir)
                elif vals[0].strip() == 'cal3z directory':
                    initdir = vals[1].strip()
                    self.strZCalDirs[2].set(initdir)
                elif vals[0].strip() == 'cal4z directory':
                    initdir = vals[1].strip()
                    self.strZCalDirs[3].set(initdir)
        else:
            self.buttonDirClick('<Button-1>')
            self.initdir = self.strDataDir.get()
            f = open('config.cfg', 'w')
            f.writelines('default directory = ' + self.strDataDir.get())
        self.entryDataDir = ttk.Entry(self.frameOne,
                                    textvariable=self.strDataDir,
                                    width=85)

        self.strDataName = tk.StringVar()
        self.labelDataName = ttk.Label(self.frameOne, text='Data file')
        self.comboDataName = ttk.Combobox(self.frameOne,
                            textvariable = self.strDataName,
                            width=82)
        self.comboDataName['values'] = self.get_file_list(self.strDataDir.get())
        self.strDataName.set(self.comboDataName['values'][0])

        self.entrySpecCalDirs = [ttk.Entry(self.frameSix,
                                       textvariable=self.strSpecCalDirs[i],
                                       width=85) for i in range(4)]

        self.labelSpecCalNames = [ttk.Label(self.frameSix, text='SPECTRAL calibration file '+str(i+1)) for i in range(4)]
        self.strSpecCalNames = [tk.StringVar() for i in range(4)]
        self.comboSpecCalNames = [ttk.Combobox(self.frameSix,
                                       textvariable=self.strSpecCalNames[i],
                                       width=82) for i in range(4)]
        for i in range(4):
            self.comboSpecCalNames[i]['values'] = self.get_file_list(self.strSpecCalDirs[i].get())
            self.strSpecCalNames[i].set(self.comboSpecCalNames[i]['values'][0])
            ###
        self.entryZCalDirs = [ttk.Entry(self.frameSeven,
                                       textvariable=self.strZCalDirs[i],
                                       width=85) for i in range(4)]

        self.labelZCalNames = [ttk.Label(self.frameSeven, text='Z-POSITION calibration file '+str(i+1)) for i in range(4)]
        self.strZCalNames = [tk.StringVar() for i in range(4)]
        self.comboZCalNames = [ttk.Combobox(self.frameSeven,
                                       textvariable=self.strZCalNames[i],
                                       width=82) for i in range(4)]
        for i in range(4):
            print(self.get_file_list_zcals(self.strZCalDirs[i].get()))
            self.comboZCalNames[i]['values'] = self.get_file_list_zcals(self.strZCalDirs[i].get())
            self.strZCalNames[i].set(self.comboZCalNames[i]['values'][0])

        self.labelNumBins = ttk.Label(self.frameOne, text='Number of frequency bins')
        self.labelActiveLasers = ttk.Label(self.frameOne, text='Active lasers: ')
        self.boolActiveLasers = [tk.BooleanVar() for i in range(4)]
        self.checkActiveLasers = [ttk.Checkbutton(self.frameOne,
                                                  variable=self.boolActiveLasers[i],
                                                  command=lambda:self.spinNumBinsClick('<Button-1>')) for i in range(4)]
        self.labelWavelengths = ttk.Label(self.frameOne, text='Wavelengths: ')
        self.strWavelengths = [tk.StringVar() for i in range(4)]
        def_waves = ['488','561','647','750']
        self.entryWavelengths = [ttk.Entry(self.frameOne,
                                          textvariable=self.strWavelengths[i],
                                          width=6) for i in range(4)]

        self.labelDyes = ttk.Label(self.frameOne, text='Fluorophores: ')
        self.strDyes = [tk.StringVar() for i in range(4)]
        def_dyes = ['A488','Cy3B','A647','A750']
        self.entryDyes = [ttk.Entry(self.frameOne,
                                          textvariable=self.strDyes[i],
                                          width=6) for i in range(4)]

        for i in range(4):
            self.strWavelengths[i].set(def_waves[i])
            self.strDyes[i].set(def_dyes[i])

        self.buttonBgRemoval = ttk.Button(self.frameTwo, text = 'Remove background')
        self.buttonBgRemoval.bind('<Button-1>', self.buttonBgRemovalClick)

        self.labelBgRemovalBlock = ttk.Label(self.frameTwo, text='Background removal block size:')
        self.strBgRemovalBlock = tk.StringVar()
        self.strBgRemovalBlock.set('50000')
        self.entryBgRemovalBlock = ttk.Entry(self.frameTwo,
                                             textvariable=self.strBgRemovalBlock,
                                             width=10)

        self.buttonReadOneFrame = ttk.Button(self.frameThree, text = 'Read a single localization frame (testing)')
        self.buttonReadOneFrame.bind('<Button-1>', self.buttonReadOneFrameClick)
        self.buttonCategorizeSingleMulti = ttk.Button(self.frameThree, text = 'Categorize localizations into single- or multi-frame')
        self.buttonCategorizeSingleMulti.bind('<Button-1>', self.buttonCategorizeSingleMultiClick)
        self.buttonDemodIndividuals = ttk.Button(self.frameThree, text = 'Demodulate at each raw localization')
        self.buttonDemodIndividuals.bind('<Button-1>', self.buttonDemodIndividualsClick)

        self.labelCategoryThreshold = ttk.Label(self.frameThree, text='Distance threshold:')
        self.strCategoryThreshold = tk.StringVar()
        self.strCategoryThreshold.set('0.5')
        self.entryCategoryThreshold = ttk.Entry(self.frameThree,
                                              textvariable=self.strCategoryThreshold,
                                              width=10)

        self.labelSingleFrameRead = ttk.Label(self.frameThree, text='Frame to read:')
        self.strSingleFrameRead = tk.StringVar()
        self.strSingleFrameRead.set('2000')
        self.entrySingleFrameRead = ttk.Entry(self.frameThree,
                                              textvariable=self.strSingleFrameRead,
                                              width=10)

        self.labelDemodBlock = ttk.Label(self.frameThree, text='Demodulation block size:')
        self.strDemodBlock = tk.StringVar()
        self.strDemodBlock.set('10000')
        self.entryDemodBlock = ttk.Entry(self.frameThree,
                                         textvariable=self.strDemodBlock,width=10)

        self.buttonTrainSVC = ttk.Button(self.frameFour, text = 'Train support vector classifier')
        self.buttonTrainSVC.bind('<Button-1>', self.buttonTrainSVCClick)
        self.labelRatio = ttk.Label(self.frameFour, text='Rejection ratio:')
        self.strRatio = tk.StringVar()
        self.strRatio.set('0.95')
        self.entryRatio = ttk.Entry(self.frameFour,
                                    textvariable=self.strRatio,
                                    width=5)
        self.labelType = ttk.Label(self.frameFour, text='Type:')
        self.type = tk.StringVar()
        self.type.set('single')
        self.comboType = ttk.Combobox(self.frameFour,
                                      textvariable=self.type,
                                      width=6)
        self.comboType['values'] = ('single','multi')
        self.buttonTestSVC = ttk.Button(self.frameFour, text = 'Test support vector classifier')
        self.buttonTestSVC.bind('<Button-1>', self.buttonTestSVCClick)
        self.buttonMergeSVCLocs = ttk.Button(self.frameFour, text='Merge single- and multi-frame localizations')
        self.buttonMergeSVCLocs.bind('<Button-1>', self.buttonMergeSVCLocsClick)
        self.buttonPlotLocsOnSVC = ttk.Button(self.frameFour, text='Plot test data on SVC decision boundary')
        self.buttonPlotLocsOnSVC.bind('<Button-1>', self.buttonPlotLocsOnSVCClick)
        self.buttonCalLocZ = ttk.Button(self.frameFour, text='Calculate Z positions of localizations')
        self.buttonCalLocZ.bind('<Button-1>', self.buttonCalLocZClick)

        self.buttonReloadDirs = ttk.Button(self.frameFive, text = 'Reload directories')
        self.buttonReloadDirs.bind('<Button-1>', self.buttonReloadDirsClick)
        self.buttonReload = ttk.Button(self.frameFive, text = 'Reload DemodLocalizer module')
        self.buttonReload.bind('<Button-1>', self.buttonReloadClick)
        self.buttonExit = ttk.Button(self.frameFive, text = 'Exit program')
        self.buttonExit.bind('<Button-1>', self.buttonExitClick)

    def constructGrid(self):
        # Time to build the GUI! Frame one (top-left)
        self.mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.frameOne.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        _row = 0
        _col = 0
        self.labelDataDir.grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
        _row += 1
        self.entryDataDir.grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
        _row += 1
        self.labelDataName.grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
        _row += 1
        self.comboDataName.grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
        _row += 1
        self.labelNumBins.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.spinNumBins.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelActiveLasers.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        for i in range(4):
            self.checkActiveLasers[i].grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
            if i < self.n_lasers:
                self.checkActiveLasers[i].configure(state='normal')
            else:
                self.checkActiveLasers[i].configure(state='disabled')
            _col += 1
        _row += 1
        _col = 2
        self.labelWavelengths.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        for i in range(4):
            self.entryWavelengths[i].grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
            if i < self.n_lasers:
                self.entryWavelengths[i].configure(state='normal')
            else:
                self.entryWavelengths[i].configure(state='disabled')
            _col += 1
        _row += 1
        _col = 2
        self.labelDyes.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        for i in range(4):
            self.entryDyes[i].grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
            if i < self.n_lasers:
                self.entryDyes[i].configure(state='normal')
            else:
                self.entryDyes[i].configure(state='disabled')
            _col += 1
        _row += 1
        _col = 2
        _col = 0

        self.frameTwo.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        _row = 0
        _col = 0
        self.buttonBgRemoval.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelBgRemovalBlock.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.entryBgRemovalBlock.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col = 0
        _row += 1

        self.frameThree.grid(column=0, row=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        _row = 0
        _col = 0
        self.buttonCategorizeSingleMulti.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelCategoryThreshold.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.entryCategoryThreshold.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col = 0
        _row += 1
        self.buttonReadOneFrame.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelSingleFrameRead.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.entrySingleFrameRead.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col = 0
        _row += 1
        self.buttonDemodIndividuals.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelDemodBlock.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.entryDemodBlock.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col = 0
        _row += 1

        self.frameFour.grid(column=0, row=3, sticky=(tk.N, tk.S, tk.E,tk. W))
        _row = 0
        _col = 0
        self.buttonTrainSVC.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelRatio.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.entryRatio.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col = 0
        _row += 1
        self.buttonTestSVC.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.labelType.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _col += 1
        self.comboType.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        _col = 0
        self.buttonMergeSVCLocs.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        self.buttonPlotLocsOnSVC.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        self.buttonCalLocZ.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1

        self.frameFive.grid(column=0, row=4, sticky=(tk.N, tk.S, tk.E, tk.W))
        _row = 0
        _col = 0
        self.buttonReloadDirs.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        self.buttonReload.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        self.buttonExit.grid(column=_col, row=_row, columnspan=1, sticky=(tk.N, tk.W))
        _row += 1
        
        self.secondMainFrame.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.frameSix.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        for i in range(4):
            self.labelSpecCalDirs[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.entrySpecCalDirs[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.labelSpecCalNames[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.comboSpecCalNames[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            if i < self.n_lasers:
                if self.boolActiveLasers[i].get():
                    self.labelSpecCalDirs[i].configure(state='normal')
                    self.entrySpecCalDirs[i].configure(state='normal')
                    self.labelSpecCalNames[i].configure(state='normal')
                    self.comboSpecCalNames[i].configure(state='normal')
                    self.entryWavelengths[i].configure(state='normal')
                    self.entryDyes[i].configure(state='normal')
                else:
                    self.labelSpecCalDirs[i].configure(state='disabled')
                    self.entrySpecCalDirs[i].configure(state='disabled')
                    self.labelSpecCalNames[i].configure(state='disabled')
                    self.comboSpecCalNames[i].configure(state='disabled')
                    self.entryWavelengths[i].configure(state='disabled')
                    self.entryDyes[i].configure(state='disabled')
            else:
                self.labelSpecCalDirs[i].configure(state='disabled')
                self.entrySpecCalDirs[i].configure(state='disabled')
                self.labelSpecCalNames[i].configure(state='disabled')
                self.comboSpecCalNames[i].configure(state='disabled')
                self.entryWavelengths[i].configure(state='disabled')
                self.entryDyes[i].configure(state='disabled')
        
        self.frameSeven.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        for i in range(4):
            self.labelZCalDirs[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.entryZCalDirs[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.labelZCalNames[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            self.comboZCalNames[i].grid(column=_col, row=_row, columnspan=8, sticky=(tk.N, tk.W))
            _row += 1
            if i < self.n_lasers:
                if self.boolActiveLasers[i].get():
                    self.labelZCalDirs[i].configure(state='normal')
                    self.entryZCalDirs[i].configure(state='normal')
                    self.labelZCalNames[i].configure(state='normal')
                    self.comboZCalNames[i].configure(state='normal')
                else:
                    self.labelZCalDirs[i].configure(state='disabled')
                    self.entryZCalDirs[i].configure(state='disabled')
                    self.labelZCalNames[i].configure(state='disabled')
                    self.comboZCalNames[i].configure(state='disabled')
            else:
                self.labelZCalDirs[i].configure(state='disabled')
                self.entryZCalDirs[i].configure(state='disabled')
                self.labelZCalNames[i].configure(state='disabled')
                self.comboZCalNames[i].configure(state='disabled')

    def spinNumBinsClick(self, event):
        self.n_lasers = int(self.spinNumBins.get())
        for i in range(4):
            if i < self.n_lasers:
                self.checkActiveLasers[i].configure(state='normal')
                if self.boolActiveLasers[i].get():
                    self.labelSpecCalDirs[i].configure(state='normal')
                    self.entrySpecCalDirs[i].configure(state='normal')
                    self.labelSpecCalNames[i].configure(state='normal')
                    self.comboSpecCalNames[i].configure(state='normal')
                    self.labelZCalDirs[i].configure(state='normal')
                    self.entryZCalDirs[i].configure(state='normal')
                    self.labelZCalNames[i].configure(state='normal')
                    self.comboZCalNames[i].configure(state='normal')
                    self.entryWavelengths[i].configure(state='normal')
                    self.entryDyes[i].configure(state='normal')
                else:
                    self.labelSpecCalDirs[i].configure(state='disabled')
                    self.entrySpecCalDirs[i].configure(state='disabled')
                    self.labelSpecCalNames[i].configure(state='disabled')
                    self.comboSpecCalNames[i].configure(state='disabled')
                    self.labelZCalDirs[i].configure(state='disabled')
                    self.entryZCalDirs[i].configure(state='disabled')
                    self.labelZCalNames[i].configure(state='disabled')
                    self.comboZCalNames[i].configure(state='disabled')
                    self.entryWavelengths[i].configure(state='disabled')
                    self.entryDyes[i].configure(state='disabled')
            else:
                self.checkActiveLasers[i].configure(state='disabled')
                self.labelSpecCalDirs[i].configure(state='disabled')
                self.entrySpecCalDirs[i].configure(state='disabled')
                self.labelSpecCalNames[i].configure(state='disabled')
                self.comboSpecCalNames[i].configure(state='disabled')
                self.labelZCalDirs[i].configure(state='disabled')
                self.entryZCalDirs[i].configure(state='disabled')
                self.labelZCalNames[i].configure(state='disabled')
                self.comboZCalNames[i].configure(state='disabled')
                self.entryWavelengths[i].configure(state='disabled')
                self.entryDyes[i].configure(state='disabled')
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        self.localizer = None
        self.localizer = udl.DemodLocalizer(lasers, int(2*self.n_lasers))

    def buttonDirClick(self, event):
        """
        Opens a UI for the user to select a new directory to load data from,
        processes and displays the list of all valid modulated counter files in
        the drop-down file selector menu.
        """
        new_dir = ttkfd.askdirectory(initialdir=self.initdir) + '/'
        print('Changed to', new_dir, '\n')
        self.dir.set(new_dir)
        self.get_file_list(self.strDataName.get())

    def get_file_list(self, directory):
        """
        Gets the list of all modulated counter files in a directory. Throws
        an exception if there are no valid modulated counter files, catches it,
        and displays and error message.
        """
        try:
            files = os.listdir(directory)
            valid_files = []
            for file in files:
                if file.endswith('.dax'):
                    valid_files.append(file)
            return valid_files
        except IndexError:
            print('*** ERROR: No valid files in this directory ***\n')
            return None
        except AttributeError:
            print('Warning: func get_file_list() threw AttributeError\n')
            return None
        
    def get_file_list_zcals(self, directory):
        try:
            files = os.listdir(directory)
            valid_files = []
            for file in files:
                if file.endswith('.txt'):
                    valid_files.append(file)
            if valid_files != []:
                return valid_files
            else:
                return ['NO VALID FILES FOUND']
        except IndexError:
            print('*** ERROR: No valid files in this directory ***\n')
            return ['NO VALID FILES FOUND']
        except AttributeError:
            print('Warning: func get_file_list_zcals() threw AttributeError\n')
            return ['NO VALID FILES FOUND']

    def buttonBgRemovalClick(self, event):
        size = int(self.strBgRemovalBlock.get())
        offset = 0
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        return self.localizer.bg_removal(size=size,offset=offset)

    def buttonReadOneFrameClick(self, event):
        frame = int(self.strSingleFrameRead.get())
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        return self.localizer.read_single_localization_frame(frame=frame)

    def buttonCategorizeSingleMultiClick(self, event):
        block_size = None
        threshold = float(self.strCategoryThreshold.get())
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        return self.localizer.individual_are_single_or_multi(block_size=block_size, dist_thresh=threshold)

    def buttonDemodIndividualsClick(self, event):
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        chunk_size = int(self.strDemodBlock.get())
#        chunk_size = 2000
        f_type = 'single'
        block_size = None
        lasers = None
        self.localizer.demodulate_individual_localizations(chunk_size=chunk_size,
                                                                  f_type=f_type,
                                                                  block_size=block_size,
                                                                  lasers=lasers)
        f_type = 'multi'
        self.localizer.demodulate_individual_localizations(chunk_size=chunk_size,
                                                                  f_type=f_type,
                                                                  block_size=block_size,
                                                                  lasers=lasers)


    def buttonTrainSVCClick(self, event):
        labels = {}
        labels['waves'] = [self.entryWavelengths[i].get() for i in range(self.n_lasers)]
        labels['dyes'] = [self.entryDyes[i].get() for i in range(self.n_lasers)]
        ratio = float(self.strRatio.get())
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        ints_multi = [[]]*sum(lasers)
        ints_single = [[]]*sum(lasers)
        self.loc_train = [udl.DemodLocalizer(lasers, int(2*self.n_lasers)) for i in range(len(lasers))]
        index = 0
        for i, e in enumerate(lasers):
            if e:
                self.loc_train[i].gen_filenames(self.strSpecCalDirs[i].get(), self.strSpecCalNames[i].get()[:-4])
                ints_multi[index] = self.loc_train[i].load_from_indiv_ints('multi', -1)
                factor_m = 1+(ints_multi[index].shape[0]//10000)
                ints_multi[index] = ints_multi[index][::factor_m]
                ints_single[index] = self.loc_train[i].load_from_indiv_ints('single', -1)
                factor_s = 1+(ints_single[index].shape[0]//10000)
                ints_single[index] = ints_single[index][::factor_s]
                index+=1
                
        self.svc_trained = udl.train_N_color_SVC(ints_multi, lasers, ratio, labels)
        udl.validate_N_color_SVC(ints_single, self.svc_trained, lasers, ratio, labels)

    def buttonTestSVCClick(self, event):
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        self.test_ints = self.localizer.load_from_indiv_ints(self.type.get(), -1)
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        self.localizer.test_N_color_SVC(self.test_ints,
                                        self.svc_trained,
                                        lasers,
                                        float(self.strRatio.get()),
                                        self.comboType.get())

    def buttonMergeSVCLocsClick(self, event):
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        self.localizer.merge_SVC_bin_files()

    def buttonPlotLocsOnSVCClick(self, event):
        labels = {}
        labels['waves'] = [self.entryWavelengths[i].get() for i in range(self.n_lasers)]
        labels['dyes'] = [self.entryDyes[i].get() for i in range(self.n_lasers)]
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        ratio = float(self.strRatio.get())
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        if self.svc_trained and self.test_ints.any():
            factor = 1+(self.test_ints.shape[0]//10000)
            data_ints = self.test_ints[::factor]
            udl.plot_ints_on_SVC(data_ints, self.svc_trained, lasers, ratio, labels)
        else:
            print('Train SVC and categorize test data first')

    def buttonCalLocZClick(self, event):
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        z_cal_files = [self.strZCalDirs[idx].get()+self.strZCalNames[idx].get() for idx, l in enumerate(lasers) if l]
        tol = 5
        maxfev = 200
        print(z_cal_files)
        self.localizer.calc_localization_Z_positions(z_cal_files, tol, maxfev)

    def buttonReloadDirsClick(self, event):
        self.localizer = None
        lasers = [self.boolActiveLasers[i].get() for i in range(self.n_lasers)]
        self.localizer = udl.DemodLocalizer(lasers, int(2*self.n_lasers))
        self.comboDataName['values'] = self.get_file_list(self.strDataDir.get())
        self.strDataName.set(self.comboDataName['values'][0])
        for i in range(len(lasers)):
            self.comboSpecCalNames[i]['values'] = self.get_file_list(self.strSpecCalDirs[i].get())
            self.strSpecCalNames[i].set(self.comboSpecCalNames[i]['values'][0])
        self.localizer.gen_filenames(self.strDataDir.get(), self.strDataName.get()[:-4])
        print('Directory updated\n')
        return True

    def buttonReloadClick(self, event):
        importlib.reload(udl)
        print('DemodLocalizer module reloaded\n')
        return True

    def buttonExitClick(self, event):
        self.parent.destroy()
        return True

def main():
    root = tk.Tk()
    root.option_add('*tearOff', False)
    app = App(root)
    app.constructGUI()
    root.mainloop()

if __name__ == '__main__':
    main()