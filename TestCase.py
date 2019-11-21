import unittest
import requests

class TestCase(unittest.TestCase):
    def test_1_PostOk(self):
        data = {
            'key': '"hello"',
            'value': 'world'
        }
        response = requests.post('http://localhost:2000/put', data=data)
        self.assertEqual(response.status_code, 200)

    def test_2_GetExist(self):
        response = requests.get('http://localhost:2000/get?key="hello"')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], 'world')

    def test_3_UpdateKey(self):
        data = {
            'key': '"hello"',
            'value': 'UNEXPECTED'
        }

        response = requests.post('http://localhost:2000/put', data=data)
        self.assertEqual(response.status_code, 200)

    def test_4_GetOldValueFromCache(self):
        response = requests.get('http://localhost:2000/get?key="hello"')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], 'world')

    def test_5_GetUpdatedValueFromDatabase(self):
        response = requests.get('http://localhost:2000/get?key="hello"&no-cache=false')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], 'UNEXPECTED')

    def test_6_DeleteExistKey(self):
        response = requests.delete('http://localhost:2000/delete?key="hello"')
        self.assertEqual(response.status_code, 200)

    def test_7_DeleteNonExistKey(self):
        response = requests.delete('http://localhost:2000/delete?key="hello"')
        self.assertEqual(response.status_code, 204)

    def test_8_GetNonExistKey(self):
        response = requests.get('http://localhost:2000/get?key="unknown"')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()