#!/usr/bin/env python3
#*****************************************************************************
# UTM projection conversion test
# Copyright (c) 2013-2020, Kjeld Jensen <kjeld@frobomind.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*****************************************************************************
"""
This file contains a simple Python script to test the UTM conversion class.

Revision
2013-04-05 KJ First version
2015-03-09 KJ Minor update of the license text.
2016-01-16 KJ Corrected a minor problem with the library location reference.
2020-02-03 KJ Python 3 compatible, changed functionality: it now moves a
              geodetic position 100 meter East
2020-09-17 KJ Changed first line to python3
"""

# import utmconv class
from utm import utmconv
from math import pi, cos
import math

# functions

def great_circle_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great circle distance using haversine formula.
    Input: lat/lon in degrees
    Output: distance in nautical miles and meters
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula (more accurate for short distances)
    d = 2 * math.asin(math.sqrt(
        math.sin((lat1_rad - lat2_rad) / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * 
        math.sin((lon1_rad - lon2_rad) / 2) ** 2
    ))
    
    # Convert radians to nautical miles
    # distance_nm = distance_radians * (180 * 60 / pi)
    distance_nm = d * (180 * 60 / math.pi)
    
    # Convert to meters
    distance_m = distance_nm * 1852
    
    return distance_nm, distance_m

# geodetic reference coordinate
lat1 =  55.47
lon1 = 010.33

print ('First position [deg]:')
print ('  latitude:  %.8f'  % (lat1))
print ('  longitude: %.8f'  % (lon1))

# instantiate utmconv class
uc = utmconv()

# convert from geodetic to UTM
(hemisphere, zone, letter, e1, n1) = uc.geodetic_to_utm (lat1,lon1)
print ('\nConverted from geodetic to UTM [m]')
print ('  %d %c %.5fe %.5fn' % (zone, letter, e1, n1))

# now generating the second UTM coordinate
e2 = e1 #+ 1000.0 
n2 = n1 + 1000

# convert back from UTM to geodetic
(lat2, lon2) = uc.utm_to_geodetic (hemisphere, zone, e2, n2)
print ('\nSecond position 1000 meter East [deg]:')
print ('  latitude:  %.8f'  % (lat2))
print ('  longitude: %.8f'  % (lon2))


nm, meters = great_circle_distance(lat1, lon1, lat2, lon2)
print(f"Reference: N{lat1}° E{lon1}°")
print(f"Target: N{lat2}° E{lon2:.6f}°")
print(f"Great Circle Distance: {nm:.6f} nm = {meters:.2f} meters")
print(f"Projection Error: {meters - 1000:.6f} meters")