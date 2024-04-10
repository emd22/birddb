import csv, sys
from typing import List, Final, Optional

sys.path.append('src')

from bird_db import BirdDB
from globals import *

from csv_generator import CSVGenerator
from sql_generator import SQLGenerator

def generate_db():
    bird_db = BirdDB()
    # generator = SQLGenerator(bird_db, "output.sql")

    csv_generator = CSVGenerator(bird_db, "")

    # load our common names
    with open('in/vernacular_name.csv') as name_file:
        name_db.load(name_file)

    # load our bird info. birds. hell yeah!
    with open('in/taxon.csv') as bird_file:
        bird_db.load(bird_file)

    csv_generator.generate()
    # generator.generate()

if __name__ == "__main__":
    generate_db()

# birdfile = open('taxon.csv')

# bird_reader = csv.reader(birdfile)
# for row in bird_reader:
#     pass
