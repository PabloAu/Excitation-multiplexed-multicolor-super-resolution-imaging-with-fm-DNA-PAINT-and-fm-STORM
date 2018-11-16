import numpy as np

def calc_indiv_demods_new(mols, dax, lasers, im_size):
    active_lasers = [i for i,el in enumerate(lasers) if el]
    num_lasers = np.sum(lasers)
    fit = np.zeros(4+num_lasers)
    locs = np.zeros([mols.shape[0],4+num_lasers])
    c_idx = 0
    for m_idx,mol in enumerate(mols):
        fit[0:4] = np.array([mol['x'],mol['y'],mol['z'],mol['fr']])
        x = np.round(mol['x'])
        y = np.round(mol['y'])
        s = 3
        min_x = int(np.max([x-(s//2)-1,0]))
        max_x = int(np.min([x+(s//2),im_size]))
        min_y = int(np.max([y-(s//2)-1,0]))
        max_y = int(np.min([y+(s//2),im_size]))
        if max_x-min_x > 0 and max_y-min_y > 0:
#            dft_data = np.zeros([len(lasers),max_x-min_x,max_y-min_y])
#            new_data = dax[:,min_y:max_y,min_x:max_x]
#            for idx_y in range(new_data.shape[1]):
#                for idx_x in range(new_data.shape[2]):
#                    dft_data[:,idx_x,idx_y] = np.abs(np.fft.rfft(new_data[:,idx_y,idx_x]))[1:]
            new_data = np.mean(dax[:,min_y:max_y,min_x:max_x], axis=(1,2))
            dft_data = np.abs(np.fft.rfft(new_data))[1:]
#            fit = np.array([mol['x'],mol['y'],mol['z'],mol['fr']])
            for l_idx,laser in enumerate(active_lasers):
                fit[4+l_idx] = dft_data[laser]
            locs[c_idx] = fit
            c_idx += 1
    return locs[:c_idx]

def calc_indiv_demods_old(mols, dax, lasers, im_size):
    active_lasers = [i for i,el in enumerate(lasers) if el]
    num_lasers = np.sum(lasers)
    fit = np.zeros(4+num_lasers)
    locs = np.zeros([mols.shape[0],4+num_lasers])
    c_idx = 0
    for m_idx,mol in enumerate(mols):
        fit[0:4] = np.array([mol['x'],mol['y'],mol['z'],mol['fr']])
        x = np.round(mol['x'])
        y = np.round(mol['y'])
        s = 3
        min_x = int(np.max([x-(s//2)-1,0]))
        max_x = int(np.min([x+(s//2),im_size]))
        min_y = int(np.max([y-(s//2)-1,0]))
        max_y = int(np.min([y+(s//2),im_size]))
        if max_x-min_x > 0 and max_y-min_y > 0:
            dft_data = np.zeros([len(lasers),max_x-min_x,max_y-min_y])
            new_data = dax[:,min_y:max_y,min_x:max_x]
            for idx_y in range(new_data.shape[1]):
                for idx_x in range(new_data.shape[2]):
                    dft_data[:,idx_x,idx_y] = np.abs(np.fft.rfft(new_data[:,idx_y,idx_x]))[1:]
#            new_data = np.mean(dax[:,min_y:max_y,min_x:max_x], axis=(1,2))
#            dft_data = np.abs(np.fft.rfft(new_data))[1:]
#            fit = np.array([mol['x'],mol['y'],mol['z'],mol['fr']])
            for l_idx,laser in enumerate(active_lasers):
                fit[4+l_idx] = np.mean(dft_data[laser])
            locs[c_idx] = fit
            c_idx += 1
    return locs[:c_idx]