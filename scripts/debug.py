from pathlib import Path

from jsonschema import ValidationError

from firm_jsonschema.validation import create_activity_validator

if __name__ == "__main__":
    try:
        validator = create_activity_validator(
            types=["Follow", "Accept", "Reject"],
            schema_path=[Path(__file__).parent / "../tests/schemas"],
        )
        validator.validate({"type": ["Follow", "Reject"]})
        print("PASS")
    except ValidationError as ex:
        print(ex)
