#****
#TODO:
# __critical__
# test calculation gps and orientation
# fix interface to camera on plane
#
# __medium__
# fix add manually
#****

#Camera.py

from numpy import matrix

class Camera(object):
    """class that defines a "Camera", which is just the
    intrinsic matrix for a camera.  Intrinsic parametrs should
    be calculated using the Caltech Calibration Toolbox for Matlab"""
    
    # variables
    fc1 = 0
    fc2 = 0
    cc1 = 0
    cc2 = 0
    alpha_c = 0
    
    def set_params(self, fc1, fc2, cc1, cc2, alpha_c):
        self.fc1 = fc1
        self.fc2 = fc2
        self.cc1 = cc1
        self.cc2 = cc2
        self.alpha_c = alpha_c
    
    def get_intrinsic_matrix(self):
        return matrix([[ self.fc1, self.alpha_c*self.fc1, self.cc1 ],\
                      [ 0,         self.fc2,             self.cc2 ],\
                      [ 0,         0,                    1        ]])
