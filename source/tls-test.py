from flask import Flask, url_for, request
import requests
import requests_pkcs12

import wrapt
from dataclasses import asdict
from functools import wraps
from pprint import pprint

r = requests.get('https://127.0.0.1:8443/serviceregistry/echo', cert=('certificates/tls-test.crt', 'certificates/tls-test.key'), verify=False)
r = requests_pkcs12.get('https://127.0.0.1:8443/serviceregistry/echo',
        pkcs12_filename='certificates/tls-test.p12',
        pkcs12_password='123456',
        verify=False)

print(r.text)
print(__name__)

