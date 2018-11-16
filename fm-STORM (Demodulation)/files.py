# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 16:53:09 2017

@author: Erik
"""

def get_filename_from_base(filepath, prefix, filetype):
    '''
    A helper function that takes a path to the STORM3 data, the prefix of
    the desired file, and the type of file, and returns the complete filename(s)
    of those parameters.

    Examples:
    path =
    prefix = 'Cell3_001'
    filetype =
    '''

    ###
    # The next group of files is used for all versions of the analysis
    ###

    if filetype == 'raw_DAX':
        # The raw DAX file from the STORM3 setup
        # E.g. '/filepath/Cell3_001.dax'
        filenames = filepath+prefix+'.dax'

    elif filetype == 'no-bg_DAX':
        # Median-subtracted DAX file
        # E.g. '/filepath/Cell3_001_no_bg.dax'
        filenames = filepath+prefix+'_no_bg.dax'

    elif filetype == 'no-bg_BIN':

        # I3 .bin files for the localizations of the bg-subtracted DAX file

    ###
    # The next group of files is from the new analysis
    ###

    elif filetype == 'demod_BIN_new':
        #


    elif filetype == 'type_BIN_new':
        #


    elif filetype == 'category_BIN_new':
        #


    elif filetype == 'INT_new':
        #


    elif filetype == 'training_BIN':
        #


    elif filetype == 'cv_BIN':
        #


    elif filetype == 'test_BIN':
        #


    elif filetype == 'training_comb_BIN':
        #


    elif filetype == 'cv_comb_BIN':
        #


    elif filetype == 'test_comb_BIN':
        #


    ###
    # The next group of files is from the old analysis
    ###

    elif filetype == 'demod_DAX':
        # Full demodulated DAX files (1 for each color)
        # E.g. ['/filepath/Cell3_001_no_bg_demod0.dax',
        #       '/filepath/Cell3_001_no_bg_demod1.dax']


    elif filetype == 'demod_BIN':
        #


    elif filetype == 'type_BIN':
        #


    elif filetype == 'category_BIN':
        #


    elif filetype == 'INT_old':
        #



    return filenames