import time

from bettertimes.crypto.ciphertext import AdditiveCipherText
from hos_protocol_v2.hos_less_than import HosLessThan
from hos_protocol_v2.proximity_testing_protocol import ProximityTestingProtocol


class ArrayTimeScramble(ProximityTestingProtocol):
    def server_enrico(self, a1, a2, a3, a4):
        # Subtracts normally
        def sub(a, b):
            return a - b

        return self.server_enrico_base(a1, a2, a3, a4, sub)

    def server_enrico_cached(self, a1, a2, a3):
        # Subtracts using a cache
        def sub(a, b):
            return self.sub_with_cache(a, b, self.key_pair)

        return self.server_enrico_base(a1, a2, a3, sub)

    def server_enrico_base(self, a1, a2, a3, a4, subtraction_method):
        """
         Compares only sums of squares. Any subtraction function can be used, to enable caching etc.
        """
        total_time = time.time()
        intermed_time = time.time()

        spat_distance = self.calc_spat_distance(a1, a2, a3)

        self.TIMES.setdefault('SERVER>calc_spat_distance', []).append(time.time() - intermed_time)
        print 'Calculated spatial distance in %s' % (time.time() - intermed_time)
        intermed_time = time.time()

        temp_distance = self.calc_temp_distance(a4)

        self.TIMES.setdefault('SERVER>calc_spat_distance', []).append(time.time() - intermed_time)
        print 'Calculated temporal distance in %s' % (time.time() - intermed_time)
        intermed_time = time.time()
        
        # The synchronized queue in which we put the sum-of-squares to be subtracted
        sums_of_squares = HosLessThan.get_sums_of_squares(int(self.r))
        scrambled_spat_array = HosLessThan.equals_any(spat_distance, sums_of_squares, subtraction_method, self.scheme, self.key_pair)
        print 'Calculated spatial scrambled array in %s' % (time.time() - intermed_time)
        intermed_time = time.time()

        # The synchronized queue in which we put the possible temporal distances to be subtracted
        possible_temps = HosLessThan.get_possible_temps(int(self.time_max), int(self.dev_prec))
        scrambled_temp_array = HosLessThan.equals_any(temp_distance, possible_temps, subtraction_method, self.scheme, self.key_pair)
        print 'Calculated temporal scrambled array in %s' % (time.time() - intermed_time)
        intermed_time = time.time()

        self.TIMES.setdefault('SERVER>creating_array', []).append(time.time() - intermed_time)
        self.TIMES.setdefault('server', []).append(time.time() - total_time)
        return scrambled_spat_array, scrambled_temp_array

    create_response = server_enrico

    def get_proximity(self, response_array):
        t = time.time()
        found = HosLessThan.look_for(response_array, lambda x: x == 0, self.scheme, self.key_pair)
        self.TIMES.setdefault('get_proximity', []).append(time.time() - t)
        return found

    @staticmethod
    def sub_with_cache(distance, s, key):
        num = key.negation_cache[s]

        sub = distance + AdditiveCipherText(num, key, key.scheme)

        return sub
