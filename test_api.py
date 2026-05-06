import requests

BASE_URL = 'http://localhost:8000/api/'

def test_health():
    try:
        response = requests.get(BASE_URL + 'dashboard/')
        print(f'Status: {response.status_code}')
        print('Backend esta vivo. Usa Swagger para pruebas completas: http://localhost:8000/api/docs/swagger/')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_health()
