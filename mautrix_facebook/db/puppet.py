# mautrix-facebook - A Matrix-Facebook Messenger puppeting bridge
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Optional, Iterator

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.sql import expression
from sqlalchemy.engine.result import RowProxy

from mautrix.types import UserID

from .base import Base


class Puppet(Base):
    __tablename__ = "puppet"

    fbid: str = Column(String(127), primary_key=True)
    name: str = Column(String(255), nullable=True)
    photo_id: str = Column(String(255), nullable=True)
    matrix_registered: bool = Column(Boolean, nullable=False, server_default=expression.false())

    custom_mxid: UserID = Column(String(255), nullable=True)
    access_token: str = Column(Text, nullable=True)

    @classmethod
    def scan(cls, row: RowProxy) -> Optional['Puppet']:
        fbid, name, photo_id, matrix_registered, custom_mxid, access_token = row
        return cls(fbid=fbid, name=name, photo_id=photo_id, matrix_registered=matrix_registered,
                   custom_mxid=custom_mxid, access_token=access_token)

    @classmethod
    def get_by_fbid(cls, fbid: str) -> Optional['Puppet']:
        return cls._select_one_or_none(cls.c.fbid == fbid)

    @classmethod
    def get_by_name(cls, name: str) -> Optional['Puppet']:
        return cls._select_one_or_none(cls.c.name == name)

    @classmethod
    def get_by_custom_mxid(cls, mxid: UserID) -> Optional['Puppet']:
        return cls._select_one_or_none(cls.c.custom_mxid == mxid)

    @classmethod
    def get_all_with_custom_mxid(cls) -> Iterator['Puppet']:
        return cls._select_all(cls.c.custom_mxid != None)

    @property
    def _edit_identity(self):
        return self.c.fbid == self.fbid

    def insert(self) -> None:
        with self.db.begin() as conn:
            conn.execute(self.t.insert().values(
                fbid=self.fbid, name=self.name, photo_id=self.photo_id,
                matrix_registered=self.matrix_registered, custom_mxid=self.custom_mxid,
                access_token=self.access_token))
