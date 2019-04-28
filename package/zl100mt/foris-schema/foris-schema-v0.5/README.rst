Foris schema
============

Library which validates whether the json matches the protocol use between Foris web and a configuration backend.

Requirements
============

* jsonschema

Installation
============

	``python setup.py install``

Schema format
=============

The format should be jsonschema format (Draf 4) and it should fill some mandatory fields e.g.::

	{
		"oneOf": [
			{
				"description": "Reply to call get action in simple module",
				"properties": {
					"module": {"enum": ["simple"]},
					"kind": {"enum": ["reply"]},
					"action": {"enum": ["get"]},
					"data": {
						"type": "object",
						"properties": {
							"result": {"type": "boolean"}
						},
						"additionalProperties": false,
						"required": ["result"]
					}
				},
				"additionalProperties": false,
				"required": ["data"]
			}
		]
	}

The mandatory fields are `kind`, `module`, `action`, optional `data`.
Note that `module` should be the same as the file name, `action` should be string and `kind` should be one `request`, `reply`, `notification`.

Definitions
-----------
Note that every schema file can use local definitions to reuse some parts of the schema::

	{
		"definitions": {
		"lower": {
			"type": "string",
			"pattern": "^[a-z]+$"
		},
		...
			"small_string": {"$ref": "#/definitions/lower"}
		...
	}

For details see https://spacetelescope.github.io/understanding-json-schema/structuring.html

Usage
=====

To validate::

	from foris_schema import ForisValidator
	validator = ForisValidator(["path/to/dir/with/schemas"])
	validator.validate({"module": "simple", "kind": "request", "action": "get"})

To validate a particular part of the module (to get more verbose output)::

	validator.validate({"module": "simple", "kind": "request", "action": "get"}, "simple", 0)
