from flask import url_for
from wsgi import app

with app.app_context():
    def test_login(web_client):
        response_invalid = web_client.post('/login', data={
            'username': 'john',
            'password': 'john@+=1967'
        })
        assert response_invalid.status_code == 404


    def test_signup(web_client):
        data = {
            'firstname': 'John',
            'lastname': 'John',
            'email': 'omartriki712@gmail.com',
            'password': 'john@1996'
        }
        with app.app_context():
            response = web_client.post('http://127.0.0.1:5000/signup', data=data)
            print(response.text)
            assert response.status_code == 200
