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
from datetime import datetime, timedelta

import virtual_radiosonde_source.vrsNarrator as radiosonde

from shis2mirto.guidebook import *

log = logging.getLogger(__name__)

def datetime_to_matlab_datenum (time):

    base_date_num      = (time + timedelta(days = 366)).toordinal()
    additional_seconds = (time - datetime(time.year, time.month, time.day, 0, 0, 0)).seconds / (24.0 * 60.0 * 60.0)
    final_datenum      = base_date_num + additional_seconds

    return final_datenum

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
    parser.add_option('-a', '--wave_num_in', dest="wnum_input", type='string', default=None,
                      help="an input file listing the wave numbers to be used in fov file creation")
    parser.add_option('-p', '--pressure_lvls', dest="plevels_input", type='string', default=None,
                      help="an input file listing the pressure levels to be used in fg file creation")
    parser.add_option('-f', '--fov_base', dest="fov_base", type='string', default=None,
                      help="the base fov.nc file to use")

    # output generation related options
    parser.add_option('-o', '--outputpath', dest='output', type='string', default='./',
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

    def build_test_wc_file (*args) :
        """create a file containing input wavenumbers for use by create_fov_file

        :param args:
        :return:
        """

        log.info("Generating input wavenumber file for testing")

        wavenumbers_list = numpy.array(
            [[    670.   ,   670.625,   671.25 ,   671.875,   672.5  ,   673.125,
                  673.75 ,   674.375,   675.   ,   675.625,   676.25 ,   676.875,
                  677.5  ,   678.125,   678.75 ,   679.375,   680.   ,   680.625,
                  681.25 ,   681.875,   682.5  ,   683.125,   683.75 ,   684.375,
                  685.   ,   685.625,   686.25 ,   686.875,   687.5  ,   688.125,
                  688.75 ,   689.375,   690.   ,   690.625,   691.25 ,   691.875,
                  692.5  ,   693.125,   693.75 ,   694.375,   695.   ,   695.625,
                  696.25 ,   696.875,   697.5  ,   698.125,   698.75 ,   699.375,
                  700.   ,   700.625,   701.25 ,   701.875,   702.5  ,   703.125,
                  703.75 ,   704.375,   705.   ,   705.625,   706.25 ,   707.5  ,
                  708.125,   708.75 ,   709.375,   710.   ,   710.625,   711.25 ,
                  711.875,   712.5  ,   713.125,   713.75 ,   714.375,   715.   ,
                  715.625,   716.25 ,   716.875,   717.5  ,   718.125,   718.75 ,
                  719.375,   720.   ,   720.625,   721.25 ,   721.875,   722.5  ,
                  723.125,   723.75 ,   724.375,   725.   ,   725.625,   726.25 ,
                  726.875,   727.5  ,   728.125,   728.75 ,   729.375,   730.   ,
                  730.625,   731.25 ,   732.5  ,   733.125,   733.75 ,   734.375,
                  735.   ,   735.625,   736.25 ,   736.875,   737.5  ,   738.125,
                  738.75 ,   739.375,   740.   ,   740.625,   741.25 ,   741.875,
                  742.5  ,   743.125,   743.75 ,   744.375,   745.   ,   745.625,
                  746.25 ,   746.875,   747.5  ,   748.125,   748.75 ,   749.375,
                  750.   ,   750.625,   751.25 ,   751.875,   752.5  ,   753.125,
                  753.75 ,   754.375,   755.   ,   755.625,   756.25 ,   756.875,
                  757.5  ,   758.125,   758.75 ,   759.375,   760.   ,   760.625,
                  761.25 ,   761.875,   762.5  ,   763.125,   763.75 ,   764.375,
                  765.   ,   766.25 ,   766.875,   767.5  ,   768.125,   768.75 ,
                  769.375,   770.   ,   770.625,   771.25 ,   771.875,   772.5  ,
                  773.125,   773.75 ,   774.375,   775.   ,   775.625,   776.25 ,
                  776.875,   777.5  ,   778.125,   778.75 ,   779.375,   780.   ,
                  780.625,   781.25 ,   781.875,   782.5  ,   783.125,   783.75 ,
                  784.375,   785.   ,   785.625,   786.25 ,   786.875,   787.5  ,
                  788.125,   788.75 ,   789.375,   790.   ,   790.625,   791.25 ,
                  791.875,   792.5  ,   793.125,   793.75 ,   794.375,   795.   ,
                  795.625,   796.25 ,   796.875,   797.5  ,   798.125,   798.75 ,
                  799.375,   800.   ,   800.625,   801.25 ,   801.875,   802.5  ,
                  803.125,   803.75 ,   804.375,   805.   ,   805.625,   806.25 ,
                  806.875,   807.5  ,   808.125,   808.75 ,   809.375,   810.   ,
                  810.625,   811.25 ,   811.875,   812.5  ,   813.125,   813.75 ,
                  814.375,   815.   ,   815.625,   816.25 ,   816.875,   817.5  ,
                  818.75 ,   820.   ,   820.625,   821.25 ,   821.875,   822.5  ,
                  823.125,   823.75 ,   824.375,   825.   ,   825.625,   826.25 ,
                  826.875,   827.5  ,   828.125,   828.75 ,   829.375,   830.   ,
                  830.625,   831.25 ,   832.5  ,   833.125,   833.75 ,   834.375,
                  835.   ,   835.625,   836.25 ,   837.5  ,   838.125,   838.75 ,
                  839.375,   840.   ,   840.625,   841.25 ,   841.875,   842.5  ,
                  843.125,   843.75 ,   844.375,   845.   ,   845.625,   846.25 ,
                  846.875,   847.5  ,   848.125,   848.75 ,   849.375,   850.   ,
                  850.625,   851.25 ,   851.875,   852.5  ,   853.125,   853.75 ,
                  854.375,   855.   ,   855.625,   856.25 ,   856.875,   857.5  ,
                  858.125,   858.75 ,   859.375,   860.   ,   860.625,   861.25 ,
                  861.875,   862.5  ,   863.125,   863.75 ,   864.375,   865.   ,
                  865.625,   866.25 ,   866.875,   867.5  ,   868.125,   868.75 ,
                  869.375,   870.   ,   870.625,   871.25 ,   871.875,   872.5  ,
                  873.125,   873.75 ,   874.375,   875.   ,   875.625,   876.25 ,
                  876.875,   877.5  ,   878.125,   878.75 ,   879.375,   880.   ,
                  880.625,   881.25 ,   881.875,   882.5  ,   883.125,   883.75 ,
                  884.375,   885.   ,   885.625,   886.25 ,   886.875,   887.5  ,
                  888.125,   888.75 ,   889.375,   890.   ,   890.625,   891.25 ,
                  891.875,   892.5  ,   893.125,   893.75 ,   894.375,   895.   ,
                  895.625,   896.25 ,   896.875,   897.5  ,   898.125,   898.75 ,
                  899.375,   900.   ,   900.625,   901.25 ,   901.875,   902.5  ,
                  903.125,   903.75 ,   904.375,   905.   ,   905.625,   906.25 ,
                  906.875,   907.5  ,   908.125,   908.75 ,   909.375,   910.   ,
                  910.625,   911.25 ,   911.875,   912.5  ,   914.375,   915.   ,
                  916.25 ,   916.875,   918.75 ,   919.375,   920.   ,   920.625,
                  923.75 ,   924.375,   925.   ,   926.25 ,   927.5  ,   928.125,
                  931.875,   933.125,   933.75 ,   934.375,   935.   ,   935.625,
                  936.25 ,   936.875,   937.5  ,   938.125,   938.75 ,   939.375,
                  940.   ,   940.625,   941.25 ,   941.875,   942.5  ,   943.125,
                  943.75 ,   944.375,   945.   ,   945.625,   946.25 ,   946.875,
                  947.5  ,   948.125,   948.75 ,   949.375,   950.   ,   950.625,
                  951.25 ,   951.875,   952.5  ,   953.125,   953.75 ,   954.375,
                  955.   ,   955.625,   956.25 ,   956.875,   957.5  ,   958.125,
                  958.75 ,   959.375,   960.   ,   960.625,   961.25 ,   962.5  ,
                  963.125,   965.   ,   965.625,   966.25 ,   966.875,   967.5  ,
                  968.125,   968.75 ,   969.375,   970.   ,   970.625,   971.25 ,
                  971.875,   972.5  ,   973.125,   973.75 ,   974.375,   975.   ,
                  975.625,   976.25 ,   976.875,   977.5  ,   978.125,   978.75 ,
                  979.375,   980.   ,   980.625,   981.25 ,   981.875,   982.5  ,
                  983.125,   983.75 ,   984.375,   985.   ,   985.625,   986.25 ,
                  986.875,   987.5  ,   988.125,   988.75 ,   989.375,   990.   ,
                  990.625,   991.25 ,   991.875,   992.5  ,   993.125,   993.75 ,
                  994.375,   995.   ,   995.625,   996.25 ,   996.875,   997.5  ,
                  998.125,   998.75 ,   999.375,  1000.   ,  1000.625,  1001.25 ,
                 1001.875,  1002.5  ,  1003.125,  1003.75 ,  1004.375,  1005.   ,
                 1005.625,  1006.25 ,  1006.875,  1007.5  ,  1008.125,  1008.75 ,
                 1009.375,  1010.   ,  1010.625,  1011.25 ,  1011.875,  1012.5  ,
                 1013.125,  1013.75 ,  1014.375,  1015.   ,  1015.625,  1016.25 ,
                 1016.875,  1017.5  ,  1018.125,  1018.75 ,  1019.375,  1020.   ,
                 1020.625,  1021.25 ,  1021.875,  1022.5  ,  1023.125,  1023.75 ,
                 1024.375,  1025.   ,  1025.625,  1026.25 ,  1026.875,  1027.5  ,
                 1028.125,  1028.75 ,  1029.375,  1030.   ,  1030.625,  1031.25 ,
                 1031.875,  1032.5  ,  1033.125,  1033.75 ,  1034.375,  1035.   ,
                 1035.625,  1036.25 ,  1036.875,  1037.5  ,  1038.125,  1038.75 ,
                 1039.375,  1040.   ,  1040.625,  1041.25 ,  1041.875,  1042.5  ,
                 1043.125,  1043.75 ,  1044.375,  1045.   ,  1045.625,  1046.25 ,
                 1046.875,  1047.5  ,  1048.125,  1048.75 ,  1049.375,  1050.   ,
                 1050.625,  1051.25 ,  1051.875,  1052.5  ,  1053.125,  1053.75 ,
                 1054.375,  1055.   ,  1055.625,  1056.25 ,  1056.875,  1057.5  ,
                 1058.125,  1058.75 ,  1059.375,  1060.   ,  1060.625,  1061.25 ,
                 1061.875,  1062.5  ,  1063.125,  1063.75 ,  1064.375,  1065.   ,
                 1065.625,  1066.25 ,  1066.875,  1067.5  ,  1068.125,  1068.75 ,
                 1069.375,  1070.   ,  1070.625,  1071.25 ,  1071.875,  1072.5  ,
                 1073.125,  1073.75 ,  1074.375,  1075.   ,  1075.625,  1076.25 ,
                 1076.875,  1077.5  ,  1078.125,  1078.75 ,  1079.375,  1080.   ,
                 1080.625,  1081.25 ,  1081.875,  1082.5  ,  1083.125,  1083.75 ,
                 1084.375,  1085.   ,  1085.625,  1086.25 ,  1086.875,  1087.5  ,
                 1088.125,  1088.75 ,  1089.375,  1090.   ,  1090.625,  1091.25 ,
                 1091.875,  1092.5  ,  1093.125,  1381.25 ,  1382.5  ,  1383.75 ,
                 1385.   ,  1386.25 ,  1387.5  ,  1388.75 ,  1390.   ,  1391.25 ,
                 1393.75 ,  1395.   ,  1396.25 ,  1398.75 ,  1400.   ,  1402.5  ,
                 1405.   ,  1406.25 ,  1411.25 ,  1412.5  ,  1416.25 ,  1417.5  ,
                 1418.75 ,  1420.   ,  1421.25 ,  1423.75 ,  1427.5  ,  1428.75 ,
                 1430.   ,  1431.25 ,  1432.5  ,  1433.75 ,  1437.5  ,  1438.75 ,
                 1441.25 ,  1446.25 ,  1447.5  ,  1448.75 ,  1455.   ,  1456.25 ,
                 1457.5  ,  1458.75 ,  1460.   ,  1461.25 ,  1462.5  ,  1463.75 ,
                 1465.   ,  1466.25 ,  1467.5  ,  1468.75 ,  1470.   ,  1471.25 ,
                 1473.75 ,  1475.   ,  1476.25 ,  1477.5  ,  1481.25 ,  1486.25 ,
                 1487.5  ,  1488.75 ,  1490.   ,  1491.25 ,  1495.   ,  1496.25 ,
                 1497.5  ,  1500.   ,  1501.25 ,  1502.5  ,  1503.75 ,  1505.   ,
                 1506.25 ,  1508.75 ,  1510.   ,  1511.25 ,  1512.5  ,  1513.75 ,
                 1515.   ,  1516.25 ,  1517.5  ,  1518.75 ,  1520.   ,  1521.25 ,
                 1522.5  ,  1523.75 ,  1525.   ,  1526.25 ,  1527.5  ,  1528.75 ,
                 1530.   ,  1531.25 ,  1532.5  ,  1533.75 ,  1535.   ,  1536.25 ,
                 1537.5  ,  1540.   ,  1541.25 ,  1543.75 ,  1545.   ,  1546.25 ,
                 1547.5  ,  1548.75 ,  1550.   ,  1551.25 ,  1552.5  ,  1553.75 ,
                 1555.   ,  1556.25 ,  1557.5  ,  1560.   ,  1561.25 ,  1563.75 ,
                 1566.25 ,  1568.75 ,  1570.   ,  1571.25 ,  1572.5  ,  1573.75 ,
                 1575.   ,  1576.25 ,  1577.5  ,  1578.75 ,  1591.25 ,  1592.5  ,
                 1595.   ,  1596.25 ,  1597.5  ,  1598.75 ,  1600.   ,  1601.25 ,
                 1602.5  ,  1603.75 ,  1605.   ,  1606.25 ,  1607.5  ,  1608.75 ,
                 1610.   ,  1611.25 ,  1612.5  ,  1613.75 ,  1615.   ,  1616.25 ,
                 1617.5  ,  1618.75 ,  1620.   ,  1621.25 ,  1622.5  ,  1625.   ,
                 1626.25 ,  1627.5  ,  1628.75 ,  1630.   ,  1631.25 ,  1632.5  ,
                 1633.75 ,  1635.   ,  1640.   ,  1641.25 ,  1642.5  ,  1643.75 ,
                 1645.   ,  1650.   ,  1651.25 ,  1653.75 ,  1655.   ,  1656.25 ,
                 1657.5  ,  1658.75 ,  1661.25 ,  1663.75 ,  1668.75 ,  1670.   ,
                 1671.25 ,  1672.5  ,  1673.75 ,  1675.   ,  1676.25 ,  1677.5  ,
                 1678.75 ,  1681.25 ,  1682.5  ,  1683.75 ,  1686.25 ,  1687.5  ,
                 1690.   ,  1691.25 ,  1692.5  ,  1695.   ,  1696.25 ,  1697.5  ,
                 1698.75 ,  1700.   ,  1701.25 ,  1702.5  ,  1705.   ,  1706.25 ,
                 1707.5  ,  1708.75 ,  1710.   ,  1711.25 ,  1713.75 ,  1715.   ,
                 1720.   ,  1721.25 ,  1723.75 ,  1728.75 ,  1732.5  ,  1736.25 ,
                 1737.5  ,  1741.25 ,  1742.5  ,  1745.   ]])

        temp_wave_ref = nc.Dataset("./in_wn.nc", 'w', format="NETCDF3_CLASSIC")
        temp_wave_ref.createDimension('wnum', None)
        temp_var = temp_wave_ref.createVariable(INPUT_WAVE_NUMBER_VAR_NAME, 'f8', ('wnum'))
        temp_var[0:wavenumbers_list.size] = wavenumbers_list

        temp_wave_ref.close()

        log.info("Finished writing in_wc.nc to file")

    def build_test_pressure_list_input (*args) :
        """create an input file with a test pressure level

        :param args:
        :return:
        """

        log.info("Writing example pressure levels to file")

        plevels = numpy.array([  4.99999989e-03,   1.61000006e-02,   3.84000018e-02,
                                 7.68999979e-02,   1.36999995e-01,   2.24399999e-01,
                                 3.45400006e-01,   5.06399989e-01,   7.13999987e-01,
                                 9.75300014e-01,   1.29719996e+00,   1.68719995e+00,
                                 2.15260005e+00,   2.70090008e+00,   3.33979988e+00,
                                 4.07700014e+00,   4.92040014e+00,   5.87760019e+00,
                                 6.95669985e+00,   8.16549969e+00,   9.51189995e+00,
                                 1.10038004e+01,   1.26492004e+01,   1.44559002e+01,
                                 1.64318008e+01,   1.85846996e+01,   2.09223995e+01,
                                 2.34526005e+01,   2.61828995e+01,   2.91210003e+01,
                                 3.22743988e+01,   3.56505013e+01,   3.92565994e+01,
                                 4.31001015e+01,   4.71882019e+01,   5.15278015e+01,
                                 5.61259995e+01,   6.09894981e+01,   6.61252975e+01,
                                 7.15398026e+01,   7.72396011e+01,   8.32310028e+01,
                                 8.95204010e+01,   9.61138000e+01,   1.03017197e+02,
                                 1.10236603e+02,   1.17777496e+02,   1.25645599e+02,
                                 1.33846207e+02,   1.42384796e+02,   1.51266403e+02,
                                 1.60495895e+02,   1.70078400e+02,   1.80018295e+02,
                                 1.90320297e+02,   2.00988693e+02,   2.12027695e+02,
                                 2.23441498e+02,   2.35233795e+02,   2.47408493e+02,
                                 2.59969086e+02,   2.72919098e+02,   2.86261688e+02,
                                 3.00000000e+02,   3.14136902e+02,   3.28675293e+02,
                                 3.43617615e+02,   3.58966492e+02,   3.74724091e+02,
                                 3.90892609e+02,   4.07473785e+02,   4.24469788e+02,
                                 4.41881897e+02,   4.59711792e+02,   4.77960693e+02,
                                 4.96629791e+02,   5.15719971e+02,   5.35232178e+02,
                                 5.55166870e+02,   5.75524780e+02,   5.96306213e+02,
                                 6.17511230e+02,   6.39139771e+02,   6.61192017e+02,
                                 6.83667297e+02,   7.06565430e+02,   7.29885681e+02,
                                 7.53627502e+02,   7.77789673e+02,   8.02371399e+02,
                                 8.27371277e+02,   8.52788025e+02,   8.78620117e+02,
                                 9.04865906e+02,   9.31523621e+02,   9.58591125e+02,
                                 9.86066589e+02,   1.01394757e+03,   1.04223193e+03,
                                 1.07091699e+03,   1.10000000e+03], dtype=numpy.float32)

        temp_wave_ref = nc.Dataset("./in_plvls.nc", 'w', format="NETCDF3_CLASSIC")
        temp_wave_ref.createDimension('plvls', None)
        temp_var = temp_wave_ref.createVariable(INPUT_PRESSURE_LEVELS_VAR_NAME, 'f8', ('plvls'))
        temp_var[0:plevels.size] = plevels

        temp_wave_ref.close()

        log.info("Finished writing in_plvls.nc to file")

    def create_fov_file (*args) :
        """generate an fov file from an input SHIS data file

        This option generates a properly formatted fov.nc file from a Scanning HIS data file.

        Examples:
         python -m shis2mirto.shis2mirto create_fov_file
        """

        log.info("Generating FOV file from SHIS data")

        # we need SHIS input and a base FOV file to generate input
        if (options.shis_input is None) or (options.wnum_input is None) :
            log.warn("Incomplete input, unable to generate FOV file")
            return

        # pull some things from the options
        center_angle  = options.center_fov_angle
        angle_range   = options.fov_angle_range
        shis_file     = nc.Dataset(clean_path(options.shis_input), 'r')
        wn_base_file  = nc.Dataset(clean_path(options.wnum_input), 'r')

        desired_wnums = numpy.sort(wn_base_file.variables[INPUT_WAVE_NUMBER_VAR_NAME][:])
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

        # copy the various time variables
        temp_base_time = shis_file.variables[SHIS_BASE_TIME_VAR_NAME][0]
        print("base time: " + str(temp_base_time))
        temp_var = out_fov_file.createVariable(OUT_FOV_BASE_TIME_VAR_NAME, 'f8')
        temp_var.assignValue(temp_base_time)
        temp_time_offset = shis_file.variables[SHIS_TIME_OFFSET_VAR_NAME][angle_mask]
        temp_var = out_fov_file.createVariable(OUT_FOV_TIME_OFFSET_VAR_NAME, 'f8', (OUT_FOV_OBS_NUM_DIM_NAME))
        temp_var[0:num_obs] = temp_time_offset

        # also need the time in the matlab datenum format
        # "TimeFracDay == is the equivalent of the matlab datenum function, 1 corresponds to Jan-1-0000 "
        total_epoc_secs = temp_time_offset + temp_base_time
        matlab_times = numpy.zeros(total_epoc_secs.size, dtype=numpy.float32)
        for index in range(0, total_epoc_secs.size) :
            matlab_times[index] = datetime_to_matlab_datenum(datetime.fromtimestamp(total_epoc_secs[index]))
        temp_var = out_fov_file.createVariable(OUT_FOV_MATLAB_DATENUM_TIME_VAR_NAME, 'f8', OUT_FOV_OBS_NUM_DIM_NAME)
        temp_var[0:num_obs] = matlab_times

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
        temp_var[0:num_selected_channels] = found_indexes + 1 # we will use matlab indexing here

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

    def create_first_guess_file (*args) :
        """build a first guess file based on a list of pressure levels and an fov.nc file

        This method requires an fov.nc file as generated by create_fov_file. It uses the
        Virtual Radiosonde code to get GFS data and then modifies it to create an fg.nc file.

        :param args:
        :return:
        """

        log.info("Generating first guess file from GFS data and fov file positioning information")

        # we need access to the fov file and an input pressure list in order to run the
        # virtual radiosonde, so if we don't have those, just stop
        if options.fov_base is None or options.plevels_input is None :
            log.warn("Unable to create first guess file without input fov file and input pressure levels.")
            return

        log.info("Loading lon/lat and times from FOV file")

        # open the fov file and pull the lon / lat and time information
        fov_file   = nc.Dataset(clean_path(options.fov_base),      'r')
        lon_data   = fov_file.variables[OUT_FOV_LON_VAR_NAME][:]
        lat_data   = fov_file.variables[OUT_FOV_LAT_VAR_NAME][:]
        time_data  = fov_file.variables[OUT_FOV_TIME_OFFSET_VAR_NAME][:] + fov_file.variables[OUT_FOV_BASE_TIME_VAR_NAME][0]
        fov_file.close()

        # build the list of time / lon / lat dictionaries
        dt_times   = [ ]
        # convert the epoch seconds format to datetimes
        for epoch_seconds in time_data :
            dt_times.append(datetime.fromtimestamp(epoch_seconds))
        # make the list of dictionaries representing each point
        desired_points = [ ]
        for index in range(0, lon_data.size) :
            desired_points.append({
                                    'datetime':  dt_times[index],
                                    'latitude':  lat_data[index],
                                    'longitude': lon_data[index]
                                  })

        log.info("Loading pressure levels from file")

        # open the pressure levels file and get the list of pressure levels
        plvls_file = nc.Dataset(clean_path(options.plevels_input), 'r')
        plvls_data = numpy.sort(plvls_file.variables[INPUT_PRESSURE_LEVELS_VAR_NAME][:])[::-1]
        plvls_file.

        log.info("Running Virtual Radiosonde code")

        # call the virtual radiosonde to get data to start with
        stamp = datetime.now().strftime('%s')
        cache_dir = os.path.join('/tmp/vr/', stamp)
        if not os.path.exists(cache_dir) :
            os.mkdir(cache_dir)
        # TODO, probably need to do bilinear interpolation, this may need to be a user knob
        src = radiosonde.VirtualRadiosondeNarrator(on_dread=True, levels=plvls_data, cache=cache_dir)
        results = list(src(desired_points))

        #print("results: " + str(results[0].keys()))

        # TODO, modify the virtual radiosonde data to make the fg file


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

