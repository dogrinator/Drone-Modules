"""Module 2, exercise 4.1: compare 1 km UTM offsets with great-circle distances."""

from math import asin, cos, pi, radians, sin, sqrt
from utm import utmconv


def great_circle_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    a = sin((lat2 - lat1) / 2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2)**2
    # Aviation Formulary: one arcminute corresponds to 1852 metres.
    radius = 1852 * 180 * 60 / pi
    return 2 * radius * asin(sqrt(min(1, max(0, a))))


def main():
    lat1, lon1 = 55.47, 10.33
    uc = utmconv()
    hemisphere, zone, letter, east, north = uc.geodetic_to_utm(lat1, lon1)
    print(f"Reference: {lat1} N, {lon1} E; UTM zone {zone}{letter}")
    for direction, de, dn in [("East", 1000, 0), ("North", 0, 1000)]:
        lat2, lon2 = uc.utm_to_geodetic(hemisphere, zone, east + de, north + dn)
        distance = great_circle_distance(lat1, lon1, lat2, lon2)
        print(f"{direction}: great-circle distance = {distance:.3f} m, "
              f"difference from 1000 m UTM = {distance - 1000:.3f} m")


if __name__ == "__main__":
    main()
