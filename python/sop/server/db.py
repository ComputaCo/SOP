from functools import cached_property
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



class HasDB:
    """Mixin class for classes that need to access the database."""

    engine = create_engine('database://user:password@host:port/database_name')

    def db() -> Session:
        return self.app.db