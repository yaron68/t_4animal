import sqlite3

def create_database():
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('4danimals.db')
    c = conn.cursor()

    # Create the Animal table
    c.execute('''CREATE TABLE IF NOT EXISTS Animal (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR,
                    gender VARCHAR,
                    color VARCHAR,
                    birth_date DATE,
                    age FLOAT,
                    species VARCHAR,
                    breed_name VARCHAR,
                    chip_number INTEGER,
                    spayed_neutered BOOLEAN,
                    arrival DATE,
                    foster BOOLEAN,
                    current_owner INTEGER,
                    Vaccines VARCHAR,
                    FOREIGN KEY (current_owner) REFERENCES Applicants(full_name)
                 )''')


    # Create the Applicants table
    c.execute('''CREATE TABLE IF NOT EXISTS Applicants (
                    id INTEGER PRIMARY KEY,
                    full_name VARCHAR,
                    teudat_zehut VARCHAR,
                    address VARCHAR,
                    city VARCHAR,
                    mail VARCHAR,
                    phone VARCHAR,
                    approved BOOLEAN,
                    owner_of VARCHAR
                 )''')

    # Create the Volunteers table
    c.execute('''CREATE TABLE IF NOT EXISTS Volunteers (
                    id INTEGER PRIMARY KEY,
                    full_name VARCHAR,
                    teudat_zehut VARCHAR,
                    address VARCHAR,
                    city VARCHAR,
                    mail VARCHAR,
                    phone VARCHAR,
                    job_function VARCHAR,
                    can_be_foster BOOLEAN,
                    animal_fostered VARCHAR,
                    FOREIGN KEY (animal_fostered) REFERENCES Animal(name)
                 )''')

    # Create the Vaccines table
    c.execute('''CREATE TABLE IF NOT EXISTS Vaccines (
                    id INTEGER PRIMARY KEY,
                    Vaccine_name VARCHAR,
                    Vaccine_date DATE
                 )''')

    # Create the Foster_application_form table
    c.execute('''CREATE TABLE IF NOT EXISTS Foster_application_form (
                    id INTEGER PRIMARY KEY,
                    full_name VARCHAR,
                    phone_number VARCHAR,
                    address VARCHAR,
                    email VARCHAR,
                    foster_dog BOOLEAN,
                    foster_cat BOOLEAN,
                    foster_pups BOOLEAN,
                    foster_kittens BOOLEAN,
                    foster_dog_with_newborns BOOLEAN,
                    foster_newborn_kittens BOOLEAN,
                    has_car BOOLEAN,
                    previous_experience BOOLEAN,
                    detailed_experience VARCHAR,
                    other_pets_at_home BOOLEAN,
                    detailed_pets_at_home VARCHAR
                 )''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()