import csv
from typing import List, Final, Optional
import re

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
    def __str__(self) -> str:
        return self.author_name

class Family:
    def __init__(self, taxon_id: str, scientific_name: str, author: Optional[Author]):
        self.taxon_id = taxon_id
        self.scientific_name: str = scientific_name
        self.common_name: Optional[str] = name_db.find(taxon_id)
        self.author: Optional[Author] = author

class Genus:
    def __init__(self, taxon_id: str, scientific_name: str, year_discovered: int, family: Family):
        self.taxon_id = taxon_id
        self.scientific_name = scientific_name
        self.year_discovered = year_discovered
        self.family = family

    def __str__(self) -> str:
        return f'{self.taxon_id} || {self.scientific_name} -> {self.family.scientific_name} :: DISCOVERED ({self.year_discovered})'

class Species:
    def __init__(self, taxon_id: str, scientific_name: str, year_discovered: Optional[int], genus: Genus, authors: List[str]):
        self.taxon_id = taxon_id
        self.scientific_name = scientific_name
        self.common_name = name_db.find(taxon_id)
        self.year_discovered = year_discovered
        self.authors: List[str] = authors
        self.genus = genus

    def print_authors(self):
        print('Authors: ', self.authors)

    def __str__(self) -> str:
        return f'{self.taxon_id} || ({self.common_name}) >> {self.scientific_name} -> {self.genus.scientific_name} :: DISCOVERED ({self.year_discovered})'

class BirdDB:
    def __init__(self):
        self.families: List[Family] = []
        self.genera: List[Genus] = []
        self.species: List[Species] = []
        self.authors: List[Author] = []

    def get_year_discovered(self, authorship) -> int:
        # get the last token split by commas, strip whitespace
        base_str = authorship.split(',')[-1].strip()

        # only some of these have parenthesis!
        if base_str[-1] == ')':
            base_str = base_str[:-1]

        return int(base_str)

    def get_author_names(self, authorship) -> List[str]:
        authors: List[str] = []

        if authorship == '':
            return []

        if authorship[0] == '(':
            authorship = authorship[1:]

        # when there is a date string, return everything before it
        splits = authorship.split(',')[:-1]

        for i in range(0, len(splits)):
            if '&' in splits[i]:
                split = splits[i].split('&')
                splits.pop(i)
                splits += [split[0], split[1]]

        prev_name = ''
        for name in splits:
            # most likely someones initials after their surname.
            # no idea why they would separate with a comma,  but here we are.
            if len(name) <= 3:
                if len(authors) > 0:
                    authors.pop()
                authors.append(name.strip() + ', ' + prev_name.strip())
                continue

            authors.append(name.strip())

            prev_name = name
        return authors

    def eval_row(self, row):
        rank: str = row['taxonRank']
        if rank != 'family' and rank != 'genus' and rank != 'species':
            return

        parent_id: str = row['parentNameUsageID']
        scientific_name = row['scientificName']
        authorship_string = row['scientificNameAuthorship']
        id: str  = row['taxonID']

        author_names: List[str] = self.get_author_names(authorship_string)
        authors_to_add = author_names.copy()
        authors: List[Author] = []

        for author in self.authors:
            if author.author_name in authors_to_add:
                authors_to_add.remove(author.author_name)
                continue

        for name in author_names:
            author = Author(name)
            self.authors.append(author)


        if rank == 'family':
            family = Family(id, scientific_name, None)
            self.families.append(family)

        elif rank == 'genus':
            parent_family = next(family for family in self.families if family.taxon_id == parent_id)
            genus = Genus(id, scientific_name, self.get_year_discovered(authorship_string), parent_family)
            self.genera.append(genus)

        elif rank == 'species':
            parent_genus = next(genus for genus in self.genera if genus.taxon_id == parent_id)
            species = Species(id, scientific_name, self.get_year_discovered(authorship_string), parent_genus, author_names)
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
        species.print_authors()
    # for species in bird_db.species:
    #     if species.taxon_id == '25f96c869ac945904c37ff2344261d49':
    #         print(species)
    #         species.print_authors()

if __name__ == "__main__":
    generate_db()

# birdfile = open('taxon.csv')

# bird_reader = csv.reader(birdfile)
# for row in bird_reader:
#     pass
