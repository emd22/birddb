from typing import List, Optional, Final
import csv

from utils import sanitize
from common_name import CommonName

class NameDB:
    def __init__(self):
        self.common_names: List[CommonName] = []

    def load(self, name_file):
        name_reader = csv.DictReader(name_file)
        # read each row from the vernacular_names csv
        for row in name_reader:
            # load in the raw data. this can hold multiple values, so we gotta split em.
            # vvv see next comment vvv
            base_name = row['vernacularName']

            names = [base_name]

            # some entries contain multiple names per taxon id, so we need to split
            # them up to be in 3rd normal form
            if ',' in base_name:
                names = base_name.split(',')
            # a pair of entries are usually separated with an ampersand, but not always!
            # always gotta check for that comma
            elif '&' in base_name:
                names = base_name.split('&')

            # for each name that we find, generate an entry that we can reference when
            # reading in species and genera.
            for name in names:
                name_obj = CommonName(row['taxonID'], sanitize(name))
                self.common_names.append(name_obj)

    # handy dandy print function for debugging
    def print(self, count: Optional[int]=None):
        # does optimization here even matter? i did write this in python after all...
        # i think this just gets compiled to a legit 'len' instruction in the vm anyway
        amt_names: Final[int] = len(self.common_names)
        max_iters: Final[int] = min(count, amt_names) if count else amt_names

        for i in range(0, max_iters):
            print(self.common_names[i])

    # this should definitely all be in a hash table or something. this makes me sad
    # issue is i had in total like 4 hours to write everything
    def find(self, taxon_id: str) -> Optional[str]:
        for name in self.common_names:
            if name.id == taxon_id:
                return name.name
        return None
