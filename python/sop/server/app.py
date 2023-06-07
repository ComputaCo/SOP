from typing import Any

from pony.orm import Database


from python.sop.base.app import MakeBaseApp
from python.sop.client.api import ClientAPI, SubController
from python.sop.client.entity import ClientEntity


class App(MakeBaseApp(ClientAPI, ClientEntity)):
    db = Database()
