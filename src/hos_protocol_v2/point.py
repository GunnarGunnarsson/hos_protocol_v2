from math import *


class Point(object):
    """ Simple point representation, which can calculate the distance to another point """

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    @staticmethod
    def from_lat_long(lat, lng):
        """ Converts longitude and latitude into an approximated euklidean space.

         Longitude has 360 degrees, latitude has 180. Longitude is east-west,
         latitude is north-south.
         The earth has a circumference north-south of 40 007.86 km, and a
         east-west circumference of 40 075.017 km.

         References:
             http://en.wikipedia.org/wiki/File:Latitude_and_Longitude_of_the_Earth.svg
             http://en.wikipedia.org/wiki/Earth
        """
        # Let our smallest unit be meters
        equatorial = 40007.86 * 1000
        meridional = 40075.017 * 1000

        x = equatorial / 2.0 * (lng + 180.0) / 360.0
        y = meridional / 2.0 * (lat + 90.0) / 180.0

        return Point(x, y)

    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)

    def distance_to(self, other):
        return sqrt(self.square_distance_to(other))

    def square_distance_to(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
