import uuid
import dataclasses
import pathlib
import pickle
import pytest
from tempus.lib.persistence import prototyping


@dataclasses.dataclass
class DomainAgg:
    id: uuid.UUID
    name: str


@pytest.fixture(scope="function")
def subject_with_path():
    path = pathlib.Path("prototyping_repo_foo.pickle")
    if path.exists():
        path.unlink()
    subject = prototyping._PrototypingRepo("foo")
    return subject, path


def test_prototyping_repo_commits(subject_with_path):
    subject, path = subject_with_path
    obj = DomainAgg(id=None, name="bar")
    subject.add(obj)
    assert not path.exists()
    subject.commit()
    assert path.exists()


def test_prototyping_repo_loads_again(subject_with_path):
    subject, path = subject_with_path
    obj = DomainAgg(id=None, name="bar")
    subject.add(obj)
    subject.commit()
    another = prototyping._PrototypingRepo("foo")
    assert another.get(obj.id) == obj


def test_prototyping_repo_rollsback(subject_with_path):
    subject, path = subject_with_path
    obj = DomainAgg(id=None, name="bar")
    subject.add(obj)
    subject.rollback()
    assert subject.get(obj.id) is None


def test_prototyping_repo_rollsback_with_existing(subject_with_path):
    subject, path = subject_with_path
    obj1 = DomainAgg(id=None, name="bar")
    subject.add(obj1)
    subject.commit()

    obj2 = DomainAgg(id=None, name="hurz")
    subject.add(obj2)
    subject.rollback()

    assert list(subject.many()) == [obj1]
