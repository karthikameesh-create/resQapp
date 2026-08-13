import pytest
from pydantic import ValidationError

from app.schemas.incident import IncidentCreate, IncidentUpdate


def valid_incident_data():
    return {
        "title": "Road Accident",
        "description": "A bus collided with a truck near Mangalore.",
        "incident_type": "Traffic Accident",
        "latitude": 12.9141,
        "longitude": 74.8560,
    }


def test_valid_incident_is_accepted():
    incident = IncidentCreate(**valid_incident_data())

    assert incident.title == "Road Accident"
    assert incident.latitude == 12.9141
    assert incident.longitude == 74.8560


def test_title_too_short_is_rejected():
    data = valid_incident_data()
    data["title"] = "x"

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_title_too_long_is_rejected():
    data = valid_incident_data()
    data["title"] = "x" * 201

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_description_too_long_is_rejected():
    data = valid_incident_data()
    data["description"] = "x" * 5001

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_invalid_latitude_is_rejected():
    data = valid_incident_data()
    data["latitude"] = 91

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_invalid_longitude_is_rejected():
    data = valid_incident_data()
    data["longitude"] = 181

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_negative_latitude_is_rejected():
    data = valid_incident_data()
    data["latitude"] = -91

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_negative_longitude_beyond_range_is_rejected():
    data = valid_incident_data()
    data["longitude"] = -181

    with pytest.raises(ValidationError):
        IncidentCreate(**data)


def test_update_coordinates_are_validated():
    with pytest.raises(ValidationError):
        IncidentUpdate(latitude=100)

    with pytest.raises(ValidationError):
        IncidentUpdate(longitude=-200)


def test_update_title_length_is_validated():
    with pytest.raises(ValidationError):
        IncidentUpdate(title="x" * 201)


def test_update_description_length_is_validated():
    with pytest.raises(ValidationError):
        IncidentUpdate(description="x" * 5001)