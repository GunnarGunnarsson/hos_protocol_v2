from bettertimes.crypto.schemes.paillier import Paillier


import random
import time


class ProximityTestingProtocol(object):
    """ 'New Protocol' implementation """

    def __init__(self, r, position, key_pair, time_max, dev_prec, scheme=Paillier()):
        self.r = r
        self.position = position

        self.key_pair = key_pair
        self.scheme = scheme

        self.time_max = time_max
        self.dev_prec = dev_prec

    def enc(self, p):
        return self.scheme.encrypt(self.key_pair, p)

    def dec(self, c):
        return self.scheme.decrypt(self.key_pair, c)

    # Constructs the message Alice sends to Bob
    def create_request(self):
        """ First message run in the protocol """
        t = time.time()
        a1 = self.enc(self.position.x)
        a2 = self.enc(self.position.y)
        a3 = self.enc(self.position.x ** 2 + self.position.y ** 2)
        a4 = self.enc(self.position.time)
        #a4 = self.enc(self.posi)
        self.TIMES.setdefault('client', []).append(time.time() - t)
        return a1, a2, a3, a4

    def create_response(self, a1, a2, a3):
        raise ValueError("Not implemented")

    def get_proximity(self, response):
        raise ValueError("Not implemented")

    """
    Description:
        Calculates the squared euclidean distance between itself and points a1, a2 and a3
    """
    def calc_spat_distance(self, a1, a2, a3):
        """
         Let:
            a1 = E_A(x_a)
            a2 = E_A(y_a)
            a3 = E_A(x_a^2 + y_a^2)

         We are computing D = (selfX - theirX)^2 + (selfY - theirY)^2
                          D = theirX^2 + theirY^2 + selfX^2 + selfY^2 - (2*selfX*theirX  + 2*selfY*theirY)
                             |---------  "enumerator"  --------------| |--------  "denominator"  ---------|

         Where D = d^2, and d is the distance between Alice and Bob
        """
        # As above, we have "enumerator" as follows:
        x2y2 = self.enc(self.position.x ** 2 + self.position.y ** 2)

        enumerator = a3 + x2y2

        # First and second part of "denominator"
        denominator_1 = a1 * (2 * self.position.x)
        denominator_2 = a2 * (2 * self.position.y)

        # Combining them, we have:
        denominator = denominator_1 + denominator_2

        # We can now compute D
        D = enumerator - denominator
        return D

    """
    Description:
        Calculates the linear (temporal) distance betwen itself and point a4
    """
    def calc_temp_distance(self, a4):
        return self.enc(self.position.time) - a4

    def suitable_rand(self):
        """
            Utility for generating a random number which is secure as possible,
            while assuring that it will not wrap in the current modulo.

            TODO: make it as secure as possible :-)
        """
        return random.randrange(self.key_pair.n / 2, self.key_pair.n)

    TIMES = {}

    @classmethod
    def reset_profile(cls):
        cls.TIMES = {}

    @classmethod
    def get_profile(cls):
        return cls.TIMES
