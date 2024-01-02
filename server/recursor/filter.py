"""
This is a validation filter for recursive DNS to prevent
sending a bunch of bogus queries upstream.

I decided to use a hash set because it was quick enough
memory efficient. You are free to change the filtering
mechanism to whatever suits your use case by simply
passing a different filter object into the validator.
"""
from resolver.filters import (
    HashFilter,
    AbstractFilter,
)  # Examples: BloomFilter, SortedArray, Trixie


class DomainValidator:
    def __init__(self, Filter: AbstractFilter):
        self.filter = Filter

    def is_valid_tld(self, tld):
        return self.filter.validate(tld)


# You might need to install the library using pip
# pip install pybloom_live

from pybloom_live import BloomFilter

# Example list of TLDs
tlds = ["com", "org", "net", "io", "ai", "co.uk", "edu"]

# Creating a Bloom Filter
bloom_filter = BloomFilter(capacity=1500, error_rate=0.01)

# Adding TLDs to the Bloom Filter
for tld in tlds:
    bloom_filter.add(tld)


# Function to check if a TLD is in the Bloom Filter
def is_valid_tld_bloom(tld):
    return tld in bloom_filter


# Testing the function
print(is_valid_tld_bloom("com"))  # Should return True
print(is_valid_tld_bloom("xyz"))  # Might return False or True (False positive)
