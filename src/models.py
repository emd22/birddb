from typing import Optional, List

from utils import sanitize
from globals import *


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
        # the common name
        self.common_name = name_db.find(taxon_id)
        self.year_discovered = year_discovered
        self.authors: List[str] = authors
        self.genus = genus

    def print_authors(self):
        print('Authors: ', self.authors)

    def __str__(self) -> str:
        return f'{self.taxon_id} || ({self.common_name}) >> {self.scientific_name} -> {self.genus.scientific_name} :: DISCOVERED ({self.year_discovered})'
