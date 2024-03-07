import csv
from functools import singledispatch
from typing import List, Final, Optional

class CommonName:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
    def __str__(self) -> str:
        return f'{self.id} || {self.name}'


class NameDB:
    def __init__(self):
        self.common_names: List[CommonName] = []

    def load(self, name_file):
        name_reader = csv.DictReader(name_file)
        for row in name_reader:
            name_obj = CommonName(row['taxonID'], row['vernacularName'])
            self.common_names.append(name_obj)

    def print(self, count: Optional[int]=None):
        amt_names: Final[int] = len(self.common_names)
        max_iters: Final[int] = min(count, amt_names) if count else amt_names

        for i in range(0, max_iters):
            print(self.common_names[i])

    def find(self, taxon_id: str) -> Optional[str]:
        for name in self.common_names:
            if name.id == taxon_id:
                return name.name
        return None

name_db = NameDB()

class Author:
    def __init__(self, author_name: str):
        self.author_name = author_name

class Family:
    def __init__(self, taxon_id: str, scientific_name: str, author: Optional[Author]):
        self.taxon_id = taxon_id
        self.scientific_name: str = scientific_name
        self.common_name: Optional[str] = name_db.find(taxon_id)
        self.author: Optional[Author] = author

class Genus:
    def __init__(self, taxon_id: str, scientific_name: str, family: Family):
        self.taxon_id = taxon_id
        self.scientific_name = scientific_name
        self.family = family

    def __str__(self) -> str:
        return f'{self.taxon_id} || {self.scientific_name} -> {self.family.scientific_name}'

class Species:
    def __init__(self, taxon_id: str, scientific_name: str, genus: Genus):
        self.taxon_id = taxon_id
        self.scientific_name = scientific_name
        self.common_name = name_db.find(taxon_id)
        self.genus = genus

    def __str__(self) -> str:
        return f'{self.taxon_id} || ({self.common_name}) >> {self.scientific_name} -> {self.genus.scientific_name}'

class BirdDB:
    def __init__(self):
        self.families: List[Family] = []
        self.genera: List[Genus] = []
        self.species: List[Species] = []

    def eval_row(self, row):
        rank: str = row['taxonRank']
        parent_id: str = row['parentNameUsageID']
        scientific_name = row['scientificName']
        id: str  = row['taxonID']

        if rank == 'family':
            family = Family(id, scientific_name, None)
            self.families.append(family)

        elif rank == 'genus':
            parent_family = next(family for family in self.families if family.taxon_id == parent_id)
            genus = Genus(id, scientific_name, parent_family)
            self.genera.append(genus)

        elif rank == 'species':
            parent_genus = next(genus for genus in self.genera if genus.taxon_id == parent_id)
            species = Species(id, scientific_name, parent_genus)
            self.species.append(species)


    def load(self, bird_file):
        name_reader = csv.DictReader(bird_file)

        for row in name_reader:
            self.eval_row(row)

    def find_in_family(self, family: Family) -> List[Genus]:
        results: List[Genus] = []
        for genus in self.genera:
            if genus.family == family:
                results.append(genus)

        return results

    def find_in_genus(self, genus: Genus):
        results: List[Species] = []
        for species in self.species:
            if species.genus == genus:
                results.append(species)

        return results



bird_db = BirdDB()

def generate_db():
    # load our vernacular mames
    with open('vernacular_name.csv') as name_file:
        name_db.load(name_file)

    # load our bird info
    with open('taxon.csv') as bird_file:
        bird_db.load(bird_file)

    family = next(family for family in bird_db.families if family.scientific_name == 'Apodidae')
    genera_in_family = bird_db.find_in_family(family)
    # for genus in genera_in_family:
    #     print(genus)
    species_in_genus = bird_db.find_in_genus(genera_in_family[1])
    for species in species_in_genus:
        print(species)



if __name__ == "__main__":
    generate_db()

# birdfile = open('taxon.csv')

# bird_reader = csv.reader(birdfile)
# for row in bird_reader:
#     pass
