""" some image manipulation functions like scaling, rotating, etc...

"""

from __future__ import print_function, unicode_literals, absolute_import, division
import logging
logger = logging.getLogger(__name__)

import os
import numpy as np
from gputools import OCLArray, OCLImage, OCLProgram, get_device
from gputools import OCLElementwiseKernel

from ._abspath import abspath


def _scale_shape(dshape, scale = (1,1,1)):
    """returns the shape after scaling"""
    nshape = np.round(np.array(dshape) * np.array(scale))
    return tuple(nshape.astype(np.int))


def scale(data, scale = (1.,1.,1.), interpolation = "linear"):
    """returns a interpolated, scaled version of data

    scale = (scale_z,scale_y,scale_x)
    or
    scale = scale_all

    interp = "linear" | "nearest"
    """

    if not (isinstance(data, np.ndarray) and data.ndim == 3):
        raise ValueError("input data has to be a 3d array!")

    interpolation_defines = {"linear": ["-D", "SAMPLER_FILTER=CLK_FILTER_LINEAR"],
                             "nearest": ["-D", "SAMPLER_FILTER=CLK_FILTER_NEAREST"]}

    if not interpolation in interpolation_defines:
        raise KeyError(
            "interpolation = '%s' not defined ,valid: %s" % (interpolation, list(interpolation_defines.keys())))


    options_types = {np.uint8:["-D","TYPENAME=uchar","-D","READ_IMAGE=read_imageui"],
                    np.uint16: ["-D","TYPENAME=short","-D", "READ_IMAGE=read_imageui"],
                    np.float32: ["-D","TYPENAME=float", "-D","READ_IMAGE=read_imagef"],
                    }

    dtype = data.dtype.type

    if not dtype in options_types:
        raise ValueError("type %s not supported! Available: %s"%(dtype ,str(list(options_types.keys()))))


    if not isinstance(scale,(tuple, list, np.ndarray)):
        scale = (scale,)*3

    if len(scale) != 3:
        raise ValueError("scale = %s misformed"%scale)

    d_im = OCLImage.from_array(data)

    nshape = _scale_shape(data.shape,scale)

    res_g = OCLArray.empty(nshape,dtype)


    prog = OCLProgram(abspath("kernels/scale.cl"),
                      build_options=interpolation_defines[interpolation]+options_types[dtype ])


    prog.run_kernel("scale",
                    res_g.shape[::-1],None,
                    d_im,res_g.data)

    return res_g.get()




if __name__ == '__main__':
    
    d = np.zeros((100,100,100),np.float32)
    d[10:-10,10:-10,10:-10] = 1.

    res = scale(d,1.7, interp = "linear")
    # res = scale(d)

    
    
