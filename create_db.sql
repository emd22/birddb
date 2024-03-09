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
