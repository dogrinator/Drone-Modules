# Module 2: UTM accuracy (exercise 4.1)

Run `python utm_accuracy.py` from this directory. The downloaded `utm_test.py`,
`utm.py`, and `transverse_mercator.py` are unchanged.

The solution compares 1000 m offsets east and north in UTM with great-circle
distances, starting at N55.47 E010.33. It uses the radius convention from the
supplied Aviation Formulary (1852 m per arcminute). The reported difference is
**great-circle distance minus UTM distance**; it includes the difference between
a spherical Earth model and the WGS84 ellipsoid, as well as projection distortion.

Using the same reference makes team results comparable because UTM distortion
varies with position. Grid east/north are not exactly constant latitude/longitude
away from the zone's central meridian. The leading zero in E010.33 simply pads
longitude to three degree digits; it does not change the decimal-degree value.
