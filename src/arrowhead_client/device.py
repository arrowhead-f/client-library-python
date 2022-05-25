from arrowhead_client.dto import DTOMixin


class ArrowheadDevice(DTOMixin):
    device_name: str
    address: str
    authentication_info: str
    mac_address: str
