from .abstract import AbstractFilter

from resolver.datasrc.iana import VALID_TLDS

bloom_filter = BloomFilter(capacity=1500, error_rate=0.01)

for tld in VALID_TLDS:
    bloom_filter.add(tld)


# Function to check if a TLD is in the Bloom Filter
def is_valid_tld_bloom(tld):
    return tld in bloom_filter


# Testing the function
print(is_valid_tld_bloom("com"))  # Should return True
print(is_valid_tld_bloom("xyz"))  # Might return False or True (False positive)
