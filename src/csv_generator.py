from bird_db import BirdDB

import csv
from typing import Iterable, Any

class SectionWriter:
    def __init__(self, filename: str):
        self.file = open('out/' + filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        pass

    def write_row(self, row: Iterable[Any]):
        self.writer.writerow(row)

    def write_rows(self, rows: Iterable[Iterable[Any]]):
        self.writer.writerows(rows)


class CSVGenerator:
    def __init__(self, bird_db: BirdDB, output_filename: str):
        self.bird_db = bird_db

        self.author_db = SectionWriter('author_db.csv')
        self.family_db = SectionWriter('family_db.csv')
        self.genera_db = SectionWriter('genera_db.csv')
        self.species_db = SectionWriter('species_db.csv')
        self.discovery_types_db = SectionWriter('discovery_types_db.csv')
        self.bird_authors_db = SectionWriter('bird_authors_db.csv')

    def setup_fields(self):
        self.author_db.write_row(['author_name'])
        self.family_db.write_row(['scientific_name', 'common_name'])
        self.genera_db.write_row(['scientific_name', 'year_discovered', 'family_scientific_name'])
        self.species_db.write_row(['scientific_name', 'common_name', 'year_discovered', 'genus_scientific_name'])
        self.discovery_types_db.write_row(['discovery_type'])
        self.bird_authors_db.write_row(['author_id', 'discovery_type', 'species_scientific_name', 'genus_scientific_name'])

    def write_authors(self):
        for author in self.bird_db.authors:
            self.author_db.write_row([author.author_name])

    def write_families(self):
        for family in self.bird_db.families:
            self.family_db.write_row([family.scientific_name, family.common_name])

    def write_genera(self):
        for genus in self.bird_db.genera:
            self.genera_db.write_row(
                [
                    genus.scientific_name,
                    genus.year_discovered,
                    f"(SELECT scientific_name FROM families WHERE scientific_name = '{genus.family.scientific_name}')"
                ]
            )

    def write_species(self):
        for species in self.bird_db.species:
            self.species_db.write_row(
                [
                    species.scientific_name,
                    species.common_name,
                    species.year_discovered,
                    f"(SELECT scientific_name FROM genera WHERE scientific_name = '{species.genus.scientific_name}')"
                ]
            )

    def write_discovery_types(self):
        self.discovery_types_db.write_rows([['SPECIES'], ['GENUS']])


    def write_bird_authors(self):
        for genus in self.bird_db.genera:
            for author in genus.authors:
                self.bird_authors_db.write_row(
                    [
                        f"(SELECT id FROM authors WHERE author_name = '{author}' LIMIT 1)",
                        "(SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS')",
                        None,
                        f"(SELECT scientific_name FROM genera WHERE scientific_name = '{genus.scientific_name}')"
                    ]
                )
        for species in self.bird_db.genera:
            for author in species.authors:
                self.bird_authors_db.write_row(
                    [
                        f"(SELECT id FROM authors WHERE author_name = '{author}' LIMIT 1)",
                        "(SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES')",
                        f"(SELECT scientific_name FROM genera WHERE scientific_name = '{species.scientific_name}')",
                        None
                    ]
                )

    def generate(self):
        self.setup_fields()
        self.write_authors()
        self.write_families()
        self.write_genera()
        self.write_species()
        self.write_discovery_types()
        self.write_bird_authors()
