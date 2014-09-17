#!/usr/bin/env python
# encoding: utf-8
"""
Provide constants for a variety of uses.

:author:       Eva Schiffer (evas)
:contact:      eva.schiffer@ssec.wisc.edu
:organization: Space Science and Engineering Center (SSEC)
:copyright:    Copyright (c) 2014 University of Wisconsin SSEC. All rights reserved.
:date:         Sept 2014

Copyright (C) 2014 Space Science and Engineering Center (SSEC),
 University of Wisconsin-Madison.

This file is part of the shis2mirto software package. The guidebook is used to store
constants that are shared throughout the package.

"""
__docformat__ = "restructuredtext en"

import sys
import logging

log = logging.getLogger(__name__)

# constants for the input fov file
INPUT_WAVE_NUMBER_VAR_NAME             = 'wavenumber'

# constants for the SHIS data file
SHIS_WAVE_NUMBER_VAR_NAME              = 'wavenumber'
SHIS_FOV_ANGLE_VAR_NAME                = 'FOVangle'
SHIS_RADIANCE_VAR_NAME                 = "radiance"
SHIS_LON_VAR_NAME                      = 'Longitude'
SHIS_LAT_VAR_NAME                      = 'Latitude'

# constants for the output fov.nc file
OUT_FOV_FILE_NAME                      = "fov.nc"
OUT_FOV_OBS_NUM_DIM_NAME               = 'obsnum'
OUT_FOV_NUM_CHANNELS_DIM_NAME          = "channels"
OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME = "selected_channels"
OUT_FOV_LON_VAR_NAME                   = 'Longitude'
OUT_FOV_LAT_VAR_NAME                   = 'Latitude'
OUT_FOV_FOV_ANGLE_VAR_NAME             = 'FOVangle'
OUT_FOV_RADIANCE_VAR_NAME              = 'Radiance'
OUT_FOV_WAVE_NUMBER_VAR_NAME           = "Wavenumber"
OUT_FOV_SELECTED_WAVE_NUMBER_VAR_NAME  = "SelWavenumber"
OUT_FOV_SELECTED_CHANNEL_IDX_VAR_NAME  = "indxselchannel"
OUT_FOV_SELECTED_RADIANCE_VAR_NAME     = "selradiances"

def main():

    return 0 # nothing should be calling this

if __name__ == '__main__':
    sys.exit(main())
