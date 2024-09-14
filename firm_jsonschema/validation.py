from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import referencing
import referencing.retrieval
from jsonschema import Draft202012Validator
from jsonschema.protocols import Validator
from referencing.jsonschema import DRAFT202012


def create_schema_retriever(schema_path: list[Path]):
    @referencing.retrieval.to_cached_resource()
    def _retriever(uri) -> str:
        for directory in schema_path:
            url = urlparse(uri)
            filepath = directory / f"{url.path}-schema.json"
            if filepath.exists() and filepath.is_file():
                with open(filepath) as fp:
                    return fp.read()
        raise FileNotFoundError(f"Schema not found: {uri}")

    return _retriever


def create_activity_validator(
    *,
    root_schema: str = "schema:activity",
    types=None,
    schema_path: list[str | Path] | None = None,
) -> Validator:
    types = set(types or [])
    schema_retriever = create_schema_retriever([Path(p) for p in (schema_path or [])])
    schema_registry = referencing.Registry(retrieve=schema_retriever)
    return Draft202012Validator(
        schema_retriever(root_schema).contents,
        registry=schema_registry.with_resource(
            uri="schema:known-activity-types",
            resource=referencing.Resource(
                contents={
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$id": "schema:known-activities",
                    # "oneOf": [{"const": a} for a in types],
                    "enum": types,
                },
                specification=DRAFT202012,
            ),
        ),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def validate_activity(activity: dict[str, Any], validator: Validator) -> dict[str, Any]:
    """Validates an activity and returns it, if valid."""
    validator.validate(activity)
    return activity


# class JsonSchemaValidator(firm.interfaces.Validator):
#     def __init__(
#         self,
#         *,
#         root_schema: str = "schema:activity",
#         types=None,
#         schema_path: list[str | Path] = None,
#     ):
#         self._validator = create_activity_validator(
#             root_schema=root_schema,
#             types=types,
#             schema_path=schema_path,
#         )

#     def validate(self, obj: firm.interfaces.JSONObject):
#         self._validator.validate(obj)
