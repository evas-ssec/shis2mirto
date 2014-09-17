#!/usr/bin/env python
# encoding: utf-8
"""Script that handles conversion from SHIS data to Mirto

:author:       Eva Schiffer (evas)
:contact:      eva.schiffer@ssec.wisc.edu
:organization: Space Science and Engineering Center (SSEC)
:copyright:    Copyright (c) 2014 University of Wisconsin SSEC. All rights reserved.
:date:         Sept 2014

Copyright (C) 2014 Space Science and Engineering Center (SSEC),
 University of Wisconsin-Madison.

This file is part of the shis2mirto software package.

    Written by Eva Schiffer    September 2014
    University of Wisconsin-Madison 
    Space Science and Engineering Center
    1225 West Dayton Street
    Madison, WI  53706
    eva.schiffer@ssec.wisc.edu

"""
__docformat__ = "restructuredtext en"

import sys, os, logging, pkg_resources
import netCDF4 as nc
import numpy as numpy

from shis2mirto.guidebook import *

log = logging.getLogger(__name__)

def get_version_string() :
    version_num = pkg_resources.require('shis2mirto')[0].version

    return "shis2mirto, version " + str(version_num)

def clean_path(string_path) :
    """
    Return a clean form of the path without any '.', '..', or '~'
    """
    clean_path = None
    if string_path is not None :
        clean_path = os.path.abspath(os.path.expanduser(string_path))

    return clean_path

def main(argv = sys.argv[1:]):
    import optparse
    usage = """
%prog [options]
run "%prog help" to list commands
examples:


"""

    # set the options available to the user on the command line
    parser = optparse.OptionParser(usage)


    # option to run a test
    parser.add_option('-t', '--test', dest="self_test",
                    action="store_true", default=False, help="run internal unit tests")

    # message related options
    parser.add_option('-q', '--quiet', dest="quiet",
                    action="store_true", default=False, help="only error output")
    parser.add_option('-v', '--verbose', dest="verbose",
                    action="store_true", default=False, help="enable more informational output")
    parser.add_option('-w', '--debug', dest="debug",
                    action="store_true", default=False, help="enable debug output")
    parser.add_option('-n', '--version', dest='version',
                      action="store_true", default=False, help="view program version")

    # input related options
    parser.add_option('-s', '--shis_in', dest="shis_input", type='string', default=None,
                      help="an input Scanning HIS radiance file")
    parser.add_option('-f', '--fov_base', dest="fov_base", type='string', default=None,
                      help="the base fov.nc file to use as a template")

    # output generation related options
    parser.add_option('-p', '--outputpath', dest='output', type='string', default='./',
                    help="set path to output directory")

    # data selection related options
    parser.add_option('-c', '--center_angle', dest="center_fov_angle", type='float', default=0.0,
                      help="the central fov angle that will be considered when searching for " +
                           "acceptable observations in the SHIS data; defaults to 0.0")
    parser.add_option('-r', '--angle_range', dest="fov_angle_range", type='float', default=1.5,
                      help="how far to either side of the central fov angle we will look when " +
                           "selecting acceptable observations in the SHIS data; defaults to 1.5 degrees")


    # parse the user options from the command line
    options, args = parser.parse_args()
    if options.self_test:
        import doctest
        doctest.testmod()
        sys.exit(2)

    # set up the logging level based on the options the user selected on the command line
    lvl = logging.WARNING
    if options.debug: lvl = logging.DEBUG
    elif options.verbose: lvl = logging.INFO
    elif options.quiet: lvl = logging.ERROR
    logging.basicConfig(level = lvl)

    # display the version
    if options.version :
        print (get_version_string() + '\n')

    commands = {}
    prior = None
    prior = dict(locals())

    ##################################################################
    # The following functions represent available menu selections
    ##################################################################

    def create_fov_file (*args) :
        """generate an fov file from an input SHIS data file

        This option generates a properly formatted fov.nc file from a Scanning HIS data file.

        Examples:
         python -m shis2mirto.shis2mirto create_fov_file
        """

        log.info("Generating FOV file from SHIS data")

        # we need SHIS input and a base FOV file to generate input
        if (options.shis_input is None) or (options.fov_base is None) :
            log.warn("Incomplete input, unable to generate FOV file")
            return

        # pull some things from the options
        center_angle  = options.center_fov_angle
        angle_range   = options.fov_angle_range
        shis_file     = nc.Dataset(clean_path(options.shis_input), 'r')
        fov_base_file = nc.Dataset(clean_path(options.fov_base),   'r')

        """ this was an attempt to create a test input fov file to pull wavenumbers out of

        temp_wave_ref = nc.Dataset("./temp/fov_wc.nc", 'w', format="NETCDF3_CLASSIC")
        temp_wave_ref.createDimension('wnum', None)
        temp_var = temp_wave_ref.createVariable('wavenumber', 'f8', ('wnum'))
        wnums_to_use = numpy.array(
            [ 581.951,  582.433837, 585.80886, 586.29101562, 586.77,  587.255,  593.5]
        )
        temp_var[0:wnums_to_use.size] = wnums_to_use
        temp_wave_ref.close()
        """

        desired_wnums = numpy.sort(fov_base_file.variables[INPUT_WAVE_NUMBER_VAR_NAME][:])
        log.debug("desired wave numbers: " + str(desired_wnums))

        # look through the wave numbers in the shis file and figure out the appropriately matching
        # indexes to the wave numbers we want
        found_indexes  = numpy.ones(desired_wnums.shape, dtype='int') * -1
        temp_wnums     = shis_file.variables[SHIS_WAVE_NUMBER_VAR_NAME][:]
        current_target = 0
        for index in range(0, temp_wnums.size - 1) :
            if current_target < found_indexes.size :
                desired = desired_wnums[current_target]
                if   desired == temp_wnums[index] :
                    found_indexes[current_target] = index
                    current_target += 1
                elif desired == temp_wnums[index + 1] :
                    found_indexes[current_target] = index + 1
                    current_target += 1
                elif (desired > temp_wnums[index]) and (desired < temp_wnums[index + 1]) :

                    if (desired - temp_wnums[index]) < (temp_wnums[index + 1] - desired) :
                        found_indexes[current_target] = index
                        current_target += 1
                    else :
                        found_indexes[current_target] = index + 1
                        current_target += 1

                    # TODO need to check the tolerance of this fit

        # if we were unable to find a matching wave number for any of the desired
        # wave numbers, stop now
        if numpy.min(found_indexes) < 0 :
            log.warn("Unable to find desired wave numbers in SHIS file")
            return

        # figure out where the acceptable fov angles fall
        temp_angles = shis_file.variables[SHIS_FOV_ANGLE_VAR_NAME][:]
        angle_mask  = (temp_angles >= (center_angle - angle_range)) & (temp_angles <= (center_angle + angle_range))
        num_obs     = numpy.sum(angle_mask)

        # find the global variables for our output fov file
        num_channels          = temp_wnums.size
        num_selected_channels = found_indexes.size

        log.debug("radiances shape:  " + str(shis_file.variables[SHIS_RADIANCE_VAR_NAME].shape))
        log.debug("num obs:          " + str(num_obs))
        log.debug("num channels:     " + str(num_channels))
        log.debug("num sel channels: " + str(num_selected_channels))

        # build the output file
        # TODO, check existence for dir and file
        out_fov_file = nc.Dataset(os.path.join(options.output, OUT_FOV_FILE_NAME), 'w', format="NETCDF3_CLASSIC")

        # create the global dimensions we're going to need
        out_fov_file.createDimension(OUT_FOV_OBS_NUM_DIM_NAME,               size=num_obs)
        out_fov_file.createDimension(OUT_FOV_NUM_CHANNELS_DIM_NAME,          size=num_channels)
        out_fov_file.createDimension(OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME, size=num_selected_channels)

        # put in the longitude and latitude variables
        temp_lon = shis_file.variables[SHIS_LON_VAR_NAME][angle_mask]
        temp_var = out_fov_file.createVariable(OUT_FOV_LON_VAR_NAME, 'f8', (OUT_FOV_OBS_NUM_DIM_NAME))
        temp_var[0:num_obs] = temp_lon
        temp_lat = shis_file.variables[SHIS_LAT_VAR_NAME] [angle_mask]
        temp_var = out_fov_file.createVariable(OUT_FOV_LAT_VAR_NAME,  'f8', (OUT_FOV_OBS_NUM_DIM_NAME))
        temp_var[0:num_obs] = temp_lat

        # put in the fov angles
        temp_fov_angles = temp_angles[angle_mask]
        temp_var = out_fov_file.createVariable(OUT_FOV_FOV_ANGLE_VAR_NAME, 'f8', (OUT_FOV_OBS_NUM_DIM_NAME))
        temp_var[0:num_obs] = temp_fov_angles

        # get the full list of radiances
        rad_shape          = shis_file.variables[SHIS_RADIANCE_VAR_NAME].shape
        # go through and pull out the appropriate observations
        all_obs_radiances = None
        for record_index in range(0, rad_shape[0]) :
            if angle_mask[record_index] :
                if all_obs_radiances is None:
                    all_obs_radiances = shis_file.variables[SHIS_RADIANCE_VAR_NAME][record_index]
                else :
                    all_obs_radiances = numpy.append(all_obs_radiances, shis_file.variables['radiance'][record_index])
        all_obs_radiances = numpy.reshape(all_obs_radiances, (num_obs, num_channels))
        """ TODO, why doesn't this strategy work?
        temp_angle_mask_3d = numpy.reshape(numpy.tile(numpy.reshape(angle_mask, (1,angle_mask.size)), rad_shape[0]), rad_shape) # make a mask for the radiances corresponding to the good fov angles
        print("3d angle mask shape:  " + str(temp_angle_mask_3d.shape))
        all_obs_radiances = numpy.reshape(shis_file.variables[SHIS_RADIANCE_VAR_NAME][temp_angle_mask_3d], (num_obs, num_channels))
        """
        temp_var = out_fov_file.createVariable(OUT_FOV_RADIANCE_VAR_NAME, 'f8', (OUT_FOV_OBS_NUM_DIM_NAME, 'channels'))
        temp_var[0:num_obs, 0:num_channels] = all_obs_radiances

        # get the full list of wave numbers
        temp_all_wavenums = shis_file.variables[SHIS_WAVE_NUMBER_VAR_NAME][:]
        temp_var = out_fov_file.createVariable(OUT_FOV_WAVE_NUMBER_VAR_NAME, 'f8', (OUT_FOV_NUM_CHANNELS_DIM_NAME))
        temp_var[0:num_channels] = temp_all_wavenums

        # get the selected wave numbers
        selected_wavenums = temp_all_wavenums[found_indexes]
        temp_var = out_fov_file.createVariable(OUT_FOV_SELECTED_WAVE_NUMBER_VAR_NAME, 'f8', (OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME))
        temp_var[0:num_selected_channels] = selected_wavenums

        # get the indexes of the selected channels
        temp_var = out_fov_file.createVariable(OUT_FOV_SELECTED_CHANNEL_IDX_VAR_NAME, 'f8', (OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME))
        temp_var[0:num_selected_channels] = found_indexes

        # get just the selected radiances
        selected_radiances = None
        for obs_number in range(0, num_obs) :
            if selected_radiances is None:
                selected_radiances = all_obs_radiances[obs_number][found_indexes]
            else :
                selected_radiances = numpy.append(selected_radiances, all_obs_radiances[obs_number][found_indexes])
        selected_radiances = numpy.reshape(selected_radiances, (num_obs, num_selected_channels))
        temp_var = out_fov_file.createVariable(OUT_FOV_SELECTED_RADIANCE_VAR_NAME, 'f8',
                                               (OUT_FOV_OBS_NUM_DIM_NAME, OUT_FOV_NUM_SELECTED_CHANNELS_DIM_NAME))
        temp_var[0:num_obs, 0:num_selected_channels] = selected_radiances

        # close the file
        out_fov_file.close()

        log.info("Finished saving fov.nc to file")

    def help(command=None):
        """print help for a specific command or list of commands
        e.g. help stats
        """
        if command is None:
            # print first line of docstring
            for cmd in commands:
                ds = commands[cmd].__doc__.split('\n')[0]
                print "%-16s %s" % (cmd,ds)
        else:
            print commands[command].__doc__

    # all the local public functions are considered part of this script, collect them up
    commands.update(dict(x for x in locals().items() if x[0] not in prior))

    # if what the user asked for is not one of our existing functions, print the help
    if (not args) or (args[0] not in commands):
        parser.print_help()
        help()
        return 9
    else:
        # call the function the user named, given the arguments from the command line
        rc = locals()[args[0]](*args[1:])
        return 0 if rc is None else rc

if __name__ == "__main__":
    sys.exit(main())

