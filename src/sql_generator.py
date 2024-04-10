from bird_db import BirdDB

class SQLGenerator:
    def __init__(self, bird_db: BirdDB, output_filename: str):
        self.bird_db = bird_db
        self.output_file = open(output_filename, "w")

    def generate_authors(self):
        output_data = "INSERT INTO authors (author_name) VALUES \n"

        for author in self.bird_db.authors:
            output_data += f"\t('{author.author_name}')"
            if author != self.bird_db.authors[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_families(self):
        output_data = "INSERT INTO families (scientific_name, common_name) VALUES\n"

        for family in self.bird_db.families:
            output_data += f"\t('{family.scientific_name}', '{family.common_name}')"
            if family != self.bird_db.families[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_genera(self):
        output_data = "INSERT INTO genera (scientific_name, year_discovered, family_scientific_name) VALUES\n"

        for genus in self.bird_db.genera:
            output_data += f"\t('{genus.scientific_name}', {genus.year_discovered}, (SELECT scientific_name FROM families WHERE scientific_name = '{genus.family.scientific_name}'))"
            if genus != self.bird_db.genera[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_species(self):
        output_data = "INSERT INTO species (scientific_name, common_name, year_discovered, genus_scientific_name) VALUES\n"

        for species in self.bird_db.species:
            output_data += f"\t('{species.scientific_name}', '{species.common_name}', {species.year_discovered}, (SELECT scientific_name FROM genera WHERE scientific_name = '{species.genus.scientific_name}'))"
            if species != self.bird_db.species[-1]:
                output_data += ',\n'

        output_data += ';\n\n'

        self.output_file.write(output_data)

    def generate_discovery_types(self):
        output_data = "INSERT INTO discovery_types (discovery_type) VALUES\n\t('SPECIES'),\n\t('GENUS');\n\n"
        self.output_file.write(output_data)

    # this fella generates all the connections between authors and genera, and authors and species.
    # because this db is supposed to be in 3nf, i just make sure that every row has only one value
    # and stuff like that. i think. well, i should've paid more attention instead of writing python
    # scripts to write the SQL for me, but this is more interesting
    def generate_bird_authors(self):
        output_data = "INSERT INTO bird_authors (author_id, discovery_type, genus_scientific_name) VALUES\n"

        print(f'writing {len(self.bird_db.genera)} author collections [genera]')
        # shield your eyes, this one is pretty ripe.
        for genus in self.bird_db.genera:
            for author in genus.authors:
                output_data += f"\t((SELECT id FROM authors WHERE author_name = '{author}' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), (SELECT scientific_name FROM genera WHERE scientific_name = '{genus.scientific_name}'))"
                if author == genus.authors[-1] and genus == self.bird_db.genera[-1]:
                    break
                output_data += ',\n'

        output_data += ';\n\n'
        self.output_file.write(output_data)

        output_data = "INSERT INTO bird_authors (author_id, discovery_type, species_scientific_name) VALUES\n"
        print(f'writing {len(self.bird_db.species)} author collections [species]')
        for species in self.bird_db.species:
            for author in species.authors:
                output_data += f"\t((SELECT id FROM authors WHERE author_name = '{author}' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), (SELECT scientific_name FROM species WHERE scientific_name = '{species.scientific_name}'))"
                if author == species.authors[-1] and species == self.bird_db.species[-1]:
                    break
                output_data += ',\n'

        output_data += ';\n\n'
        self.output_file.write(output_data)

    def generate(self):
        self.generate_authors()
        self.generate_families()
        self.generate_genera()
        self.generate_species()
        self.generate_discovery_types()
        self.generate_bird_authors()
