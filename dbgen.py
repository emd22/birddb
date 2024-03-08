import csv
from typing import List, Final, Optional
import re

def sanitize(data: str) -> str:
    # apostrophes can be a catastrophe
    if '\'' in data:
        data = data.replace('\'', '')
    # replace any non-ascii characters
    data = ''.join(ch for ch in data if ord(ch) < 128).strip()
    if len(data) > 0 and data[-1] == ',':
        data = data[:-1]
    return data

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
            name_obj = CommonName(row['taxonID'], sanitize(row['vernacularName']))
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
        self.author_name = sanitize(author_name)
    def __str__(self) -> str:
        return self.author_name

class Family:
    def __init__(self, taxon_id: str, scientific_name: str):
        self.taxon_id = taxon_id
        self.scientific_name: str = sanitize(scientific_name)
        self.common_name: Optional[str] = name_db.find(taxon_id)

class Genus:
    def __init__(self, taxon_id: str, scientific_name: str, year_discovered: int, family: Family, authors: List[str]):
        self.taxon_id = taxon_id
        self.scientific_name = sanitize(scientific_name)
        self.year_discovered = year_discovered
        self.authors: List[str] = authors
        self.family = family

    def __str__(self) -> str:
        return f'{self.taxon_id} || {self.scientific_name} -> {self.family.scientific_name} :: DISCOVERED ({self.year_discovered})'

class Species:
    def __init__(self, taxon_id: str, scientific_name: str, year_discovered: Optional[int], genus: Genus, authors: List[str]):
        self.taxon_id = taxon_id
        self.scientific_name = sanitize(scientific_name)
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
            name = sanitize(name)

            # most likely someones initials after their surname.
            # no idea why they would separate with a comma,  but here we are.
            if len(name) <= 3 and len(splits) > 2:
                if len(authors) > 0:
                    authors.pop()
                authors.append(name.strip() + ', ' + prev_name.strip())
                continue

            authors.append(name.strip())

            prev_name = name
        return authors

    def add_unique_authors(self, author_names: List[str]):
        authors_to_add = author_names.copy()
        authors: List[Author] = []

        for author in self.authors:
            if author.author_name in authors_to_add:
                authors_to_add.remove(author.author_name)
                continue

        for name in authors_to_add:

            author = Author(name)
            self.authors.append(author)

    def eval_row(self, row):
        rank: str = row['taxonRank']
        if rank != 'family' and rank != 'genus' and rank != 'species':
            return

        parent_id: str = row['parentNameUsageID']
        scientific_name = row['scientificName']
        authorship_string = row['scientificNameAuthorship']
        id: str = row['taxonID']

        author_names: List[str] = []

        # this is SUPER slow, best to only run this when we need to.
        if rank == 'genus' or rank == 'species':
            author_names = self.get_author_names(authorship_string)
            self.add_unique_authors(author_names.copy())

        if rank == 'family':
            family = Family(id, scientific_name)
            self.families.append(family)

        elif rank == 'genus':
            parent_family = next(family for family in self.families if family.taxon_id == parent_id)
            genus = Genus(id, scientific_name, self.get_year_discovered(authorship_string), parent_family, author_names)
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


class SQLGenerator:
    def __init__(self, bird_db: BirdDB, output_filename: str):
        self.bird_db = bird_db
        self.output_file = open(output_filename, "w")

    def generate_authors(self):
        output_data = "INSERT INTO authors VALUES \\\n"


        for author in self.bird_db.authors:
            output_data += f"\t('{author.author_name}')"
            if author != self.bird_db.authors[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_families(self):
        output_data = "INSERT INTO families VALUES \\\n"

        for family in self.bird_db.families:
            output_data += f"\t('{family.scientific_name}', '{family.common_name}')"
            if family != self.bird_db.families[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_genera(self):
        output_data = "INSERT INTO genera VALUES \\\n"

        for genus in self.bird_db.genera:
            output_data += f"\t('{genus.scientific_name}', {genus.year_discovered}, (SELECT scientific_name FROM families WHERE scientific_name = '{genus.family.scientific_name}'))"
            if genus != self.bird_db.genera[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_species(self):
        output_data = "INSERT INTO species VALUES \\\n"

        for species in self.bird_db.species:
            output_data += f"\t('{species.scientific_name}', '{species.common_name}', {species.year_discovered}, (SELECT scientific_name FROM genera WHERE scientific_name = '{species.genus.scientific_name}'))"
            if species != self.bird_db.genera[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_discovery_types(self):
        output_data = "INSERT INTO discovery_types VALUES\\\n\t('SPECIES'),\n\t('GENUS');\n\n"
        self.output_file.write(output_data)

    def generate_bird_authors(self):
        output_data = "INSERT INTO bird_authors VALUES \\\n"

        # shield your eyes, this one is pretty ripe.
        for genus in self.bird_db.genera:
            for author in genus.authors:
                output_data += f"\t((SELECT id FROM authors WHERE author_name = '{author}'), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), NULL, (SELECT scientific_name FROM genus WHERE scientific_name = '{genus.scientific_name}'))"
                output_data += ',\n'

        for species in self.bird_db.species:
            for author in species.authors:
                output_data += f"\t((SELECT id FROM authors WHERE author_name = '{author}'), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), NULL, (SELECT scientific_name FROM species WHERE scientific_name = '{species.scientific_name}'))"
                if author != species.authors[-1] and species != self.bird_db.species[-1]:
                    output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate(self):
        self.generate_authors()
        self.generate_families()
        self.generate_genera()
        self.generate_discovery_types()
        self.generate_bird_authors()


bird_db = BirdDB()
generator = SQLGenerator(bird_db, "output.txt")

def generate_db():
    # load our vernacular mames
    with open('vernacular_name.csv') as name_file:
        name_db.load(name_file)

    # load our bird info
    with open('taxon.csv') as bird_file:
        bird_db.load(bird_file)

    # family = next(family for family in bird_db.families if family.scientific_name == 'Apodidae')
    # genera_in_family = bird_db.find_in_family(family)

    # for genus in genera_in_family:
    #     print(genus)

    # species_in_genus = bird_db.find_in_genus(genera_in_family[1])
    # for species in species_in_genus:
    #     print(species)
    #     species.print_authors()

    generator.generate()

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
