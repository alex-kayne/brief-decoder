import pytest
from pydantic import ValidationError

from app.providers.fake import VALID_RESPONSE, INVALID_SEVERITY_RESPONSE
from app.schemas import BriefDecodeResult


def test_valid_response_passes():
    result = BriefDecodeResult.model_validate_json(VALID_RESPONSE)
    assert result.summary
    assert result.risks and result.risks[0].severity == "high"


def test_malformed_json_rejected():
    with pytest.raises(ValidationError) as exc:
        BriefDecodeResult.model_validate_json('{"summary": "broken", not json')
    assert {e["type"] for e in exc.value.errors()} == {"json_invalid"}


def test_missing_fields_rejected():
    with pytest.raises(ValidationError) as exc:
        BriefDecodeResult.model_validate_json('{"summary": "only summary"}')
    kinds = {e["type"] for e in exc.value.errors()}
    assert kinds == {"missing"}
    missing_fields = {e["loc"][0] for e in exc.value.errors()}
    assert "goals" in missing_fields and "risks" in missing_fields


def test_invalid_severity_rejected():
    with pytest.raises(ValidationError) as exc:
        BriefDecodeResult.model_validate_json(INVALID_SEVERITY_RESPONSE)
    errors = exc.value.errors()
    assert {e["type"] for e in errors} == {"enum"}
    assert errors[0]["loc"] == ("risks", 0, "severity")
