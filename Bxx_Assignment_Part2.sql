-- create a table that contains all of the author's names. These will be
-- referenced by our bird_authors table, which connects the authors to
-- families and species.
CREATE TABLE authors (
	id INT NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(100),

    PRIMARY KEY (id)
);

-- note: there is only data for common names of bird families and species.

-- create a table to hold all of the animal families. these are one level
-- above genera(genus's) and two levels above species.
CREATE TABLE families (
	scientific_name VARCHAR(450),
    common_name VARCHAR(100),

    PRIMARY KEY (scientific_name)
);

-- create a table to hold each bird type's genus. these bad boys also have a
CREATE TABLE genera (
	scientific_name VARCHAR(450),
    year_discovered INT,
    family_scientific_name VARCHAR(450),

    PRIMARY KEY (scientific_name),
    FOREIGN KEY (family_scientific_name) REFERENCES families(scientific_name)
);

-- create a table to hold each species of bird.
CREATE TABLE species (
	scientific_name VARCHAR(450),
    common_name VARCHAR(100),
    year_discovered INT,
    genus_scientific_name VARCHAR(450),

    PRIMARY KEY (scientific_name),
    FOREIGN KEY (genus_scientific_name) REFERENCES genera(scientific_name)
);

CREATE TABLE discovery_types (
	discovery_type VARCHAR(30),
    PRIMARY KEY (discovery_type),
    CONSTRAINT chk_type CHECK (discovery_type = "GENUS" OR discovery_type = "SPECIES")
);

CREATE TABLE bird_authors (
	id INT NOT NULL AUTO_INCREMENT,
	author_id INT,
    discovery_type VARCHAR(30),
    species_scientific_name VARCHAR(450),
    genus_scientific_name VARCHAR(450),

    PRIMARY KEY (id),
    FOREIGN KEY (author_id) REFERENCES authors(id),
	FOREIGN KEY (discovery_type) REFERENCES discovery_types(discovery_type),
    FOREIGN KEY (species_scientific_name) REFERENCES species(scientific_name),
    FOREIGN KEY (genus_scientific_name) REFERENCES genera(scientific_name)
);


-- data loading into tables: for this, i wrote a python script to
-- generate the sql commands automatically as a lot of the data was
-- either dirty, or load data didnt combine the tables correctly
-- anyway, heres some data loading:


-- load author data into our authors table
INSERT INTO authors (author_name) VALUES
	('Adamowicz'),
	('Agne'),
	('Pacheco'),
	('Alexander');

-- insert families into families table
INSERT INTO families (scientific_name, common_name) VALUES
	('Struthionidae', 'Ostriches'),
	('Rheidae', 'Rheas'),
	('Apterygidae', 'Kiwis'),
	('Casuariidae', 'Cassowaries');

-- insert genera, set foreign key to our parent family
INSERT INTO genera (scientific_name, year_discovered, family_scientific_name) VALUES
	('Clanga Adamowicz, 1854', 1854, (SELECT scientific_name FROM families WHERE scientific_name = 'Accipitridae')),
	('Willisornis Agne & Pacheco, 2007', 2007, (SELECT scientific_name FROM families WHERE scientific_name = 'Thamnophilidae')),
	('Urolais Alexander, 1903', 1903, (SELECT scientific_name FROM families WHERE scientific_name = 'Cisticolidae')),
	('Poliolais Alexander, 1903', 1903, (SELECT scientific_name FROM families WHERE scientific_name = 'Cisticolidae'));

-- insert our species in, using our genera as a foreign key
INSERT INTO species (scientific_name, common_name, year_discovered, genus_scientific_name) VALUES
	('Puffinus yelkouan (Acerbi, 1827)', 'Yelkouan Shearwater', 1827, (SELECT scientific_name FROM genera WHERE scientific_name = 'Puffinus Brisson, 1760')),
	('Hydrobates cheimomnestes (Ainley, 1980)', 'Ainleys Storm Petrel', 1980, (SELECT scientific_name FROM genera WHERE scientific_name = 'Hydrobates Boie, F, 1822')),
	('Alauda razae (Alexander, 1898)', 'Raso Lark', 1898, (SELECT scientific_name FROM genera WHERE scientific_name = 'Alauda Linnaeus, 1758')),
	('Muscicapa gambagae (Alexander, 1901)', 'Gambaga Flycatcher', 1901, (SELECT scientific_name FROM genera WHERE scientific_name = 'Muscicapa Brisson, 1760'));

-- there are only two discovery types, families do not have discovery information with them.
INSERT INTO discovery_types (discovery_type) VALUES
	('SPECIES'),
	('GENUS');

-- the authors of the discoveries, these are for genus descoveries
INSERT INTO bird_authors (author_id, discovery_type, genus_scientific_name) VALUES
	((SELECT id FROM authors WHERE author_name = 'Adamowicz' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), (SELECT scientific_name FROM genera WHERE scientific_name = 'Clanga Adamowicz, 1854')),
	((SELECT id FROM authors WHERE author_name = 'Agne' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), (SELECT scientific_name FROM genera WHERE scientific_name = 'Willisornis Agne & Pacheco, 2007')),
	((SELECT id FROM authors WHERE author_name = 'Pacheco' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), (SELECT scientific_name FROM genera WHERE scientific_name = 'Willisornis Agne & Pacheco, 2007')),
	((SELECT id FROM authors WHERE author_name = 'Alexander' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'GENUS'), (SELECT scientific_name FROM genera WHERE scientific_name = 'Urolais Alexander, 1903'));

-- the authors of the discoveries, these are for species discoveries
INSERT INTO bird_authors (author_id, discovery_type, species_scientific_name) VALUES
	((SELECT id FROM authors WHERE author_name = 'Acerbi' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), (SELECT scientific_name FROM species WHERE scientific_name = 'Puffinus yelkouan (Acerbi, 1827)')),
	((SELECT id FROM authors WHERE author_name = 'Ainley' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), (SELECT scientific_name FROM species WHERE scientific_name = 'Hydrobates cheimomnestes (Ainley, 1980)')),
	((SELECT id FROM authors WHERE author_name = 'Alexander' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), (SELECT scientific_name FROM species WHERE scientific_name = 'Alauda razae (Alexander, 1898)')),
	((SELECT id FROM authors WHERE author_name = 'Alexander' LIMIT 1), (SELECT discovery_type FROM discovery_types WHERE discovery_type = 'SPECIES'), (SELECT scientific_name FROM species WHERE scientific_name = 'Muscicapa gambagae (Alexander, 1901)'));
