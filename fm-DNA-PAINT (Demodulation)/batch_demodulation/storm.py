import DAX
import numpy as np
import math

class STORM:
    def __init__(self, start, frames):
        self.parameters = {}
        self.start = start
        self.frames = frames
        self.parameters['width'] = 0
        self.parameters['height'] = 0
        self.parameters['num_frames'] = 0
        self.parameters['frame_rate'] = 0.0
        self.parameters['measurement_time'] = 0.0
        self.parameters['laser_wavelengths'] = []
        self.parameters['mod_freqs'] = []
        self.parameters['num_lasers'] = len(self.parameters['laser_wavelengths'])
        
    def load(self):
        self.filepath = self.parameters['dir'] + self.parameters['name']
        dax = DAX.DAX()
        dax.open(self.filepath)
        if dax.numFrames < self.start+self.frames:
            self.parameters['num_frames'] = dax.numFrames-self.start
        else:
            self.parameters['num_frames'] = self.frames
        self.parameters['width'] = dax.width
        self.parameters['height'] = dax.height
        self.parameters['image_size'] = dax.width
        self.parameters['frame_rate'] = dax.frameRate
        self.parameters['pixel_size'] = dax.pixelSize
        self.parameters['measurement_time'] = dax.exposureTime
        self.parameters['laser_wavelengths'] = dax.laserWavelengths[::-1]
        self.parameters['mod_freqs'] = dax.modFreqs[::-1]
        self.parameters['num_lasers'] = len(self.parameters['laser_wavelengths'])
        self.data = np.zeros([self.parameters['num_frames'],
                                self.parameters['height'],
                                self.parameters['width']])
        for frame in range(self.start, self.start+self.parameters['num_frames']):
            self.data[frame-self.start] = dax.read(frame)
        dax.close()
        return True
        
    def close(self):
        self.data = None
        self.parameters = None