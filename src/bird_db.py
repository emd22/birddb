from typing import List
import csv

from models import Family, Genus, Species, Author
from utils import sanitize


class BirdDB:
    def __init__(self):
        self.families: List[Family] = []
        self.genera: List[Genus] = []
        self.species: List[Species] = []
        self.authors: List[Author] = []

    # split out the year discovered from the authorship string
    def get_year_discovered(self, authorship) -> int:
        # get the last token split by commas, strip whitespace
        base_str = authorship.split(',')[-1].strip()

        # only some of these have parenthesis
        if base_str[-1] == ')':
            base_str = base_str[:-1]

        return int(base_str)

    def get_author_names(self, authorship) -> List[str]:
        authors: List[str] = []

        if authorship == '':
            return []

        if authorship[0] == '(':
            authorship = authorship[1:]

        # make sure we dont have the year included, because we already parsed that
        # >> see get_year_discovered <<
        splits = authorship.split(',')[:-1]

        for i in range(0, len(splits)):
            if '&' in splits[i]:
                # EWW
                split = splits[i].split('&')
                splits.pop(i)
                splits += [split[0], split[1]]

        prev_name = ''

        for name in splits:
            name = sanitize(name)

            # most likely someones initials after their surname.
            # no idea why they would separate with a comma, but here we are
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
        # or you can run it all the time, i'm not your mom
        if rank == 'genus' or rank == 'species':
            author_names = self.get_author_names(authorship_string)
            self.add_unique_authors(author_names.copy())

        if rank == 'family':
            family = Family(id, scientific_name)
            self.families.append(family)

        elif rank == 'genus':
            # connect the genus to a parent family
            parent_family = next(family for family in self.families if family.taxon_id == parent_id)
            genus = Genus(id, scientific_name, self.get_year_discovered(authorship_string), parent_family, author_names)
            self.genera.append(genus)

        elif rank == 'species':
            # connect our species to a parent genus
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
