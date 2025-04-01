import hashlib
from bitarray import bitarray

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item):
        for i in range(self.hash_count):
            digest = self.hash(item, i)
            index = digest % self.size
            self.bit_array[index] = True

    def check(self, item):
        for i in range(self.hash_count):
            digest = self.hash(item, i)
            index = digest % self.size
            if not self.bit_array[index]:
                return False
        return True

    def hash(self, item, i):
        return int(hashlib.sha256((str(item) + str(i)).encode('utf-8')).hexdigest(), 16)