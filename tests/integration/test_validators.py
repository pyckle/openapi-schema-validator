import pytest
from jsonschema import ValidationError

from openapi_schema_validator import OAS30Validator
from openapi_schema_validator import OAS31Validator
from openapi_schema_validator import oas30_format_checker
from openapi_schema_validator import oas31_format_checker

try:
    from unittest import mock
except ImportError:
    from unittest import mock


class TestOAS30ValidatorValidate:
    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_null(self, schema_type):
        schema = {"type": schema_type}
        validator = OAS30Validator(schema)
        value = None

        with pytest.raises(ValidationError):
            validator.validate(value)

    @pytest.mark.parametrize("is_nullable", [True, False])
    def test_nullable_untyped(self, is_nullable):
        schema = {"nullable": is_nullable}
        validator = OAS30Validator(schema)
        value = None

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_nullable(self, schema_type):
        schema = {"type": schema_type, "nullable": True}
        validator = OAS30Validator(schema)
        value = None

        result = validator.validate(value)

        assert result is None

    def test_nullable_enum_without_none(self):
        schema = {"type": "integer", "nullable": True, "enum": [1, 2, 3]}
        validator = OAS30Validator(schema)
        value = None

        with pytest.raises(ValidationError):
            validator.validate(value)

    def test_nullable_enum_with_none(self):
        schema = {"type": "integer", "nullable": True, "enum": [1, 2, 3, None]}
        validator = OAS30Validator(schema)
        value = None

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_no_datetime_validator(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        True,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_datetime_rfc3339_validator(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339", True
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_datetime_strict_rfc3339(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", True
    )
    def test_string_format_datetime_isodate(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-00Z",
            "2018",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", True
    )
    def test_string_format_datetime_invalid_isodate(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        with pytest.raises(
            ValidationError, match=f"'{value}' is not a 'date-time'"
        ):
            validator.validate(value)

    @pytest.mark.parametrize(
        "value",
        [
            "f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
            "F50EC0B7-F960-400D-91F0-C42A6D44E3D0",
        ],
    )
    def test_string_uuid(self, value):
        schema = {"type": "string", "format": "uuid"}
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)

        result = validator.validate(value)

        assert result is None

    def test_allof_required(self):
        schema = {
            "allOf": [
                {
                    "type": "object",
                    "properties": {"some_prop": {"type": "string"}},
                },
                {"type": "object", "required": ["some_prop"]},
            ]
        }
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)
        with pytest.raises(
            ValidationError, match="'some_prop' is a required property"
        ):
            validator.validate({"another_prop": "bla"})

    def test_required(self):
        schema = {
            "type": "object",
            "properties": {"some_prop": {"type": "string"}},
            "required": ["some_prop"],
        }

        validator = OAS30Validator(schema, format_checker=oas30_format_checker)
        with pytest.raises(
            ValidationError, match="'some_prop' is a required property"
        ):
            validator.validate({"another_prop": "bla"})
        assert validator.validate({"some_prop": "hello"}) is None

    def test_read_only(self):
        schema = {
            "type": "object",
            "properties": {"some_prop": {"type": "string", "readOnly": True}},
        }

        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, write=True
        )
        with pytest.raises(
            ValidationError, match="Tried to write read-only property with hello"
        ):
            validator.validate({"some_prop": "hello"})
        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, read=True
        )
        assert validator.validate({"some_prop": "hello"}) is None

    def test_write_only(self):
        schema = {
            "type": "object",
            "properties": {"some_prop": {"type": "string", "writeOnly": True}},
        }

        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, read=True
        )
        with pytest.raises(
            ValidationError, match="Tried to read write-only property with hello"
        ):
            validator.validate({"some_prop": "hello"})
        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, write=True
        )
        assert validator.validate({"some_prop": "hello"}) is None

    def test_required_read_only(self):
        schema = {
            "type": "object",
            "properties": {"some_prop": {"type": "string", "readOnly": True}},
            "required": ["some_prop"],
        }

        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, read=True
        )
        with pytest.raises(
            ValidationError, match="'some_prop' is a required property"
        ):
            validator.validate({"another_prop": "hello"})
        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, write=True
        )
        assert validator.validate({"another_prop": "hello"}) is None

    def test_required_write_only(self):
        schema = {
            "type": "object",
            "properties": {"some_prop": {"type": "string", "writeOnly": True}},
            "required": ["some_prop"],
        }

        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, write=True
        )
        with pytest.raises(
            ValidationError, match="'some_prop' is a required property"
        ):
            validator.validate({"another_prop": "hello"})
        validator = OAS30Validator(
            schema, format_checker=oas30_format_checker, read=True
        )
        assert validator.validate({"another_prop": "hello"}) is None

    def test_oneof_required(self):
        instance = {
            "n3IwfId": "string",
        }
        schema = {
            "type": "object",
            "properties": {
                "n3IwfId": {"type": "string"},
                "wagfId": {"type": "string"},
            },
            "oneOf": [
                {"required": ["n3IwfId"]},
                {"required": ["wagfId"]},
            ],
        }
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)
        result = validator.validate(instance)
        assert result is None

    @pytest.mark.parametrize(
        "schema_type",
        [
            "oneOf",
            "anyOf",
            "allOf",
        ],
    )
    def test_oneof_discriminator(self, schema_type):
        # We define a few components schemas
        components = {
            "MountainHiking": {
                "type": "object",
                "properties": {
                    "discipline": {
                        "type": "string",
                        # we allow both the explicitely matched mountain_hiking discipline
                        # and the implicitely matched MoutainHiking discipline
                        "enum": ["mountain_hiking", "MountainHiking"],
                    },
                    "length": {
                        "type": "integer",
                    },
                },
                "required": ["discipline", "length"],
            },
            "AlpineClimbing": {
                "type": "object",
                "properties": {
                    "discipline": {
                        "type": "string",
                        "enum": ["alpine_climbing"],
                    },
                    "height": {
                        "type": "integer",
                    },
                },
                "required": ["discipline", "height"],
            },
            "Route": {
                # defined later
            },
        }
        components["Route"][schema_type] = [
            {"$ref": "#/components/schemas/MountainHiking"},
            {"$ref": "#/components/schemas/AlpineClimbing"},
        ]

        # Add the compoments in a minimalis schema
        schema = {
            "$ref": "#/components/schemas/Route",
            "components": {"schemas": components},
        }

        if schema_type != "allOf":
            # use jsonschema validator when no discriminator is defined
            validator = OAS30Validator(
                schema, format_checker=oas30_format_checker
            )
            with pytest.raises(
                ValidationError,
                match="is not valid under any of the given schemas",
            ):
                validator.validate(
                    {"something": "matching_none_of_the_schemas"}
                )
                assert False

        if schema_type == "anyOf":
            # use jsonschema validator when no discriminator is defined
            validator = OAS30Validator(
                schema, format_checker=oas30_format_checker
            )
            with pytest.raises(
                ValidationError,
                match="is not valid under any of the given schemas",
            ):
                validator.validate(
                    {"something": "matching_none_of_the_schemas"}
                )
                assert False

        discriminator = {
            "propertyName": "discipline",
            "mapping": {
                "mountain_hiking": "#/components/schemas/MountainHiking",
                "alpine_climbing": "#/components/schemas/AlpineClimbing",
            },
        }
        schema["components"]["schemas"]["Route"][
            "discriminator"
        ] = discriminator

        # Optional: check we return useful result when the schema is wrong
        validator = OAS30Validator(schema, format_checker=oas30_format_checker)
        with pytest.raises(
            ValidationError, match="does not contain discriminating property"
        ):
            validator.validate({"something": "missing"})
            assert False

        # Check we get a non-generic, somehow usable, error message when a discriminated schema is failing
        with pytest.raises(
            ValidationError, match="'bad_string' is not of type 'integer'"
        ):
            validator.validate(
                {"discipline": "mountain_hiking", "length": "bad_string"}
            )
            assert False

        # Check explicit MountainHiking resolution
        validator.validate({"discipline": "mountain_hiking", "length": 10})

        # Check implicit MountainHiking resolution
        validator.validate({"discipline": "MountainHiking", "length": 10})

        # Check non resolvable implicit schema
        with pytest.raises(
            ValidationError,
            match="reference '#/components/schemas/other' could not be resolved",
        ):
            result = validator.validate({"discipline": "other"})
            assert False

    @pytest.mark.parametrize("is_nullable", [True, False])
    def test_nullable_ref(self, is_nullable):
        """
        Tests that a field that points to a schema reference is null checked based on the $ref schema rather than
        on this schema
        :param is_nullable:  if the schema is marked as nullable. If not, validate an exception is raised on None
        """
        schema = {
            "$ref": "#/$defs/Pet",
            "$defs": {
                "NullableText": {
                    "type": "string",
                    "nullable": is_nullable
                },
                "Pet": {
                    "properties": {
                        "testfield": {"$ref": "#/$defs/NullableText"},
                    },
                }
            },
        }
        validator = OAS30Validator(
            schema,
            format_checker=oas30_format_checker,
        )

        result = validator.validate({"testfield": "John"})
        assert result is None

        if is_nullable:
            result = validator.validate({"testfield": None})
            assert result is None
        else:
            with pytest.raises(
                    ValidationError,
                    match="None for not nullable",
            ):
                validator.validate({"testfield": None})
                assert False


    @pytest.mark.parametrize(
        "schema_type, not_nullable_regex",
        [
            ("oneOf", "None is not valid under any of the given schemas"),
            ("anyOf", "None is not valid under any of the given schemas"),
            ("allOf", "None for not nullable")
        ],
    )
    @pytest.mark.parametrize("is_nullable", [True, False])
    def test_nullable_schema_combos(self, is_nullable, schema_type, not_nullable_regex):
        """
        This test ensures that nullablilty semantics are correct for oneOf, anyOf and allOf
        Specifically, nullable should checked on the children schemas
        :param is_nullable:  if the schema is marked as nullable. If not, validate an exception is raised on None
        :param schema_type: the schema type to validate
        :param not_nullable_regex: the expected raised exception if fields are marked as not nullable
        """
        schema = {
            "$ref": "#/$defs/Pet",
            "$defs": {
                "NullableText": {
                    "type": "string",
                    "nullable": False if schema_type == "oneOf" else is_nullable
                },
                "NullableEnum": {
                    "type": "string",
                    "nullable": is_nullable,
                    "enum": ["John", "Alice", None]
                },
                "Pet": {
                    "properties": {
                        "testfield": {
                            schema_type: [
                                {"$ref": "#/$defs/NullableText"},
                                {"$ref": "#/$defs/NullableEnum"},
                            ]
                        }
                    },
                }
            },
        }
        validator = OAS30Validator(
            schema,
            format_checker=oas30_format_checker,
        )

        if is_nullable:
            result = validator.validate({"testfield": None})
            assert result is None
        else:
            with pytest.raises(
                    ValidationError,
                    match=not_nullable_regex
            ):
                validator.validate({"testfield": None})
                assert False

class TestOAS31ValidatorValidate:
    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_null(self, schema_type):
        schema = {"type": schema_type}
        validator = OAS31Validator(schema)
        value = None

        with pytest.raises(ValidationError):
            validator.validate(value)

    @pytest.mark.parametrize(
        "schema_type",
        [
            "boolean",
            "array",
            "integer",
            "number",
            "string",
        ],
    )
    def test_nullable(self, schema_type):
        schema = {"type": [schema_type, "null"]}
        validator = OAS31Validator(schema)
        value = None

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_no_datetime_validator(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        True,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_datetime_rfc3339_validator(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339", True
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", False
    )
    def test_string_format_datetime_strict_rfc3339(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "1989-01-02T00:00:00Z",
            "2018-01-02T23:59:59Z",
        ],
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_RFC3339_VALIDATOR",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_STRICT_RFC3339",
        False,
    )
    @mock.patch(
        "openapi_schema_validator._format." "DATETIME_HAS_ISODATE", True
    )
    def test_string_format_datetime_isodate(self, value):
        schema = {"type": "string", "format": "date-time"}
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            "f50ec0b7-f960-400d-91f0-c42a6d44e3d0",
            "F50EC0B7-F960-400D-91F0-C42A6D44E3D0",
        ],
    )
    def test_string_uuid(self, value):
        schema = {"type": "string", "format": "uuid"}
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    def test_schema_validation(self):
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "age": {
                    "type": "integer",
                    "format": "int32",
                    "minimum": 0,
                    "nullable": True,
                },
                "birth-date": {
                    "type": "string",
                    "format": "date",
                },
            },
            "additionalProperties": False,
        }
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate({"name": "John", "age": 23})
        assert result is None

        with pytest.raises(ValidationError) as excinfo:
            validator.validate({"name": "John", "city": "London"})

        error = "Additional properties are not allowed ('city' was unexpected)"
        assert error in str(excinfo.value)

        with pytest.raises(ValidationError) as excinfo:
            validator.validate({"name": "John", "birth-date": "-12"})

        error = "'-12' is not a 'date'"
        assert error in str(excinfo.value)

    def test_schema_ref(self):
        schema = {
            "$ref": "#/$defs/Pet",
            "$defs": {
                "Pet": {
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"},
                        "tag": {"type": "string"},
                    },
                }
            },
        }
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate({"id": 1, "name": "John"})
        assert result is None

        with pytest.raises(ValidationError) as excinfo:
            validator.validate({"name": "John"})

        error = "'id' is a required property"
        assert error in str(excinfo.value)

    @pytest.mark.parametrize(
        "value",
        [
            [1600, "Pennsylvania", "Avenue", "NW"],
            [1600, "Pennsylvania", "Avenue"],
        ],
    )
    def test_array_prefixitems(self, value):
        schema = {
            "type": "array",
            "prefixItems": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Boulevard"]},
                {"enum": ["NW", "NE", "SW", "SE"]},
            ],
            "items": False,
        }
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        result = validator.validate(value)

        assert result is None

    @pytest.mark.parametrize(
        "value",
        [
            [1600, "Pennsylvania", "Avenue", "NW", "Washington"],
        ],
    )
    def test_array_prefixitems_invalid(self, value):
        schema = {
            "type": "array",
            "prefixItems": [
                {"type": "number"},
                {"type": "string"},
                {"enum": ["Street", "Avenue", "Boulevard"]},
                {"enum": ["NW", "NE", "SW", "SE"]},
            ],
            "items": False,
        }
        validator = OAS31Validator(
            schema,
            format_checker=oas31_format_checker,
        )

        with pytest.raises(ValidationError) as excinfo:
            validator.validate(value)

        error = "Expected at most 4 items, but found 5"
        assert error in str(excinfo.value)
