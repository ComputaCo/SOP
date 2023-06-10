from __future__ import annotations
from functools import cached_property
from typing import Type

from pony.orm import Required, Set, db_session, select, Optional


from python.sop.server.api import ServerAPI
from python.sop.server.app import App
from python.sop.server.entity import ServerEntity


class AuthEnhancedServerAPI(ServerAPI):
    def requires_owner(self, *attrs):
        return self.access_control(
            *attrs, predicate=lambda entity: entity.owner == self.app.current_user
        )

    def requires_role(self, role):
        return self.access_control(
            predicate=lambda entity: self.app.current_user.has_role(role)
        )


class App(App):
    current_user: User

    @cached_property
    def Entity(self) -> Type[ServerEntity]:
        class Entity(super().Entity):
            class Meta(self.T_Entity.Meta):
                api = AuthEnhancedServerAPI()
                app = self

            owner: User = Required("User")

        return Entity


app = App()


class User(app.Entity):
    class Meta(app.Entity.Meta):
        api = ServerAPI()

    name: str
    email: str
    hashed_password: str
    salt: str

    Meta.api.hidden("create")

    @classmethod
    def login(cls, email: str, password: str) -> User:
        ...

    @classmethod
    def logout(cls) -> None:
        ...
