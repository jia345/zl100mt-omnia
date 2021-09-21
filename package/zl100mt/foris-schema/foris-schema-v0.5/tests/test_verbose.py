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


def test_request(validator):
    validator.validate_verbose({"module": "simple", "kind": "request", "action": "get"})


def test_reply(validator):
    validator.validate_verbose({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": False}
    })
    validator.validate_verbose({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": True}
    })


def test_notification(validator):
    validator.validate_verbose({"module": "simple", "kind": "notification", "action": "triggered"})
    validator.validate_verbose({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": "Passed"}
    })
    validator.validate_verbose({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": ""}
    })


def test_unknown_action(validator):

    with pytest.raises(ValidationError):
        validator.validate_verbose({"module": "simple", "kind": "request", "action": "non-existing"})

    with pytest.raises(ValidationError):
        validator.validate_verbose({
            "module": "simple", "kind": "reply", "action": "non-existing",
            "data": {"result": True}
        })

    with pytest.raises(ValidationError):
        validator.validate_verbose({"module": "simple", "kind": "notification", "action": "non-existing"})


def test_unknown_kind(validator):
    with pytest.raises(ValidationError):
        validator.validate_verbose({"module": "simple", "kind": "non-existing", "action": "triggered"})

    with pytest.raises(ValidationError):
        validator.validate_verbose({
            "module": "simple", "kind": "non-existing", "action": "get",
            "data": {"result": True}
        })

    with pytest.raises(ValidationError):
        validator.validate_verbose({"module": "simple", "kind": "non-existing", "action": "get"})


def test_unknown_module(validator):

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose(
            {"module": "non-existing", "kind": "notification", "action": "triggered"})
    assert "is not valid under any of the given schemas" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "non-existing", "kind": "reply", "action": "get",
            "data": {"result": True}
        })
    assert "is not valid under any of the given schemas" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({"module": "non-existing", "kind": "request", "action": "get"})
    assert "is not valid under any of the given schemas" in str(excinfo)


def test_data_presence(validator):
    validator.validate({"module": "simple", "kind": "request", "action": "get"})
    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose(
            {"module": "simple", "kind": "request", "action": "get", "data": {"result": True}})
    assert "'data' was unexpected" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "reply", "action": "get",
        })
    assert "'data' is a required property" in str(excinfo)
    validator.validate_verbose({
        "module": "simple", "kind": "reply", "action": "get",
        "data": {"result": True}
    })

    validator.validate_verbose({"module": "simple", "kind": "notification", "action": "triggered"})
    validator.validate_verbose({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": "Passed"}
    })
    validator.validate_verbose({
        "module": "simple", "kind": "notification", "action": "triggered",
        "data": {"event": ""}
    })
    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {}
        })
    assert "'event' is a required property" in str(excinfo)


def test_no_extra_properties(validator):
    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({"module": "simple", "kind": "request", "action": "get", "extra": False})
    assert "Additional properties are not allowed" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "reply", "action": "get",
            "data": {"result": False, "extra": False}
        })
    assert "Additional properties are not allowed" in str(excinfo)
    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "reply", "action": "get", "extra": False,
            "data": {"result": False}
        })
    assert "Additional properties are not allowed" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose(
            {"module": "simple", "kind": "notification", "action": "triggered", "extra": False})
    assert "Additional properties are not allowed" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {"event": "Passed", "extra": False}
        })
    assert "Additional properties are not allowed" in str(excinfo)

    with pytest.raises(ValidationError) as excinfo:
        validator.validate_verbose({
            "module": "simple", "kind": "notification", "action": "triggered",
            "data": {"extra": False}
        })
    assert "Additional properties are not allowed" in str(excinfo) or \
            "'event' is a required property" in str(excinfo)
