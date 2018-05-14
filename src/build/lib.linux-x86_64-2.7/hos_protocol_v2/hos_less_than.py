import random
from multiprocessing import Process, Manager



class HosLessThan(object):
    num_threads = 1
    parallel = True

    @classmethod
    def get_sums_of_squares(cls, to):
        sums_of_squares = []
        # Fill the array
        for i in range(0, to):
            for j in range(i, to):
                sum_of_square = j ** 2 + i ** 2
                sums_of_squares.append(sum_of_square)

        return list(set(sums_of_squares))

    @classmethod
    def get_possible_temps(cls, time_max, dev_prec):
        possible_temps = []
        # Fill the array
        for i in range(0, time_max, dev_prec):
            possible_temps.append(i)
            possible_temps.append(-i)
        return list(set(possible_temps))

    @classmethod
    def equals_any(cls, needle, haystack, subtraction_method, scheme, key_pair):
        plaintext_space = scheme.plaintext_space(key_pair)

        # The synchronized queue in which we'll store the result
        result_queue = Manager().Queue()

        haystack_queue = Manager().Queue()
        for sum_of_square in haystack:
            haystack_queue.put(sum_of_square)

        # We are expecting one result per sum-of-square
        result_size = haystack_queue.qsize()
        if cls.num_threads > 1:
            threads = []
            for i in range(cls.num_threads):
                haystack_queue.put(None)  # Add one sentinel per thread
                thread = Process(target=cls.__subtract_and_blind_all,
                                 args=(haystack_queue, needle, subtraction_method, result_queue, plaintext_space))
                thread.start()

                threads.append(thread)

            for thread in threads:
                thread.join()
        else:
            haystack_queue.put(None)  # Add a sentinel also here
            cls.__subtract_and_blind_all(haystack_queue, needle, subtraction_method, result_queue, plaintext_space)

        # Scramble the array
        scrambled_array = [0] * result_size  # This array will hold the result, initially zerofilled
        indexes = range(0, result_size)
        for i in range(0, result_size):
            index = random.randrange(0, len(indexes))
            n = indexes[index]

            del indexes[index]

            scrambled_array[n] = result_queue.get()
        return scrambled_array

    @classmethod
    def look_for(cls, ciphertext_array, condition, scheme, key_pair):
        found = False
        manager = Manager()
        ciphertext_queue = manager.Queue()
        result_queue = manager.Queue()
        # Add all ciphertext to be consumed later by threads OR this main thread
        for cipher in ciphertext_array:
            ciphertext_queue.put(cipher)

        # Arguments passed to workers, note that the queue is mutated after this point as well
        args = (ciphertext_queue, scheme.decrypt, key_pair, result_queue, condition)
        if cls.num_threads > 1:
            threads = []
            for i in range(cls.num_threads):
                ciphertext_queue.put(None)  # Add a sentinel for each thread
                thread = Process(target=cls.__decrypt_many, args=args)
                thread.start()

                threads.append(thread)  # Save thread so that we may kill it and wait for it to finish later

            # Wait until either all threads return, or one thread returns True
            num_returned = 0
            while num_returned < cls.num_threads:
                result = result_queue.get()
                if result:
                    found = True
                    break

                num_returned += 1

            # Exit somewhat gracefully
            for thread in threads:
                if thread.is_alive():
                    thread.terminate()

            for thread in threads:
                thread.join()
        else:
            ciphertext_queue.put(None)  # Add a sentinel here as well

            # Run the decryption on the main thread
            cls.__decrypt_many(*args)

            # Get the result (there's only one result now)
            found = result_queue.get()
        return found

    @classmethod
    def __decrypt_many(cls, ciphertext_queue, decryption_function, key_pair, result_queue, condition):
        """
            Decrypts all cipher texts in the queue. Adds a boolean to the result queue, indicating if a zero is found
        """
        # Note that we use the sentinel value None to abort iteration
        for ciphertext in iter(ciphertext_queue.get, None):
            plain = decryption_function(key_pair, ciphertext)
            if condition(plain):
                result_queue.put(True)

        result_queue.put(False)

    @classmethod
    def __subtract_and_blind_all(cls, sos_queue, distance, subtraction_method, result_queue, plaintext_space):
        """
            Subtracts the distance with each value in the s_queue, blinding all non-zero values by multiplication
        """
        # Note that we use the sentinel value None to abort iteration
        for sum_of_square in iter(sos_queue.get, None):
            difference = subtraction_method(distance, sum_of_square)

            blinded = difference * random.randrange(1, plaintext_space)

            # Don't know why this was needed - perhaps for ElGamal and pickling or something (for a tupe of mpz's?).
            # Was breaking MaxPace, so removed for now.
            # raw_blinded = blinded.ciphertext
            # if isinstance(raw_blinded, tuple):  # ElGamal (ECC or over the integers)
            #     out = tuple([long(part) for part in raw_blinded])
            # else:
            #     out = raw_blinded

            result_queue.put(blinded)
