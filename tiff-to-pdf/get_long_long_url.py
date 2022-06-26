import requests

# детали запроса
uid = '8447ce27-9374-4e17-b754-5ca86fb77ee0'
url = ('http://fortum.proactor.pro/api/extensions/' '792162f9-eb8d-4872-94af-763e275a02b0/script/' f'file_by_id?uid={uid}')
ELMA_TOKEN = '22615f9c-c9d8-4fca-9d4c-7821e285d95b'

header = {"X-TOKEN": ELMA_TOKEN}

response = requests.get(url, headers=header, stream=True)

result = response.json()
print(result)

''' 

{'data': {'filename': 'test_conv.tiff', 
          'url': 'http://fortum.proactor.pro/s3elma365/305211ce-411d-4f82-abeb-15f2d746f374?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=PZSF73JG72Ksd955JKU1HIA%2F20220510%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220510T184408Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&response-content-disposition=attachment%3B%20filename%3Dtest_conv.tiff&X-Amz-Signature=46c3a7a63fcb304235b1f2e63195a105d016433877ebd9b784a7b0616643f350'
          }, 
          'error': None
}

'''