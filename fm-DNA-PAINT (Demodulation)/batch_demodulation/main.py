import storm
import analysis
import DAX
import os
import numpy as np
from timeit import default_timer as timer

def calc_window_size(num_lasers, mod_freqs, frame_rate, nyquist):
    if nyquist:
        if num_lasers == 1:
            window_size = 6
        elif num_lasers == 2:
            window_size = 6
        elif num_lasers == 3:
            window_size = 6
        elif num_lasers == 4:
            window_size = 6
    else:
        if num_lasers == 1:
            window_size = 6
        elif num_lasers == 2:
            window_size = 6
        elif num_lasers == 3:
            window_size = 6
        elif num_lasers == 4:
            window_size = 6
    return window_size

def main():
    # Replace the directory below with the top-level directory of the data sets
    dir = 'E:/ICFO - AFIB/Raid3 (Data)/Multiplexing STORM ALL Data [#####]/STORM DNA-PAINT 2 Color/170405_DNA-paint_MSTORM_Comparison -100ms and 16ms/Overllaped 561nm plus 647nm/'
    dir_exts = os.listdir(dir)
    # print(dir_exts)
    chunk_size = 50000

    for dir_ext in dir_exts:
        names = os.listdir(dir + dir_ext)
        for name in names:
            if name[-4:] == '.dax':
                daxIn = DAX.DAX()
                daxIn.open(dir + dir_ext + '/' + name)
                _num_frames = daxIn.numFrames
                _num_lasers = len(daxIn.laserWavelengths[::-1])
                _mod_freqs = daxIn.modFreqs
                _frame_rate = daxIn.frameRate
                daxIn.close()
                if _num_frames > 100:
                    num_chunks = _num_frames//chunk_size
                    # num_chunks = 10
                    if np.max(_mod_freqs) > 0.48*_frame_rate and np.max(_mod_freqs) < 0.52*_frame_rate:
                        nyquist = True
                    else:
                        nyquist = False
                    dft_window_width = calc_window_size(_num_lasers, _mod_freqs, _frame_rate, nyquist)
                    print(name[:-4]+'_demod_'+str(dft_window_width)+'_frame_window')
                    daxOut = [DAX.DAX() for i in range(_num_lasers)]
                    for i in range(_num_lasers):
                        daxOut[i].create(dir+dir_ext+'/'+name[:-4]+'_demod'+str(i)+'_'+str(dft_window_width)+'_frame_window.dax')
                    start_frame = 0
                    for i in range(num_chunks):
                        data = storm.STORM(start = start_frame, frames = chunk_size)
                        data.parameters['dir'] = dir + dir_ext + '/'
                        data.parameters['name'] = name
                        load_success = data.load()
                        
                        storm_analysis = analysis.Analysis(data, [chunk_size,dft_window_width])
                        start_time = timer()
                        analysis_return = storm_analysis.calc_dft()
                        dt = timer() - start_time
                        print('Analysis finished in %f s' % dt)
                        for j in range(_num_lasers):
                            for k in range(storm_analysis.parameters['d_number']):
                                daxOut[j].write(analysis_return[j][k])
                        print('Chunk '+str(i+1)+' of '+str(num_chunks)+' completed.')
                        storm_analysis.close()
                        data.close()
                        start_frame += chunk_size
                    for i in range(_num_lasers):
                        daxOut[i].close()

if __name__ == '__main__':
    main()