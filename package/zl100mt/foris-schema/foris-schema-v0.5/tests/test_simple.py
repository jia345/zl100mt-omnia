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

from jsonschema import ValidationError

from foris_schema import ForisValidator


@pytest.fixture(scope="module")
def validator():
    return ForisValidator(["tests/schemas/modules/simple/"])


def test_schema_load(validator):
    pass


def test_schema_property(validator):
    assert isinstance(validator.schema, dict)


def test_request(validator):
    validator.validate({"module": "simple", "kind": "request", "action": "get"})


def test_reply(validator):
    validator.validate({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": False}
    })
    validator.validate({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": True}
    })


def test_notification(validator):
    validator.validate({"module": "simple", "kind": "notification", "action": "triggered"})
    validator.validate({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": "Passed"}
    })
    validator.validate({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": ""}
    })


def test_unknown_action(validator):

    with pytest.raises(ValidationError):
        validator.validate({"module": "simple", "kind": "request", "action": "non-existing"})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "reply", "action": "non-existing",
            "data": {"result": True}
        })

    with pytest.raises(ValidationError):
        validator.validate({"module": "simple", "kind": "notification", "action": "non-existing"})


def test_unknown_kind(validator):
    with pytest.raises(ValidationError):
        validator.validate({"module": "simple", "kind": "non-existing", "action": "triggered"})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "non-existing", "action": "get",
            "data": {"result": True}
        })

    with pytest.raises(ValidationError):
        validator.validate({"module": "simple", "kind": "non-existing", "action": "get"})


def test_unknown_module(validator):

    with pytest.raises(ValidationError):
        validator.validate({"module": "non-existing", "kind": "notification", "action": "triggered"})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "non-existing", "kind": "reply", "action": "get",
            "data": {"result": True}
        })

    with pytest.raises(ValidationError):
        validator.validate({"module": "non-existing", "kind": "request", "action": "get"})


def test_data_presence(validator):
    validator.validate({"module": "simple", "kind": "request", "action": "get"})
    with pytest.raises(ValidationError):
        validator.validate(
            {"module": "simple", "kind": "request", "action": "get", "data": {"result": True}})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "reply", "action": "get",
        })
    validator.validate({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": True}
    })

    validator.validate({"module": "simple", "kind": "notification", "action": "triggered"})
    validator.validate({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": "Passed"}
    })
    validator.validate({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": ""}
    })
    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {}
        })


def test_no_extra_properties(validator):
    with pytest.raises(ValidationError):
        validator.validate({"module": "simple", "kind": "request", "action": "get", "extra": False})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "reply", "action": "get",
            "data": {"result": False, "extra": False}
        })
    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "reply", "action": "get", "extra": False,
            "data": {"result": False}
        })

    with pytest.raises(ValidationError):
        validator.validate(
            {"module": "simple", "kind": "notification", "action": "triggered", "extra": False})

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {"event": "Passed", "extra": False}
        })

    with pytest.raises(ValidationError):
        validator.validate({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {"extra": False}
        })
