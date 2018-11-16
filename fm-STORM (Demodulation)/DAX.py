import numpy as np

class DAX(object):
    """
    A DAX file contains image data that is saved in a big-endian, uint16
    file format. There is no metadata in a DAX file, so the file size 
    should equal: #frames * frame_width * frame_height * 2
    
    Each DAX file has a corresponding INF file associated with it which
    provides the metadata (e.g., number of frames, frame width, frame height)
    that are necessary to be able to read frames from the DAX file. The
    INF file must have the same filename as the DAX file
    
    example: 
    /my/path/filename.dax 
    /my/path/filename.inf
    """
    
    _hRead = None
    _hWrite = None
    
    def close(self, infPath=None):
        """Closes the file handle"""
        if self._hRead is not None:
            self._hRead.close()
            self._hRead = None

        if self._hWrite is not None:
            self._hWrite.close()
            self._hWrite = None
            
            # create the default INF file
            inf = open(self._filename[:-3] + "inf", "w")
            inf.write('DAX_file_path = %s\n' % self._filename)
            inf.write('DAX_data_type = "I16_big_endian"\n')
            inf.write("binning = 1 x 1\n")
            inf.write("binning = 1\n")
            inf.write("frame_X_size = %d\n" % self._width)
            inf.write("frame_Y_size = %d\n" % self._height)
            inf.write("frame dimensions = %d x %d\n" % (self._width, self._height))
            inf.write("number_of_frames = %d\n" % self._numFrames)
            inf.write("number of frames = %d\n" % self._numFrames)
            inf.close()
        
    def open(self, filename):
        """
        Opens the DAX file
        
        Inputs
        ------
        filename : string
            the absolute path of the DAX file
        
        Raises
        ------
        IOError if the DAX or the INF file does not exist
        """        
        self._hRead = open(filename, "rb")
        
        # fetch the metadata from the INF file
        with open(filename[:-3] + "inf") as f:
            self._modFreqs = []
            self._laserWavelengths = []
            for line in f:
                key, value = line.partition(" = ")[::2]
                key = key.strip()
                value = value.strip()
                if key == "frame dimensions":
                    self._width, self._height = map(int, value.split("x"))
                    self._count = self._width * self._height
                elif key.strip() == "Frame_Rate":
                    self._frameRate = float(value)
                elif key.strip().lower() == "machine_name":
                    if value[1:-1] == 'STORM2':
                        self._pixelSize = 157
                    elif value[1:-1] == 'STORM3':
                        self._pixelSize = 155
                    else:
                        print("ERROR in _pixelSize")
                        self._pixelSize = None
                elif key == "number of frames":
                    self._numFrames = int(value)
                elif key.strip().lower() == "exposure_time":
                    self._exposureTime = float(value)
                elif 'frequency' in key.strip().lower() and float(value) > 0.1:
                    self._modFreqs.append(float(value))
                    self._laserWavelengths.append(key.strip()[0:3])
        self._filename = filename
         
    def read(self, frameIndex):
        """
        Reads the pixel values for the specified frame index.
        
        Inputs
        ------
        frameIndex : int
            the first frame has an index value of 0
        
        Returns
        -------
        A 2D, uint16 numpy array
        
        Raises
        ------
        ValueError if the frame index is invalid
        """
        if (frameIndex > -1) and (frameIndex < self._numFrames):
            self._hRead.seek(frameIndex * self._count * 2)
            pixels = np.fromfile(self._hRead, dtype=np.uint16, count=self._count).reshape((self._height, self._width))
            pixels.byteswap(True) # big-endian
            return pixels
        else:
            raise ValueError("Invalid frameIndex %d (acceptable range is 0 <= frameIndex < %d)" % (frameIndex, self._numFrames))

    def create(self, filename):
        """
        Create or overwrite a DAX file. 

        Inputs
        ------
        filename : string
            the absolute path of the DAX file
        """
        self._hWrite = open(filename, "wb")
        self._numFrames = 0
        self._filename = filename
    
    def write(self, frame):
        """
        Write the pixel values for this frame to the file
        
        Inputs
        ------
        frame : numpy ndarray
          The pixel values        
        """
        if self._numFrames == 0:
            self._height, self._width = frame.shape
        elif (self._height, self._width) != frame.shape:
            raise TypeError("The frame must have dimensions %d x %d. Got %d x %d" 
                            % (self._width, self._height, frame.shape[1], frame.shape[0])) 
        
        image16 = frame.astype(np.uint16)
        image16.byteswap(True)
        image16.tofile(self._hWrite)
        self._numFrames += 1
        
    @property
    def filename(self):
        """Returns the filename"""
        return self._filename
        
    @property
    def width(self):
        """Returns the image width, in pixels"""
        return self._width

    @property
    def height(self):
        """Returns the image height, in pixels"""
        return self._height

    @property
    def numFrames(self):
        """Returns the total number of frames in the DAX file"""
        return self._numFrames
        
    @property
    def frameRate(self):
        """Returns the real frame rate of the camera"""
        return self._frameRate
        
    @property
    def pixelSize(self):
        """Returns the physical pixel size in nanometers"""
        return self._pixelSize
        
    @property
    def exposureTime(self):
        """Returns the exposure time of one frame"""
        return self._exposureTime
        
    @property
    def laserWavelengths(self):
        """Returns the laser wavelengths used in the experiment"""
        return self._laserWavelengths
        
    @property
    def modFreqs(self):
        """Returns the modulations frequencies of the lasers"""
        return self._modFreqs
        
if __name__ == "__main__":
    
    filename = r"\\files\Groups\ICFO\Users File Sharing\Jason_O\Erik G\BJ_DNA-Cy3_cell1_conv_000.dax"
    
    daxIn = DAX()
    daxIn.open(filename)
    
    print("filename  = " + daxIn.filename)
    print("numFrames = %d" % daxIn.numFrames)
    print("width     = %d" % daxIn.width)
    print("height    = %d" % daxIn.height)

    daxOut = DAX()
    daxOut.create(filename[:-4]+"_new.dax") 
     
    # write every other frame to the new dax file
    for i in range(0, daxIn.numFrames, 2):
        daxOut.write( daxIn.read(i) )
     
    daxIn.close()
    daxOut.close()
        
        
        
        
