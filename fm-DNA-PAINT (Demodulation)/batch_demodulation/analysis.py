import DAX
import numpy as np
import math
from numba import autojit

class Analysis:
    def __init__(self, data, params):
        self.data = data.data
        self.parameters = data.parameters
        self.parameters['n_frames'] = params[0]
        self.parameters['d_width'] = params[1]
        self.parameters['d_number'] = math.floor(params[0]/params[1])

    @autojit
    def calc_dft(self):
        _d_n = self.parameters['d_number']
        _d_w = self.parameters['d_width']
        windowed_dft = np.zeros([self.parameters['num_lasers'],
                    self.parameters['d_number'],
                    self.parameters['height'],
                    self.parameters['width']])
        self.centers_dft = self.find_centers(_d_w)
        start_index = 0
        end_index = _d_w
        for i in range(_d_n):
            for index in np.ndindex(self.parameters['height'], self.parameters['width']):
                _dfft = np.fft.rfft(self.data[start_index:end_index, index[1], index[0]])
                for l in range(self.parameters['num_lasers']):
                    windowed_dft[l,i,index[1],index[0]] = 2*np.abs(_dfft[self.centers_dft[l]])/_d_w
            start_index = end_index
            end_index += _d_w
        return windowed_dft

    def find_centers(self, num_time_points):
        times = np.linspace(0, int(num_time_points)/self.parameters['frame_rate'], 
                num_time_points)
        freqs = np.fft.fftfreq(num_time_points, 1/self.parameters['frame_rate'])
        fft_total = np.zeros([freqs.shape[0]])
        centers = np.zeros([self.parameters['num_lasers']])
        for idx, freq in enumerate(self.parameters['mod_freqs']):
            centers[idx] = np.abs(freqs-freq).argmin()
        return centers
            
    def save_batch(self, index):
        for channel in range(self.parameters['num_lasers']):
            filepath = self.parameters['dir']+self.parameters['name'][:-4]+'_demod'+str(channel)+'_block'+str(index)+'.dax'
            print('Created ' + filepath)
            dax = DAX.DAX()
            dax.create(filepath)
            for i in range(self.windowed_dft.shape[1]):
                dax.write(self.windowed_dft[channel][i])
            dax.close()
            
    def close(self):
        self.data = None
        self.parameters = None