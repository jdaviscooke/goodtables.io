import json
from unittest import mock

import pytest


from goodtablesio import helpers, services
from goodtablesio.app import app


@pytest.fixture(scope='function', autouse=True)
def db_cleanup():

    services.database['jobs'].delete()

    yield


@pytest.fixture()
def client():

    return app.test_client()


def _data(response):

    return json.loads(response.get_data(as_text=True))


def test_api_basic(client):

    response = client.get('/api/')

    assert response.status_code == 200
    assert response.content_type == 'application/json; charset=utf-8'


def test_api_job_list_empty(client):

    response = client.get('/api/job')

    assert _data(response) == []


def test_api_job_list(client):

    helpers.insert_job_row('1')
    helpers.insert_job_row('2')

    response = client.get('/api/job')

    assert _data(response) == ['2', '1']


def test_api_get_job(client):

    helpers.insert_job_row('1')

    response = client.get('/api/job/1')

    data = _data(response)

    # TODO: Update after #19

    assert 'result' in data
    assert data['result']['job_id'] == '1'
    assert 'created' in data['result']
    assert 'status' in data


def test_api_get_job_not_found(client):

    response = client.get('/api/job/xxx')

    assert response.status_code == 404

    assert _data(response) == {'message': 'Job not found'}


def test_api_create_job(client):

    payload = {'files': [{'source': 'http://example.com'}]}

    # NB: We can't post the payload directly in `data` as Werkzeug
    # will think that the `files` key are actual uploads

    with mock.patch('goodtablesio.tasks.validate'):
        response = client.post(
            '/api/job',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'})

    assert response.status_code == 200

    job_id = response.get_data(as_text=True)
    assert services.database['jobs'].find_one(job_id=job_id)


def test_api_create_job_empty_body(client):

    response = client.post('/api/job')

    assert response.status_code == 400

    assert _data(response) == {'message': 'Missing configuration'}


def test_api_create_job_wrong_params(client):

    payload = {'not_files': [{'source': 'http://example.com'}]}

    response = client.post(
        '/api/job',
        data=json.dumps(payload),
        headers={'Content-Type': 'application/json'})

    assert response.status_code == 400

    assert _data(response) == {'message': 'Invalid configuration'}
