from typing import Any
from python.sop.base.app import MakeBaseApp
from python.sop.client.api import ClientAPI, SubController
from python.sop.client.entity import ClientEntity


class App(MakeBaseApp(ClientAPI, ClientEntity)):
    pass
