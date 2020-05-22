#!/usr/bin/env python

from . import configuration
from .system import ArrowheadSystem
from .system import ConsumerSystem
from .system import ProviderSystem
from .service import ConsumedHttpService as ConsumedService
from .service import ProvidedHttpService as ProvidedService

config = configuration.set_config()

#TODO: This line should be removed and the certificates should be added
# to the list of trusted certificates.
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

