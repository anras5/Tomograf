import numpy as np
import scipy.signal as sig


def filter_h(sinogram):
    shape = np.shape(sinogram)
    filtered_sinogram = []
    for i in range(0, shape[0]):
        filtered_sinogram.append(
            sig.convolve(sinogram[i],
                         [-4 / (9 * np.pi ** 2),
                          0,
                          -4 / np.pi ** 2,
                          1,
                          -4 / np.pi ** 2,
                          0,
                          -4 / (9 * np.pi ** 2)],
                         mode='same', method='direct')
        )

    return np.array(filtered_sinogram)
