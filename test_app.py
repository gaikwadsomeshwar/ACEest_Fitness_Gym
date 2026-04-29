import gc
import os
import pytest
import sqlite3
import flask_app  # Import the module to allow monkeypatching

TEST_DB = 'test_database.db'


@pytest.fixture(autouse=True)
def setup_teardown():
    original_db_name = flask_app.DB_NAME
    flask_app.DB_NAME = TEST_DB

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    flask_app.init_db(TEST_DB)
    yield

    gc.collect()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    flask_app.DB_NAME = original_db_name


@pytest.fixture
def client():
    return flask_app.app.test_client()


def test_index_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Client Dashboard' in response.data


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()["status"] == "OK"


def test_add_client_and_calorie_logic(client):
    response = client.post(
        '/add_client',
        data=dict(
            name='Test User',
            age='30',
            height='175',
            weight='75',
            program='Fat Loss (FL)',
        ),
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Client Test User added successfully!' in response.data

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM clients WHERE name = ?', ('Test User',)).fetchone()
    conn.close()

    assert row is not None
    assert row['calories'] == 1650


def test_search_clients(client):
    client.post(
        '/add_client',
        data=dict(name='Alpha', age='28', height='170', weight='70', program='Beginner (BG)'),
        follow_redirects=True,
    )
    client.post(
        '/add_client',
        data=dict(name='Beta', age='34', height='180', weight='80', program='Muscle Gain (MG)'),
        follow_redirects=True,
    )

    response = client.get('/?search=alpha')
    assert response.status_code == 200
    assert b'Alpha' in response.data
    assert b'Beta' not in response.data


def test_log_metric_updates_weight(client):
    client.post(
        '/add_client',
        data=dict(name='MetricUser', age='25', height='170', weight='68', program='Beginner (BG)'),
        follow_redirects=True,
    )

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT id FROM clients WHERE name = ?', ('MetricUser',)).fetchone()
    conn.close()
    client_id = row['id']

    response = client.post(
        f'/client/{client_id}/log_metric',
        data=dict(date='2026-04-29', weight='70', waist='80', bodyfat='18.5'),
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Body metrics logged successfully!' in response.data

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    updated = conn.execute('SELECT weight FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()

    assert updated['weight'] == 70.0


def test_generate_program(client):
    client.post(
        '/add_client',
        data=dict(name='ProgramUser', age='32', height='175', weight='72', program='Muscle Gain (MG)'),
        follow_redirects=True,
    )

    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT id FROM clients WHERE name = ?', ('ProgramUser',)).fetchone()
    conn.close()

    response = client.get(f"/client/{row['id']}/generate_program")
    assert response.status_code == 200
    assert b'AI Generated Program for' in response.data


def test_duplicate_client_error(client):
    client.post(
        '/add_client',
        data={
            'name': 'Duplicate User',
            'age': '30',
            'height': '180',
            'weight': '90',
            'program': 'Muscle Gain (MG)',
        },
        follow_redirects=True,
    )

    response = client.post(
        '/add_client',
        data={
            'name': 'Duplicate User',
            'age': '31',
            'height': '181',
            'weight': '95',
            'program': 'Fat Loss (FL)',
        },
    )

    assert response.status_code == 400
    assert b'Client with name Duplicate User already exists.' in response.data
