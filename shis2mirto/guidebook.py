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
import numpy

log = logging.getLogger(__name__)

# constants for the input wave numbers file
INPUT_WAVE_NUMBER_VAR_NAME             = 'wavenumber'

# constants for the input pressure levels file
INPUT_PRESSURE_LEVELS_VAR_NAME         = 'PressureLevels'

# constants for the SHIS data file
SHIS_WAVE_NUMBER_VAR_NAME              = 'wavenumber'
SHIS_FOV_ANGLE_VAR_NAME                = 'FOVangle'
SHIS_RADIANCE_VAR_NAME                 = "radiance"
SHIS_LON_VAR_NAME                      = 'Longitude'
SHIS_LAT_VAR_NAME                      = 'Latitude'
SHIS_BASE_TIME_VAR_NAME                = "base_time"
SHIS_TIME_OFFSET_VAR_NAME              = "time_offset"

# constants for the output fov.nc file
OUT_FOV_FILE_NAME                      = "fov.nc"
OUT_FOV_OBS_NUM_DIM_NAME               = 'obsnum'
OUT_FOV_NUM_CHANNELS_DIM_NAME          = "channels"
OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME = "selected_channels"
OUT_FOV_LON_VAR_NAME                   = 'Longitude'
OUT_FOV_LAT_VAR_NAME                   = 'Latitude'
OUT_FOV_BASE_TIME_VAR_NAME             = "base_time"
OUT_FOV_TIME_OFFSET_VAR_NAME           = "time_offset"
OUT_FOV_MATLAB_DATENUM_TIME_VAR_NAME   = "TimeFracDay"
OUT_FOV_FOV_ANGLE_VAR_NAME             = 'FOVangle'
OUT_FOV_RADIANCE_VAR_NAME              = 'Radiance'
OUT_FOV_WAVE_NUMBER_VAR_NAME           = "Wavenumber"
OUT_FOV_SELECTED_WAVE_NUMBER_VAR_NAME  = "SelWavenumber"
OUT_FOV_SELECTED_CHANNEL_IDX_VAR_NAME  = "indxselchannel"
OUT_FOV_SELECTED_RADIANCE_VAR_NAME     = "selradiances"

# constants from the virtual radiosonde data
VR_INPUT_DATETIME_KEY                  = 'datetime'
VR_INPUT_LON_KEY                       = 'longitude'
VR_INPUT_LAT_KEY                       = 'latitude'
VR_TEMPERATURE_KEY                     = 'tdry'
VR_PRESSURE_KEY                        = 'pres'

# constants for the output fg.nc file
OUT_FG_FILE_NAME                       = "fg.nc"
OUT_FG_NUM_STATEVAR_DIM_NAME           = "numstatevar"
OUT_FG_OBS_NUM_DIM_NAME                = "obsnum"
OUT_FG_STATEVAR_DIMS_DIM_NAME          = "dims"
OUT_FG_NUM_SELECTED_STATEVAR_DIM_NAME  = "numselstatevar"
OUT_FG_LIN_POINT_VAR_NAME              = 'xa'
OUT_FG_FIRST_GUESS_STATE_VEC_VAR_NAME  = 'x0'
OUT_FG_PRESSURE_GRID_VAR_NAME          = 'p'
OUT_FG_STATE_VECTOR_DIMS_VAR_NAME      = 'xdim'
OUT_FG_SEL_STATE_VECTOR_IDX_VAR_NAME   = 'varindx'
OUT_FG_SEL_LIN_POINT_VAR_NAME          = 'selxa'
OUT_FG_SEL_FG_STATE_VEC_VAR_NAME       = 'selx0'
OUT_FG_SEL_PRESSURE_GRID_VAR_NAME      = 'selp'

# science constants
SURFACE_EMISSIVITY_COEFFICIENTS        = numpy.array([numpy.nan, numpy.nan, numpy.nan, numpy.nan ,numpy.nan]) # todo get constants from Paolo
CELSIUS_TO_KELVIN_ADD_CONST            = -273.15
C02_CONST_STARTING_PT_IN_PPMV          = 394.0

def main():

    return 0 # nothing should be calling this

if __name__ == '__main__':
    sys.exit(main())
