import json


def test_create_tenant(client):
    payload = {'name': 'Clínica Alpha', 'subdomain': 'Clinica-Alpha!'}
    resp = client.post('/tenants/', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'tenant' in data
    assert data['tenant']['name'] == 'Clínica Alpha'
    # subdomain deve ser sanitizado (lowercase, sem caracteres especiais)
    assert data['tenant']['subdomain'] == 'clinica-alpha'


def test_create_duplicate_subdomain(client):
    payload = {'name': 'Clínica Beta', 'subdomain': 'dup-sub'}
    r1 = client.post('/tenants/', data=json.dumps(payload), content_type='application/json')
    assert r1.status_code == 201

    # tentar criar novamente com mesmo subdomain
    payload2 = {'name': 'Outra', 'subdomain': 'dup-sub'}
    r2 = client.post('/tenants/', data=json.dumps(payload2), content_type='application/json')
    assert r2.status_code == 409


def test_create_user_with_tenant(client):
    # cria um tenant primeiro
    t = {'name': 'Clinica User', 'subdomain': 'clinic-user'}
    tr = client.post('/tenants/', data=json.dumps(t), content_type='application/json')
    assert tr.status_code == 201
    tenant_id = tr.get_json()['tenant']['id']

    user_payload = {
        'name': 'Maria',
        'email': 'maria@example.com',
        'password': 'secret123',
        'tenant_id': tenant_id
    }
    ur = client.post('/users/', data=json.dumps(user_payload), content_type='application/json')
    assert ur.status_code == 201
    udata = ur.get_json()
    assert udata['name'] == 'Maria'
    assert udata['email'] == 'maria@example.com'
