import numpy as np
import DAX
import shutil
import local_dft
import i3dtype
import readinsight3
import writeinsight3
import matplotlib.pyplot as plt
from scipy.spatial import distance
from scipy import optimize
from timeit import default_timer as timer
from sklearn.model_selection import ShuffleSplit
from sklearn.svm import SVC

class DemodLocalizer:
    def __init__(self, lasers, block):
        '''
        We define all of the filenames in advance so that we can just pass
        them around and call them whenever we need them inside functions. We
        cannot define the I3Reader and I3Writer tasks yet because some of the
        requirements (e.g. localization files) might not exist at intialization.
        I3Reader and I3Writer tasks are initialized in local function calls.
        '''

        # Define the demodulation block size
        self.block_size = block

        # 'lasers' is a list of Booleans
        self.lasers = lasers
        self.num_lasers = np.sum(self.lasers)

    def gen_filenames(self, filepath, prefix):
        # The path to the files (global or local)
        self.filepath = filepath

        # E.g. 'Cell3_001'
        self.file_prefix = prefix

        # E.g. '/filepath/Cell3_001.dax'
        self.base_DAX_name = self.filepath+self.file_prefix+'.dax'
#        print('Base DAX file:',self.base_DAX_name,'\n')

        # The filename of the median-subtracted DAX file
        # E.g. '/filepath/Cell3_001_no_bg.dax'
        self.nobg_DAX_name = self.base_DAX_name[:-4]+'_no_bg.dax'
#        print('Background-subtracted DAX file:',self.nobg_DAX_name,'\n')

        # Filename for the Insight3 background-subtracted localization file
        # E.g. '/filepath/Cell3_001_no_bg_list.bin'
        self.i3inNobgBinName = self.nobg_DAX_name[:-4]+'_list.bin'
#        print('Background-subtracted localization file:',self.i3inNobgBinName,'\n')

        # List of filenames for the single/multi localizations.
        # Each of these files will have the uncategorized localizations as an
        # intermediate step to intensity-based classification
        # E.g. ['/filepath/Cell3_001_no_bg_single_list.bin',
        #       '/filepath/Cell3_001_no_bg_multi_list.bin']
        self.i3TypeBinNames = {}
        self.i3TypeBinNames['single'] = self.nobg_DAX_name[:-4]+'_single_list.bin'
        self.i3TypeBinNames['multi'] =  self.nobg_DAX_name[:-4]+'_multi_list.bin'
#        print('Single- and multi-frame localization files:',self.i3TypeBinNames,'\n')

        # List of filenames for the single/multi localizations.
        # Each of these files will have the uncategorized localizations as an
        # intermediate step to intensity-based classification
        # E.g. ['/filepath/Cell3_001_no_bg_single_list.bin',
        #       '/filepath/Cell3_001_no_bg_multi_list.bin']
        self.i3TypeIndivBinNames = {}
        self.i3TypeIndivBinNames['single'] = self.nobg_DAX_name[:-4]+'_indiv_single_list.bin'
        self.i3TypeIndivBinNames['multi'] =  self.nobg_DAX_name[:-4]+'_indiv_multi_list.bin'
#        print('Single- and multi-frame individual localization files:',self.i3TypeIndivBinNames,'\n')

        # List of filenames for the single/multi localizations.
        # Each of these files will have the uncategorized localizations as an
        # intermediate step to intensity-based classification
        # These are for the individually-demodulated localizations
        # E.g. ['/filepath/Cell3_001_no_bg_single_list.bin',
        #       '/filepath/Cell3_001_no_bg_multi_list.bin']
        self.i3CatIndivBinNames = {}
        self.i3CatIndivBinNames['single'] = self.nobg_DAX_name[:-4]+'_indiv_single_cat_list.bin'
        self.i3CatIndivBinNames['multi'] =  self.nobg_DAX_name[:-4]+'_indiv_multi_cat_list.bin'
#        print('Categorized individual localization files:',self.i3CatIndivBinNames,'\n')

        # List of filenames for the intensity ratio of each localization
        # Each of these files is for either the single- or multiple-frame
        # localizations, and contains ONLY those localizations which appear in
        # multiple color channels. Single-color localizations are omitted.
        # These are for the individually-demodulated localizations
        # E.g. ['/filepath/Cell3_001_no_bg_single_list.ints',
        #       '/filepath/Cell3_001_no_bg_multi_list.ints']
        self.loc_intens_ratio_indiv_names = {}
        self.loc_intens_ratio_indiv_names['single'] = self.i3TypeIndivBinNames['single'][:-4]+'.ints'
        self.loc_intens_ratio_indiv_names['multi'] = self.i3TypeIndivBinNames['multi'][:-4]+'.ints'
#        print('Intensity ratio files:',self.loc_intens_ratio_indiv_names,'\n')

        # List of filenames for the clustered SVC test localizations.
        # Each of these files will have the categorized localizations from
        # the test (single) set, with categories found according to a trained
        # multinomial logistic regression
        # E.g. ['/filepath/Cell3_001_indiv_single_SVC_list.bin',
        #       '/filepath/Cell3_001_indiv_multi_SVC_list.bin']
        self.i3TestIndivSVCBinNames = {}
        self.i3TestIndivSVCBinNames['single'] =  self.nobg_DAX_name[:-4]+'_indiv_single_SVC_list.bin'
        self.i3TestIndivSVCBinNames['multi'] =  self.nobg_DAX_name[:-4]+'_indiv_multi_SVC_list.bin'
#        print('Categorized individual localization files:',self.i3TestIndivSVCBinNames,'\n')

        # Filename for the merged clustered SVC test localizations.
        # This file will have the categorized localizations from
        # the test (single) set, with categories found according to a trained
        # multinomial logistic regression
        # E.g. ['/filepath/Cell3_001_indiv_single_SVC_list.bin',
        #       '/filepath/Cell3_001_indiv_multi_SVC_list.bin']
        self.i3TestCombSVCBinName = {}
        self.i3TestCombSVCBinName =  self.nobg_DAX_name[:-4]+'_indiv_test_comb_SVC_list.bin'
#        print('Categorized individual localization files:',self.i3TestIndivSVCBinNames,'\n')

        # Filename for the merged clustered SVC test localizations with Z calibration.
        # This file will have the categorized localizations from
        # the test (single) set, with categories found according to a trained
        # multinomial logistic regression, with calibrated Z coordinates for each color.
        # E.g. ['/filepath/Cell3_001_indiv_single_SVC_list.bin',
        #       '/filepath/Cell3_001_indiv_multi_SVC_list.bin']
        self.i3TestZCombSVCBinNames = {}
        self.i3TestZCombSVCBinNames =  self.nobg_DAX_name[:-4]+'_indiv_Zcal_comb_SVC_list.bin'
#        print('Categorized individual localization files:',self.i3TestIndivSVCBinNames,'\n')

    def bg_removal(self, size=10000, offset=0):
        print('Subtracting median background from raw DAX file.')
        daxIn = DAX.DAX()
        daxOut = DAX.DAX()
        daxIn.open(self.base_DAX_name)
        daxOut.create(self.nobg_DAX_name)
        _im_size = daxIn.height
        _num_frames = daxIn.numFrames
        _chunk_size = size # Due to memory restrictions
        _num_chunks = _num_frames//_chunk_size
        _extra_frames = _num_frames%_chunk_size
        data = np.zeros([_chunk_size, _im_size, _im_size]).astype(np.uint16)
        bg_free_data = np.zeros([_chunk_size, _im_size, _im_size]).astype(np.uint16)
        start_time = timer()
        for i in range(_num_chunks):
            for j in range(_chunk_size):
                data[j] = daxIn.read(_chunk_size*i+j)
            for j in range(_chunk_size):
                bg_free_data[j] = np.abs(offset+data[j]-np.median(data[j])).astype(np.uint16)
            for j in range(_chunk_size):
                daxOut.write(bg_free_data[j])
        if _extra_frames:
            for j in range(_extra_frames):
                data[j] = daxIn.read(_chunk_size*_num_chunks+j)
            for j in range(_extra_frames):
                bg_free_data[j] = np.abs(offset+data[j]-np.median(data[j])).astype(np.uint16)
            for j in range(_extra_frames):
                daxOut.write(bg_free_data[j])
        print('Background subtraction finished in',str(int(timer() - start_time)),'seconds.\n')
        daxIn.close()
        daxOut.close()
        shutil.copy(self.base_DAX_name[:-4]+'.inf', self.nobg_DAX_name[:-4]+'_no_bg.inf')
        data = None
        bg_free_data = None
        return True

    def read_single_localization_frame(self, frame):
        i3in = readinsight3.I3Reader(self.i3TypeIndivBinNames['multi'])
        locs = i3in.getMoleculesInFrame(frame)
        print(locs)
        i3in.close()
        return locs

    def individual_are_single_or_multi(self, block_size=None, dist_thresh=0.5):
        if block_size == None:
            block_size = self.block_size
        # Insight3 .bin reader for the median-subtracted localizations
        i3inNobg = readinsight3.I3Reader(self.i3inNobgBinName)
        num_frames = i3inNobg.getNumberFrames()
        single = np.zeros([i3inNobg.getNumMols(),4])
        multi = np.zeros([i3inNobg.getNumMols()//2,4])
        print('Opened',self.i3inNobgBinName,'for reading background-subtracted localizations.')
        start_time = timer()
        s_idx = 0
        m_idx = 0
        for frame in range(num_frames//block_size):
            dists_th = np.array([False])
            molsNobg = i3inNobg.getMoleculesInFrameRange(block_size*frame,\
                                                         block_size*(frame+1))
            molsNobg = np.sort(molsNobg, order=['fr','x','y'])
            molsNobg_xy = np.array([molsNobg['x'],molsNobg['y']]).T
            dists = distance.squareform(distance.pdist(molsNobg_xy))
            dists_th = dists<dist_thresh
            num_mols = molsNobg.shape[0]
            multis = []
            for i in range(num_mols):
                if i in multis:
                    pass
                else:
                    loc = np.array([molsNobg[i]['x'],molsNobg[i]['y']])
                    div = 1
                    for j in range(i+1,num_mols):
                        if dists_th[i][j]:
                            div+=1
                            if i not in multis:
                                multis.append(i)
                            if j not in multis:
                                multis.append(j)
                            loc = np.sum([loc,[molsNobg[j]['x'],molsNobg[j]['y']]],axis=0)
                    loc /= div
                    if i in multis:
                        multi[m_idx] = [molsNobg[i]['x'],molsNobg[i]['y'],molsNobg[i]['z'],molsNobg[i]['fr']]
                        m_idx+=1
                    else:
                        single[s_idx] = [molsNobg[i]['x'],molsNobg[i]['y'],molsNobg[i]['z'],molsNobg[i]['fr']]
                        s_idx+=1

        i3inNobg.close()
        print('Localization classification completed in %f seconds.' % (timer()-start_time))

        i3outSingle = writeinsight3.I3Writer(self.i3TypeIndivBinNames['single'], frames=num_frames-1)
        print('Opened',self.i3TypeIndivBinNames['single'],'for writing single-frame localizations.')
        i3outSingle.addMoleculesWithXYZF(single[:s_idx,0],single[:s_idx,1],single[:s_idx,2],single[:s_idx,3])
        i3outSingle.close()
        print('Finished writing single-frame localizations.')
        i3outMulti = writeinsight3.I3Writer(self.i3TypeIndivBinNames['multi'], frames=num_frames-1)
        print('Opened',self.i3TypeIndivBinNames['multi'],'for writing multi-frame localizations.')
        i3outMulti.addMoleculesWithXYZF(multi[:m_idx,0],multi[:m_idx,1],multi[:m_idx,2],multi[:m_idx,3])
        i3outMulti.close()
        print('Finished writing multi-frame localizations.')
        single = None
        multi = None
        print('Finished assigning localizations.\n')
        return True

    def demodulate_individual_localizations(self,
                                            chunk_size=1000,
                                            f_type='single',
                                            block_size=None,
                                            lasers=None):
        daxIn = DAX.DAX()
        daxIn.open(self.nobg_DAX_name)
        _num_frames = daxIn.numFrames
        _im_size = daxIn.height
        if block_size == None:
            block_size = self.block_size
        if lasers == None:
            lasers = self.lasers
        _chunk_size = chunk_size*block_size
        _num_chunks = _num_frames//(_chunk_size)
        _extra_frames = _num_frames%(_chunk_size)
        print(_chunk_size,_num_chunks,_extra_frames,_chunk_size*_num_chunks+_extra_frames)

        i3in = readinsight3.I3Reader(self.i3TypeIndivBinNames[f_type])
        locs = i3in.getMoleculesInFrameRange(0,_num_frames+1)
        demod_locs = np.zeros([locs.shape[0],4+np.sum(lasers)])
        idx_dm = 0
        data = np.zeros([_chunk_size+block_size, _im_size, _im_size]).astype(np.uint16)
        for i in range(_num_chunks):
            t_locs = i3dtype.maskData(locs,locs['fr']>=_chunk_size*i+1)
            i_locs = i3dtype.maskData(t_locs,t_locs['fr']<_chunk_size*(i+1)+1)
            start_time = timer()
            for j in range(_chunk_size+block_size):
                data[j] = daxIn.read(_chunk_size*i+j)
            curr_locs = idx_dm
            for frame in range(_chunk_size):
                _f = frame+_chunk_size*i
                l_locs = i3dtype.maskData(i_locs,i_locs['fr']==_f+1)
                l_data = data[frame:frame+block_size]
                temp_locs = local_dft.calc_indiv_demods_new(l_locs,l_data,lasers,_im_size)
                demod_locs[idx_dm:idx_dm+temp_locs.shape[0]] = temp_locs
                idx_dm += temp_locs.shape[0]
            stop_time = timer()
            new_locs = idx_dm - curr_locs
            print('Chunk %d of %d complete in %d seconds (%d localizations added).' % (i+1, _num_chunks, stop_time-start_time, new_locs))
        start_time = timer()
        for j in range(_extra_frames):
            data[j] = daxIn.read(_chunk_size*_num_chunks+j)
        curr_locs = idx_dm
        i_locs = i3dtype.maskData(locs,locs['fr']>=_chunk_size*_num_chunks+1)
        for frame in range(_extra_frames-block_size):
            _f = frame+_num_chunks*_chunk_size
            l_locs = i3dtype.maskData(i_locs,i_locs['fr']==_f+1)
            l_data = data[frame:frame+block_size]
            temp_locs = local_dft.calc_indiv_demods_new(l_locs,l_data,lasers,_im_size)
            demod_locs[idx_dm:idx_dm+temp_locs.shape[0]] = temp_locs
            idx_dm += temp_locs.shape[0]
        stop_time = timer()
        new_locs = idx_dm - curr_locs
        print('Extra frames complete in %d seconds (%d localizations added).' % (stop_time-start_time, new_locs))
        i3in.close()
        daxIn.close()
        i3out = writeinsight3.I3Writer(self.i3CatIndivBinNames[f_type],_num_frames-1)
        i3out.addMoleculesWithXYZF(demod_locs[:,0],demod_locs[:,1],demod_locs[:,2],demod_locs[:,3])
        i3out.close()
        self.write_to_indiv_ints(demod_locs, f_type)
        return True

    def write_to_indiv_ints(self, ints, f_type='single'):
        with open(self.loc_intens_ratio_indiv_names[f_type], 'w') as ints_file:
            ints_file.writelines('\t'.join(str(i) for i in l) + '\n' for l in ints)
        ints_file.close()

    def load_from_indiv_ints(self, f_type='single', number_to_read=-1):
        with open(self.loc_intens_ratio_indiv_names[f_type], 'r') as ints_file:
            if number_to_read>0:
                ints_in_str = ints_file.readlines(number_to_read)
            else:
                ints_in_str = ints_file.readlines()
        ints_file.close()
        width = len(ints_in_str[0].split())
        ints = np.zeros([len(ints_in_str),width+self.num_lasers])
        idx = 0
        for line in ints_in_str:
            temp = line.split()
            ints[idx][0:4+self.num_lasers] = temp
            ints[idx][4+self.num_lasers:] = \
                np.log(np.array(temp[4:]).astype(np.float)+1)
            idx+=1
        return ints

    def plot_indiv_ints(self, ints=[], f_type='single'):
        if ints == []:
            with open(self.loc_intens_ratio_indiv_names[f_type], 'r') as ints_file:
                ints_in_str = ints_file.readlines()
            ints_file.close()
            ints = np.zeros([len(ints_in_str),2])
            for idx, line in enumerate(ints_in_str):
                ints[idx] = line.split()
        plt.figure(figsize=(8,8))
        plt.title(f_type + ' log intensity histogram')
        [counts, xedges, yedges, Image] = plt.hist2d(ints[:,4+self.num_lasers], ints[:,5+self.num_lasers],\
            bins=200, cmap=plt.cm.OrRd)
        plt.xlabel('Log(Ch1 (yellow) intensity)')
        plt.ylabel('Log(Ch0 (red) intensity)')
        plt.xlim(5, 11)
        plt.ylim(5, 11)
        plt.colorbar()
        plt.show()
        return [counts, xedges, yedges]

    def test_N_color_SVC(self, ints, regressor, lasers, ratio, f_type='multi'):
        n_lasers = np.sum(lasers)
        _ints = ints[:,4+n_lasers:4+2*n_lasers]
        dists = distance.cdist(_ints,np.array([[6]*n_lasers]))
        temp_ints = np.array([k for i,k in enumerate(ints) if (dists[i]>0.8)])
        int_mag = distance.cdist(temp_ints[:,4+n_lasers:4+2*n_lasers],np.array([[0]*n_lasers]))
        int_n = temp_ints[:,4+n_lasers:4+2*n_lasers]/int_mag
        unit_v = np.array(([1]*n_lasers)/np.sqrt(np.sum([1]*n_lasers)))
        dists = np.array([np.dot(i,unit_v) for i in int_n])**1000
        new_ints = np.array([k for i,k in enumerate(temp_ints) if dists[i]<ratio**n_lasers])
        labels = regressor.predict(new_ints[:,4+n_lasers:4+2*n_lasers])
        n_classes, c_classes = np.unique(labels, return_counts=True)
        i3out = writeinsight3.I3Writer(self.i3TestIndivSVCBinNames[f_type], frames=int(np.max(new_ints[:,3])))
        i3out.addMoleculesWithXYZCatFrame(new_ints[:,0],new_ints[:,1],new_ints[:,2],labels,new_ints[:,3])
        i3out.close()
        return c_classes

    def merge_SVC_bin_files(self):
        i3multi = readinsight3.I3Reader(self.i3TestIndivSVCBinNames['multi'])
        i3single = readinsight3.I3Reader(self.i3TestIndivSVCBinNames['single'])
        num_frames = int(np.max([i3multi.getNumberFrames(),i3single.getNumberFrames()]))
        i3out = writeinsight3.I3Writer(self.i3TestCombSVCBinName, frames=num_frames)
        im1 = i3multi.getMoleculesInFrameRange(0,num_frames+1)
        is1 = i3single.getMoleculesInFrameRange(0,num_frames+1)
        n_mol0 = im1.shape[0]
        n_mol1 = is1.shape[0]
        i3new = i3dtype.createDefaultI3Data(n_mol0+n_mol1)
        for i in range(n_mol0):
            i3new[i] = im1[i]
        for j in range(n_mol1):
            i3new[n_mol0+j] = is1[j]
        i3new = np.sort(i3new,order=['fr','x','y'])
        i3out.addMoleculesWithXYZHCatFrame(i3new['x'],i3new['y'],i3new['z'],i3new['h'],i3new['c'],i3new['fr'])
        i3multi.close()
        i3single.close()
        i3out.close()
        im1 = None
        is1 = None
        i3new = None
        return True

    def calc_localization_Z_positions(self, cal_files, tol, maxfev):
        def calc_z(mol, cal, init, tol, maxfev):
            def fun(z, *args):
                '''
                args = [const, A, B, c, d]
                '''
                z0 = (z-args[3])/args[4]
                return args[0]+(z0)**2+\
                           args[1]*(z0)**3+\
                           args[2]*(z0)**4
            ax = mol['ax']
            w = mol['w']
            wx = w/np.sqrt(ax)
            wy = w*np.sqrt(ax)
            const_x = 1-(wx/cal['wx0'])**2
            const_y = 1-(wy/cal['wy0'])**2
            xargs = (const_x, cal['Ax'], cal['Bx'], cal['gx'], cal['zrx'])
            yargs = (const_y, cal['Ay'], cal['By'], cal['gy'], cal['zry'])
            fx = optimize.fsolve(fun, [init,init,init,init], args=xargs, xtol=tol, maxfev=maxfev)
            fy = optimize.fsolve(fun, [init,init,init,init], args=yargs, xtol=tol, maxfev=maxfev)
            root_diff = np.argmin(np.abs(fx-fy))
            return np.mean([fx[root_diff],fy[root_diff]])
        cals = []
        for file in cal_files:
            with open(file, 'r') as f:
                params = f.readlines()[0].split(';')
            f.close()
            _cal = {}
            for p in params:
                _cal[p.split('=')[0]]=float(p.split('=')[1])
            cals.append(_cal)
        i3in = readinsight3.I3Reader(self.i3TestCombSVCBinName)
        num_frames = i3in.getNumberFrames()
        i3out = writeinsight3.I3Writer(self.i3TestZCombSVCBinNames, frames=num_frames)
        mols_in = i3in.getMoleculesInFrameRange(0,num_frames+1)
        mols_out = i3in.getMoleculesInFrameRange(0,num_frames+1)
        start_time = timer()
        n_lasers = np.sum(self.lasers)
        cats = []
        for n in range(n_lasers):
            cats.append(len([mol for mol in mols_in if mol['c']==n]))
#        print(cats)
        indices = np.zeros(np.sum(self.lasers)).astype(np.uint32)
        diffs = [np.zeros(c) for c in cats]
        for idx, mol in enumerate(mols_in):
            if idx%10000 == 0:
                stop_time = timer()
                print('%d of %d completed in %f seconds.' % (idx, mols_in.shape[0], stop_time-start_time))
                start_time = timer()
            z = calc_z(mol, cals[mol['c']], mol['z'], tol, maxfev)
            mols_out[idx]['z'] = z
            diffs[mol['c']][indices[mol['c']]] = z - mol['z']
            indices[mol['c']]+=1
        for i in range(len(cats)):
            print('Localization shift, ch%d (mean): %f' % (i, np.mean(diffs[i])))
            print('Localization shift, ch%d (std.): %f' % (i, np.std(diffs[i])))
        i3out.addMolecules(mols_out)
        i3out.close()
        return True

    def close(self):
        return False

def train_N_color_SVC(ints, lasers, ratio, labels):
    n_lasers = np.sum(lasers)
    int_train = np.array([]).reshape(0,n_lasers)
    int_test = [np.array([]).reshape(0,n_lasers) for i in range(n_lasers)]
    int_cats = np.array([])
    rs = ShuffleSplit(n_splits=1,train_size=0.7, test_size=0.3)
    for n in range(n_lasers):
        int_s = ints[n][:,4+n_lasers:4+2*n_lasers]
        int_mag = distance.cdist(int_s,np.array([[0]*n_lasers]))
        int_n = int_s/int_mag
        unit_v = np.array(([1]*n_lasers)/np.sqrt(np.sum([1]*n_lasers)))
        dists = np.array([np.dot(i,unit_v) for i in int_n])**1000
        for train_index, test_index in rs.split(int_s):
            int_s_train = np.array([int_s[i] for i in train_index if dists[i] < ratio**n_lasers])
            int_s_cat = np.ones(int_s_train.shape[0])*n
            int_s_test = np.array([int_s[j] for j in test_index if dists[j] < ratio**n_lasers])
            int_test[n] = np.vstack((int_test[n],int_s_test))
            int_train = np.vstack((int_train, int_s_train))
            int_cats = np.append(int_cats, int_s_cat)
    log_reg = SVC(C=1.0, cache_size=500, kernel='rbf')
    log_reg.fit(int_train, int_cats)

    idx = 0
    for n, l in enumerate(lasers):
        if l:
            cats = log_reg.predict(int_test[idx])
            n_classes, c_classes = np.unique(cats, return_counts=True)
            good = c_classes[idx]
            bad = sum(c_classes)-c_classes[idx]
            print('Fraction of correct %s multi-frame locs: %f' % (labels['dyes'][n], good/sum(c_classes)))
            print('Fraction of wrong %s multi-frame locs: %f' % (labels['dyes'][n], bad/sum(c_classes)))
            print('Total tested %s multi-frame locs: %d\n' % (labels['dyes'][n], sum(c_classes)))
            idx += 1

    colors = ['b','lime','orangered']
    c_arr = [colors[int(i)] for i in int_cats]

    if n_lasers == 2:
        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, x_max]x[y_min, y_max].
        ax_labels = [labels['waves'][i] for i, l in enumerate(lasers) if l]
        x_min, x_max = 5, 11
        y_min, y_max = 5, 11
        h = 0.02
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        ZFull = np.c_[xx.ravel(), yy.ravel()]
        Z = log_reg.predict(ZFull)
        Z = Z.reshape(xx.shape)
        import matplotlib.pyplot as plt
        plt.figure()

#        plt.pcolormesh(xx, yy, Z*0.2, cmap=plt.cm.Reds,alpha=1,edgecolors='None')
#        plt.pcolormesh(xx, yy, (1-Z)*0.2, cmap=plt.cm.Blues,alpha=1,edgecolors='None')
        plt.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=0.5)
        plt.scatter(int_train[:,0],int_train[:,1],c=c_arr,s=4,alpha=0.3,marker='.')
        plt.title('Multi-frame training localizations')
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        plt.xlabel('Log('+ax_labels[0]+'-nm intensity)')
        plt.ylabel('Log('+ax_labels[1]+'-nm intensity)')
        plt.show(block=False)
    elif n_lasers == 3:
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(int_train[:,0],int_train[:,1],int_train[:,2],s=4,c=c_arr)
        ax.set_title('Multi-frame training localizations')

        ax.set_xlabel('Log('+labels['waves'][0]+'-nm intensity)')
        ax.set_ylabel('Log('+labels['waves'][1]+'-nm intensity)')
        ax.set_zlabel('Log('+labels['waves'][2]+'-nm intensity)')
    return log_reg

def validate_N_color_SVC(ints, regressor, lasers, ratio, labels):
    n_lasers = np.sum(lasers)
    int_valid = np.array([]).reshape(0,n_lasers)
    int_cats = np.array([])
    idx = 0
    for n, l in enumerate(lasers):
        if l:
            _ints = ints[idx][:,4+n_lasers:4+2*n_lasers]
            dists = distance.cdist(_ints,np.array([[6]*n_lasers]))
            temp_ints = np.array([k for i,k in enumerate(_ints) if (dists[i]>0.8)])
            int_mag = distance.cdist(temp_ints,np.array([[0]*n_lasers]))
            int_n = temp_ints/int_mag
            unit_v = np.array(([1]*n_lasers)/np.sqrt(np.sum([1]*n_lasers)))
            dists = np.array([np.dot(i,unit_v) for i in int_n])**1000
            new_ints = np.array([k for i,k in enumerate(temp_ints) if dists[i]<ratio**n_lasers])
            int_valid = np.vstack((int_valid, new_ints))
            int_cats = np.append(int_cats, np.ones(new_ints.shape[0])*idx)
            cats = regressor.predict(new_ints)
            n_classes, c_classes = np.unique(cats, return_counts=True)
            good = c_classes[idx]
            bad = sum(c_classes)-c_classes[idx]
            print('Fraction of correct %s single-frame locs: %f' % (labels['dyes'][n], good/sum(c_classes)))
            print('Fraction of wrong %s single-frame locs: %f' % (labels['dyes'][n], bad/sum(c_classes)))
            print('Total tested %s single-frame locs: %d\n' % (labels['dyes'][n], sum(c_classes)))
            idx += 1

    colors = ['b','lime','orangered']
    c_arr = [colors[int(i)] for i in int_cats]

    if n_lasers == 2:
        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, x_max]x[y_min, y_max].
        ax_labels = [labels['waves'][i] for i, l in enumerate(lasers) if l]
        x_min, x_max = 5, 11
        y_min, y_max = 5, 11
        h = 0.02
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        ZFull = np.c_[xx.ravel(), yy.ravel()]
        Z = regressor.predict(ZFull)
        Z = Z.reshape(xx.shape)
        plt.figure()
        plt.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=0.5)
#        plt.pcolormesh(xx, yy, Z, cmap=plt.cm.Reds,alpha=0.2,edgecolors=None)
#        plt.pcolormesh(xx, yy, 1-Z, cmap=plt.cm.Blues,alpha=0.2,edgecolors=None)
        plt.scatter(int_valid[:,0],int_valid[:,1],c=c_arr,s=4,alpha=0.3,marker='.')
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        plt.title('Single-frame training localizations')
        plt.xlabel('Log('+ax_labels[0]+'-nm intensity)')
        plt.ylabel('Log('+ax_labels[1]+'-nm intensity)')
        plt.show(block=False)
    elif n_lasers == 3:
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(int_valid[:,0],int_valid[:,1],int_valid[:,2],s=4,c=c_arr)
        ax.set_title('Single-frame training localizations')
        ax.set_xlabel('Log('+labels['waves'][0]+'-nm intensity)')
        ax.set_ylabel('Log('+labels['waves'][1]+'-nm intensity)')
        ax.set_zlabel('Log('+labels['waves'][2]+'-nm intensity)')
    return True

def plot_ints_on_SVC(ints, regressor, lasers, ratio, labels):
    n_lasers = np.sum(lasers)
    new_ints = ints[:,4+n_lasers:4+2*n_lasers]
    dists = distance.cdist(new_ints,np.array([[6]*n_lasers]))
    temp_ints = np.array([k for i,k in enumerate(new_ints) if (dists[i]>0.8)])
    int_mag = distance.cdist(temp_ints,np.array([[0]*n_lasers]))
    int_n = temp_ints/int_mag
    unit_v = np.array(([1]*n_lasers)/np.sqrt(np.sum([1]*n_lasers)))
    dists = np.array([np.dot(i,unit_v) for i in int_n])**1000
    new_ints = np.array([k for i,k in enumerate(temp_ints) if dists[i]<ratio**n_lasers])
    if n_lasers == 2:
        # Plot the decision boundary. For that, we will assign a color to each
        # point in the mesh [x_min, x_max]x[y_min, y_max].
        ax_labels = [labels['waves'][i] for i, l in enumerate(lasers) if l]
        x_min, x_max = 5, 11
        y_min, y_max = 5, 11
        h = 0.02
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
        ZFull = np.c_[xx.ravel(), yy.ravel()]
        Z = regressor.predict(ZFull)
        Z = Z.reshape(xx.shape)
        plt.figure()
        plt.contourf(xx, yy, Z, cmap=plt.cm.RdBu, alpha=0.5)
#        plt.pcolormesh(xx, yy, Z, cmap=plt.cm.Reds,alpha=0.2,edgecolors=None)
#        plt.pcolormesh(xx, yy, 1-Z, cmap=plt.cm.Blues,alpha=0.2,edgecolors=None)
        plt.scatter(new_ints[:,0],new_ints[:,1],c='k',s=4,alpha=0.3,marker='.')
        plt.title('Test data localizations on SVC decision boundary')
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        plt.xlabel('Log('+ax_labels[0]+'-nm intensity)')
        plt.ylabel('Log('+ax_labels[1]+'-nm intensity)')
        plt.show(block=False)
    elif n_lasers == 3:
        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(new_ints[:,0],new_ints[:,1],ints[:,2],s=4,c='k')
        ax.set_title('Test data localizations')
        ax.set_xlabel('Log('+labels['waves'][0]+'-nm intensity)')
        ax.set_ylabel('Log('+labels['waves'][1]+'-nm intensity)')
        ax.set_zlabel('Log('+labels['waves'][2]+'-nm intensity)')
    return True