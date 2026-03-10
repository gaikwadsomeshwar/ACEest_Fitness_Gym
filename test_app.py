import os
import pytest
import sqlite3
import flask_app  # Import the module to allow monkeypatching

# Define the name for the test database
TEST_DB = 'test_database.db'

@pytest.fixture(autouse=True)
def setup_teardown():
    """
    This fixture automatically runs for every test.
    It sets up a clean test database before each test and tears it down afterward.
    """
    # Monkeypatch the DB_NAME global in the flask_app module to use our test DB
    original_db_name = flask_app.DB_NAME
    flask_app.DB_NAME = TEST_DB

    # Ensure the DB is clean before tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Initialize the database schema for the test session
    flask_app.init_db()

    yield  # This is where the test execution happens

    # Teardown: clean up the database file after the test
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Restore the original DB_NAME to avoid side effects
    flask_app.DB_NAME = original_db_name

@pytest.fixture
def client():
    """A test client for the Flask app."""
    # Return the test client from our app instance
    return flask_app.app.test_client()

def test_index_page_loads(client):
    """Test that the dashboard/index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Client Dashboard" in response.data

def test_add_client_and_calorie_logic(client):
    """
    Test the full flow of adding a client and validate the internal logic,
    specifically the automatic calorie calculation.
    """
    # POST data to add a new client
    response = client.post('/add_client', data=dict(
        name='Test User',
        age=30,
        height=175,
        weight=75,
        program='Fat Loss (FL)'
    ), follow_redirects=True)

    # Assert that the page responds correctly and shows a success message
    assert response.status_code == 200
    assert b"Client Test User added successfully!" in response.data

    # Verify the data directly in the database to confirm internal logic
    client_row = None
    try:
        conn = sqlite3.connect(TEST_DB)
        conn.row_factory = sqlite3.Row
        client_row = conn.execute('SELECT * FROM clients WHERE name = ?', ('Test User',)).fetchone()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

    # Assert that the database record is correct
    assert client_row is not None
    assert client_row['name'] == 'Test User'
    # The calorie factor for 'Fat Loss (FL)' is 22. Calculation: 75 * 22 = 1650
    assert client_row['calories'] == 1650

def test_delete_client(client):
    """Test that a client can be successfully deleted."""
    # First, add a client to be deleted directly to the database
    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, age, height, weight, program) VALUES (?, ?, ?, ?, ?)",
                ('UserToDelete', 30, 170, 80, 'Beginner (BG)'))
    client_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Send a POST request to the delete endpoint
    response = client.post(f'/client/{client_id}/delete', follow_redirects=True)

    # Assert the deletion was successful
    assert response.status_code == 200
    assert b"Client deleted successfully!" in response.data
    assert b"UserToDelete" not in response.data

def test_duplicate_client_error(client):
    """Test that adding a client with a duplicate name shows the correct error."""
    # Add a client
    client.post('/add_client', data={
        'name': 'Duplicate User',
        'age': '30',
        'height': '180',
        'weight': '90',
        'program': 'Muscle Gain (MG)'
    })

    # Attempt to add the same client again
    response = client.post('/add_client', data={
        'name': 'Duplicate User',
        'age': '31',
        'height': '181',
        'weight': '95',
        'program': 'Fat Loss (FL)'
    })

    # Assert that the correct flash message is displayed
    assert response.status_code == 400
    assert b"Client with name Duplicate User already exists." in response.data