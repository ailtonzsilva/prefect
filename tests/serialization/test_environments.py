import datetime
import json

import marshmallow
import pytest

import prefect
from prefect import environments
from prefect.serialization.environment import (
    DockerEnvironmentSchema,
    EnvironmentSchema,
    LocalEnvironmentSchema,
)

FERNET_KEY = b"1crderTHVJ7vvVJj79Zns81_1opaTID0HRZoOzqIpOA="


def test_serialize_local_environment():
    env = environments.LocalEnvironment(encryption_key=FERNET_KEY)
    serialized = LocalEnvironmentSchema().dump(env)
    assert (
        serialized["encryption_key"]
        == "MWNyZGVyVEhWSjd2dlZKajc5Wm5zODFfMW9wYVRJRDBIUlpvT3pxSXBPQT0="
    )
    assert serialized["__version__"] == prefect.__version__


def test_deserialize_local_environment():
    env = environments.LocalEnvironment(encryption_key=FERNET_KEY)
    serialized = LocalEnvironmentSchema().dump(env)
    deserialized = LocalEnvironmentSchema().load(serialized)
    assert isinstance(deserialized, environments.LocalEnvironment)
    assert deserialized.encryption_key == FERNET_KEY


def test_serialize_container_environment():
    env = environments.DockerEnvironment(
        base_image="a",
        python_dependencies=["b", "c"],
        registry_url="f",
        image_name="g",
        image_tag="h",
    )
    serialized = DockerEnvironmentSchema().dump(env)
    assert serialized["base_image"] == "a"
    assert serialized["registry_url"] == "f"
    assert serialized["image_name"] == "g"
    assert serialized["image_tag"] == "h"
    assert serialized["__version__"] == prefect.__version__


def test_deserialize_empty_container_environment():
    schema = DockerEnvironmentSchema()
    with pytest.raises(marshmallow.ValidationError):
        schema.load(schema.dump({}))


def test_deserialize_minimal_container_environment():
    schema = DockerEnvironmentSchema()
    assert schema.load(schema.dump({"base_image": "a", "registry_url": "b"}))


def test_deserialize_container_environment():
    env = environments.DockerEnvironment(
        base_image="a", python_dependencies=["b", "c"], registry_url="f"
    )
    serialized = DockerEnvironmentSchema().dump(env)
    deserialized = DockerEnvironmentSchema().load(serialized)

    assert deserialized.base_image == env.base_image
    assert deserialized.registry_url == env.registry_url


def test_environment_schema_with_local_environment():
    env = environments.LocalEnvironment(encryption_key=FERNET_KEY)
    serialized = EnvironmentSchema().dump(env)
    deserialized = EnvironmentSchema().load(serialized)
    assert isinstance(deserialized, environments.LocalEnvironment)
    assert deserialized.encryption_key == FERNET_KEY


def test_environment_schema_with_container_environment():
    env = environments.DockerEnvironment(
        base_image="a", python_dependencies=["b", "c"], registry_url="f"
    )
    serialized = EnvironmentSchema().dump(env)
    deserialized = EnvironmentSchema().load(serialized)
    assert isinstance(deserialized, environments.DockerEnvironment)
    assert deserialized.registry_url == env.registry_url
    assert deserialized.base_image == env.base_image
