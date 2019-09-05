import numpy as np
from convolution_cpp_lib import matrix_convolution
from scipy.signal import convolve2d

a = np.array([[1,0,0,0],
              [0,0,0,0],
              [0,0,0,0],
              [0,0,0,0]])
b = np.array([[0,1,0,0],
              [0,0,0,0],
              [0,0,0,0],
              [0,0,0,0]])

bb = np.array([[0,1,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],

              [0,0,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],
              [0,0,0,0 ,0,0,0,0],
])

print(convolve2d(a,b))
# print("b fft2= ")
# print(np.fft.fft2(bb))
print()
print(matrix_convolution(a.astype(float),b.astype(float)))



