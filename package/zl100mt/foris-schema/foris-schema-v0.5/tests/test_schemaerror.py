# foris-schema
# Copyright (C) 2017 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from foris_schema import ForisValidator
from foris_schema.validator import (
    SchemaErrorModuleMismatch,
    SchemaErrorMutipleTypes,
    SchemaErrorWrongMessage,
    ModuleAlreadyLoaded,
    SchemaErrorDefinitionAlreadyUsed
)


def test_missing_properties():
    with pytest.raises(SchemaErrorWrongMessage):
        ForisValidator(["tests/schemas/modules/wrong_schema/properties/"])


def test_missing_mandatory():
    with pytest.raises(SchemaErrorWrongMessage):
        ForisValidator(["tests/schemas/modules/wrong_schema/mandatory/"])


def test_module_mismatched():
    with pytest.raises(SchemaErrorModuleMismatch):
        ForisValidator(["tests/schemas/modules/wrong_schema/mismatched/"])


def test_already_loaded():
    with pytest.raises(ModuleAlreadyLoaded):
        ForisValidator([
            "tests/schemas/modules/wrong_schema/same1/",
            "tests/schemas/modules/wrong_schema/same2/",
        ])


def test_multiple_types():
    with pytest.raises(SchemaErrorMutipleTypes):
        ForisValidator(["tests/schemas/modules/wrong_schema/multiple/"])


def test_redefinition():
    with pytest.raises(SchemaErrorDefinitionAlreadyUsed):
        ForisValidator([
            "tests/schemas/modules/wrong_schema/redefinition/redefinition1",
            "tests/schemas/modules/wrong_schema/redefinition/redefinition2",
        ])

    with pytest.raises(SchemaErrorDefinitionAlreadyUsed):
        ForisValidator([
            "tests/schemas/modules/wrong_schema/redefinition/redefinition3",
        ])

def test_redefinition_external_internal():
    with pytest.raises(SchemaErrorDefinitionAlreadyUsed):
        ForisValidator(
            ["tests/schemas/modules/definitions/",],
            ["tests/schemas/definitions/definitions-external/", ],
        )
        O
def test_redefinition_two_externals():
    with pytest.raises(SchemaErrorDefinitionAlreadyUsed):
        ForisValidator(
            ["tests/schemas/modules/simple/",],
            ["tests/schemas/definitions/redefinition/", ],
        )

def test_redefinition_base():
    with pytest.raises(SchemaErrorDefinitionAlreadyUsed):
        ForisValidator(
            ["tests/schemas/modules/simple/",],
            ["tests/schemas/definitions/redefinition_base/", ],
        )
