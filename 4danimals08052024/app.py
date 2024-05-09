from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime
import sqlite3, hashlib
from validate_fileds import validate_form
import os

app = Flask(__name__)
# Get the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))
# Set the database URI to use the root folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '4danimals.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

REQUEST_COUNTER = Counter(
    'http_requests_total',
    'Total HTTP Requests (by status and method)',
    ['method', 'endpoint', 'status']
)

#runs before any REST API request is handled, saves aside the start time
@app.before_request
def before_request_func():
    """
    This function runs before each request and records the start time.
    """
    request._prometheus_metrics_request_start_time = time()

#runs after any REST API request is handled, calculates latency and counts relevant stats
@app.after_request
def after_request(response):
    """
    The dunction calculates the latency by subtracting the recorded start time from the current time.
    Then, it increments the REQUEST_COUNTER metric for the appropriate labels derived from the request and response
    details: HTTP method, the endpoint accessed, and the HTTP status code of the response.
    The response object is then returned, unchanged.
    """
    request_latency = time() - request._prometheus_metrics_request_start_time
    REQUEST_COUNTER.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    return response

#the route that Prometheus will hit to scrape metrics
@app.route('/metrics')
def metrics():
    """
    The function returns the latest metrics data in the proper format (CONTENT_TYPE_LATEST) expected by Prometheus.
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# Define the Animal model
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date)
    age = db.Column(db.Float)
    species = db.Column(db.String(50), nullable=False)
    breed_name = db.Column(db.String(100))
    chip_number = db.Column(db.Integer, unique=True)
    spayed_neutered = db.Column(db.Boolean)
    arrival = db.Column(db.Date, default=datetime.utcnow)
    foster = db.Column(db.Boolean)
    current_owner = db.Column(db.Integer)
    vaccines = db.Column(db.String(255))

class Applicants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    teudat_zehut = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(255))
    mail = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    approved = db.Column(db.Boolean)
    owner_of = db.Column(db.String(255))

class Volunteers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    teudat_zehut = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(255))
    mail = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    job_function = db.Column(db.String(255))
    can_be_foster = db.Column(db.Boolean)
    animal_fostered = db.Column(db.String(255))


def convert_to_datetime(text_date):
    """
    Convert a date string in the format 'YYYY-MM-DD' to a datetime object.
    """
    print(str(text_date))
    try:
        # Use strptime to parse the date string with specific format
        date_obj = datetime.strptime(str(text_date), "%Y-%m-%d")
        return date_obj
    except ValueError:
        raise ValueError(f"Invalid date format: {str(text_date)}. Expected format YYYY-MM-DD")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view-volunteers', methods=['GET', 'POST'])
def view_volunteers():
    """
    This function responds to both GET and POST requests at the '/view-volunteers' route.
    For a GET request, it fetches all volunteers from the database and renders them on a web page.
    For a POST request, it applies filters received from a form submission to query specific volunteers
    and displays them accordingly.
    """
    if request.method == 'GET':
        # Connect to your SQL database
        conn = sqlite3.connect('4danimals.db')
        cur = conn.cursor()
        # Query for available volunteers
        cur.execute("SELECT * FROM Volunteers")
        volunteers = cur.fetchall()
        # Close the connection
        conn.close()
        # Render the HTML page with the volunteers data
        return render_template('view-volunteers.html', volunteers=volunteers) #animals=animals)

    elif request.method == 'POST':
        # Extract filter values from the form
        animal_fostered = request.form.get('animal_fostered')
        city = request.form.get('city')
        can_be_foster = request.form.get('can_be_foster') == '1'

        # Construct query based on filters
        query = Volunteers.query
        if animal_fostered:
            query = query.filter(Volunteers.animal_fostered == animal_fostered)
        if city:
            query = query.filter(Volunteers.city == city)
        if can_be_foster:
            query = query.filter(Volunteers.can_be_foster == '1')
        volunteers = query.all()
    else:
        # If it's a GET request, just display all volunteers initially
        volunteers = Volunteers.query.all()

    return render_template('view-volunteers.html', volunteers=volunteers)

@app.route('/view-animals', methods=['GET', 'POST'])
def view_animals():
    """
    For a GET request, this function retrieves all animals from the database and renders them on a web page.
    For a POST request, it filters the animals based on form submission parameters such as gender, age range,
    species, breed, and whether they are spayed or neutered, then displays the filtered list.
    """
    if request.method == 'GET':
        # Connect to your SQL database
        conn = sqlite3.connect('4danimals.db')
        cur = conn.cursor()

        # Query for available animals
        cur.execute("SELECT * FROM Animal")
        animals = cur.fetchall()

        # Close the connection
        conn.close()

        # Render the HTML page with the animals data
        return render_template('view-animals.html', table_name=Animal) #animals=animals)

    elif request.method == 'POST':
        # Extract filter values from the form
        gender = request.form.get('gender')
        age_min = request.form.get('age_min')
        age_max = request.form.get('age_max')
        species = request.form.get('species')
        breed = request.form.get('breed')
        spayed_neutered = request.form.get('spayed_neutered') == '1'

        # Construct query based on filters
        query = Animal.query
        if gender:
            query = query.filter(Animal.gender == gender)
        if age_min:
            query = query.filter(Animal.age >= age_min)
        if age_max:
            query = query.filter(Animal.age <= age_max)
        if species:
            query = query.filter(Animal.species.ilike(f'%{species}%'))
        if breed:
            query = query.filter(Animal.breed.ilike(f'%{breed}%'))
        if spayed_neutered:
            query = query.filter(Animal.spayed_neutered == spayed_neutered)
        animals = query.all()
    else:
        # If it's a GET request, just display all animals initially
        animals = Animal.query.all()

    return render_template('view-animals.html', animals=animals)

@app.route('/view-adopters', methods=['GET', 'POST'])
def view_adopters():
    """
    For a GET request, this function retrieves all adopters from the database and renders them on a web page.
    For a POST request, it filters the adopters based on form submission parameters such as the type of animal owned,
    city, and whether their application has been approved, then displays the filtered list.

    """
    if request.method == 'GET':
        # Connect to your SQL database
        conn = sqlite3.connect('4danimals.db')
        cur = conn.cursor()

        # Query for available adopters
        cur.execute("SELECT * FROM Applicants")
        applicants = cur.fetchall()

        # Close the connection
        conn.close()

        # Render the HTML page with the adopters data
        return render_template('view-adopters.html', applicants=applicants)

    elif request.method == 'POST':
        # Extract filter values from the form
        owner_of = request.form.get('owner_of')
        city = request.form.get('city')
        approved = request.form.get('approved') == '1'

        # Construct query based on filters
        query = Applicants.query
        if owner_of:
            query = query.filter(Applicants.owner_of == owner_of)
        if city:
            query = query.filter(Applicants.city == city)
        if approved:
            query = query.filter(Applicants.approved == '1')
        applicants = query.all()
    else:
        # If it's a GET request, just display all applicants initially
        applicants = Applicants.query.all()

    return render_template('view-adopters.html', applicants=applicants)

@app.route('/add-animal', methods=['GET', 'POST'])
def add_animal():
    """
    The function manages the addition of a new animal to the database via a web form.
    For a GET request, this function simply renders the form for adding a new animal.
    For a POST request, it processes the submitted form data to create and store a new animal entry in the database.
    If the data is valid, it commits the new animal to the database and redirects to the home page.
    If the data is invalid, it refills the form with the previously submitted data and displays error messages.
    """
    if request.method == 'POST':
        refill = True
        while (refill):
            # Create a new Animal instance using the form data
            new_animal = Animal(
                name=request.form['name'],
                gender=request.form['gender'],
                color=request.form['color'] if request.form['color'] else None,
                birth_date=convert_to_datetime(request.form['birth_date']) if request.form['birth_date'] else None,
                age=request.form['age'] if request.form['age'] else None,
                species=request.form['species'] if request.form['species'] else None,
                breed_name=request.form['breed_name'] if request.form['breed_name'] else None,
                chip_number=request.form['chip_number'] if request.form['chip_number'] else None,
                spayed_neutered=True if request.form.get('spayed_neutered') == 'on' else False,
                # arrival=request.form['arrival'] if request.form['arrival'] else None,
                arrival= convert_to_datetime(request.form['arrival']) if request.form['arrival'] else None,
                foster=True if request.form.get('foster') == "on" else False,
                current_owner=request.form['current_owner'] if request.form['current_owner'] else None,
                vaccines=request.form['vaccines'] if request.form['vaccines'] else None
            )

            animal_data = {
                "name": {"name": "name", "value": new_animal.name, "required": True},
                "gender": {"name": "gender", "value": new_animal.gender, "required": True},
                "color": {"name": "color", "value": new_animal.color, "required": True},
                "birth_date": {"name": "birth_date", "value": None, "required": False},
                "age": {"name": "age", "value": new_animal.age, "required": False},
                "species": {"name": "species", "value": new_animal.species, "required": True},
                "breed_name": {"name": "breed_name", "value": new_animal.breed_name, "required": False},
                "chip_number": {"name": "chip_number", "value": new_animal.chip_number, "required": False},  # Add optional parameters
                "spayed_neutered": {"name": "spayed_neutered", "value": new_animal.spayed_neutered, "required": False},
                "arrival": {"name": "arrival", "value": new_animal.arrival.strftime("%Y-%m-%d"), "required": True},
                # "foster": {"name": "foster", "value": new_animal.foster, "required": False},
                "current_owner": {"name": "current_owner", "value": new_animal.current_owner, "required": False},
                "vaccines": {"name": "Vaccines", "value": new_animal.vaccines, "required": False},

            }
            try:
                if new_animal.birth_date:
                    animal_data["birth_date"]["value"] = new_animal.birth_date.strftime("%Y-%m-%d")
            except :
                print("do nothing")
            validate, errors = validate_form(**animal_data)
            if validate:
                refill = False
                # Add the new animal to the session and commit it to the database
                # Animal.arrival = convert_to_datetime(Animal.arrival)
                # Animal.birth_date = convert_to_datetime(Animal.Animal.birth_date)
                db.session.add(new_animal)
                db.session.commit()
                # Redirect to a new URL, or render a template with a success message
                return redirect(url_for('index'))  # Redirect back to the home page or a confirmation page
            else:
                print(",".join(errors))
                return render_template('add-animal.html', animal_data=animal_data, errors=errors)

    elif request.method == 'GET':
        return render_template('add-animal.html')
    # If the request method isn't POST, you might want to redirect or show an error
    return render_template('error.html')  # Render an error template or redirect

@app.route('/add-adopter', methods=['GET', 'POST'])
def add_adopter():
    """
    The function manages the addition of a new adopter to the database via a web form.
    For a GET request, this function renders the form for adding a new adopter.
    For a POST request, it processes the submitted form data to create and store a new adopter entry in the database.
    Upon successful form submission, the new adopter is added to the database, and the user is redirected to the home page.
    """
    if request.method == 'POST':
        # Create a new Animal instance using the form data
        new_adopter = Applicants(
            full_name=request.form['full_name'],
            Teudat_Zehut=request.form['teudat_zehut'],
            address=request.form['address'] if request.form['address'] else None,
            city=request.form['city'] if request.form['city'] else None,
            mail=request.form['mail'] if request.form['mail'] else None,
            phone=request.form['phone'] if request.form['phone'] else None,
            approved=False, #True if request.form.get('approved') == 'on' else False,
            owner_of=request.form['owner_of'] if request.form['owner_of'] else None
        )

        # Add the new animal to the session and commit it to the database
        db.session.add(new_adopter)
        db.session.commit()

        # Redirect to a new URL, or render a template with a success message
        return redirect(url_for('index'))  # Redirect back to the home page or a confirmation page
    elif request.method == 'GET':
        return render_template('add-adopter.html')
    # If the request method isn't POST, you might want to redirect or show an error
    return render_template('error.html')  # Render an error template or redirect

@app.route('/add-volunteer', methods=['GET', 'POST'])
def new_volunteer():
    """
    The function manages the addition of a new volunteer to the database via a web form.
    For a GET request, this function renders the form for adding a new volunteer.
    For a POST request, it processes the submitted form data to create and store a new volunteer entry in the database.
    Upon successful form submission, the new volunteer is added to the database, and the user is redirected to the home page.
    """
    if request.method == 'POST':
        # Create a new Animal instance using the form data
        new_volunteer = Volunteers(
            full_name=request.form['full_name'],
            teudat_zehut=request.form['teudat_zehut'],
            address=request.form['address'] if request.form['address'] else None,
            city=request.form['city'] if request.form['city'] else None,
            mail=request.form['mail'] if request.form['mail'] else None,
            phone=request.form['phone'] if request.form['phone'] else None,
            job_function=request.form['job_function'] if request.form['job_function'] else None,
            can_be_foster=False, #True if request.form.get('can_be_foster') == 'on' else False,
            animal_fostered=request.form['animal_fostered'] if request.form['animal_fostered'] else None
        )

        # Add the new animal to the session and commit it to the database
        db.session.add(new_volunteer)
        db.session.commit()

        # Redirect to a new URL, or render a template with a success message
        return redirect(url_for('index'))  # Redirect back to the home page or a confirmation page
    elif request.method == 'GET':
        return render_template('add-volunteer.html')
    # If the request method isn't POST, you might want to redirect or show an error
    return render_template('error.html')  # Render an error template or redirect

@app.route('/pets-catalog', methods=['GET'])
def pets_catalog():
    """
    This function displays the pets catalog page.
    It's responsible for rendering the 'pets-catalog.html' page when the '/pets-catalog' route is accessed via a GET
    request.
    It is designed to provide users with a view of the pets catalog, showcasing available pets or pet-related
    information.
    """
    return render_template('pets-catalog.html')

@app.route('/about-us', methods=['GET'])
def about_us():
    """
    This function displays the 'About Us' page.
    It handles the rendering of the 'about-us.html' page when the '/about-us' route is accessed via a GET request.
    It is intended to provide users with information about the organization, it's history, or other relevant details.
    """
    return render_template('about-us.html')

@app.route('/faqs', methods=['GET'])
def faqs():
    """
    This function displays the Frequently Asked Questions (FAQs) page.
    It's responsible for rendering the 'faqs.html' page when the '/faqs' route is accessed via a GET request.
    It is designed to provide users with answers to common questions about services, policies, or other inquiries
    relevant to the organization.
    """
    return render_template('faqs.html')

@app.route('/admin', methods=['GET'])
def admin():
    """
    This function displays the administrative dashboard page.
    It's tasked with rendering the 'admin.html' page when the '/admin' route is accessed via a GET request.
    It provides a user interface for administrative tasks, allowing authorized users to manage settings, view reports,
    or control various aspects of the application.
    """
    return render_template('admin.html')

@app.route('/admin/get_table_data/<table>', methods=['GET'])
def get_table_data(table):
    """
    The function retrieves and returns all data from a specified database table as JSON.
    This function connects to an SQLite database, fetches all entries from the specified table, and then
    converts this data into a JSON-compatible format using a list of dictionaries where each dictionary
    represents a row in the table. The function handles GET requests and is intended for administrative purposes
    to view table contents directly.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('4danimals.db')
    c = conn.cursor()

    # Fetch data from the specified table
    c.execute(f'SELECT * FROM {table}')
    data = c.fetchall()

    # Close the database connection
    conn.close()

    # Convert the data to a list of dictionaries for JSON serialization
    table_data = []
    for row in data:
        table_data.append(dict(zip([column[0] for column in c.description], row)))

    # Return the table data as JSON
    return jsonify(table_data)

#THIS PART WAS LEFT HERE FOR PROJECT DOCUMENTATION PURPOSES ONLY, UNDER NORMAL CURCEMSTANCES IT SHOULD BE GONE!
# user_name for log-in into admin section: "admin"
# password for log-in into admin section: "Password123!"

@app.route('/log-in', methods=['GET', 'POST'])
def login():
    """
    The function handles the user login process via a web form.
    For a GET request, this function renders the login form.
    For a POST request, it processes the submitted username and password. It verifies these credentials by comparing
    hashed values stored as environment variables with hashes of the user inputs. If the credentials match,
    the user is redirected to the admin page. If not, an error message is displayed.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #Get HASH values of username and password that were passed as ENV variables in Dockerfile
        user_hash = os.environ.get('USER_HASH')
        password_hash = os.environ.get('PASSWORD_HASH')

        #Encode and generate HASH values for the user input strings
        user_hash256 = hashlib.sha256(username.encode('utf-8')).hexdigest()
        password_hash256 = hashlib.sha256(password.encode('utf-8')).hexdigest()

        #compare user input hash with ENV variables HASH
        if user_hash == user_hash256 and password_hash == password_hash256:
            return redirect(url_for('admin'))
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)


    elif request.method == 'GET':
        return render_template('login.html')

@app.route('/admin/approve/<table>/<id>', methods=['PUT'])
def approve(table, id):
    """
    The function updates the approval status of an entry in the specified table using a PUT request.
    This function connects to an SQLite database to update the 'approved' status of an entry, identified by an ID,
    in a specified table. It supports different approval fields for different tables: 'approved' for applicants
    and 'can_be_foster' for volunteers. If the specified table is not supported, it returns an error.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('4danimals.db')
    c = conn.cursor()

    # Update the 'approved' status of the adopter with the specified ID
    if table == 'applicants':
        approved = 'approved'
    elif table == 'volunteers':
        approved = 'can_be_foster'
    else:
        return jsonify({"error": f"Table {table} not found"})
    c.execute(f'UPDATE {table} SET {approved} = True WHERE id = {id}')
    conn.commit()
    conn.close()

    return jsonify({"message": f"id {id} in {table} approved successfully"})

@app.route('/admin/delete/<table>/<id>', methods=['DELETE'])
def delete(table, id):
    """
    The function handles the deletion of a database entry via a DELETE request.
    This function connects to an SQLite database, deletes an entry based on the specified table name and entry ID,
    and then commits the change.
    It is designed to be called using a DELETE HTTP method, which is typical for RESTful APIs.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('4danimals.db')
    c = conn.cursor()

    # Delete the entry with the specified ID from the table
    c.execute(f'DELETE FROM {table} WHERE id = {id}')
    conn.commit()
    conn.close()

    return jsonify({"message": f"id {id} in {table} deleted successfully"})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)