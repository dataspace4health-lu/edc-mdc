from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCAT, RDF
from unittest.mock import Mock

from models.contact import Contact
from models.identity_context import IdentityContext
from schemas.contact import ResourceContact
from services.catalogues.importers.contact_import_service import ContactImportService
from services.catalogues.mappers.namespace_constants import VCARD
from services.contact import ContactService


def _build_graph(include_email: bool = True):
    graph = Graph()
    dataset_uri = URIRef("http://example.com/dataset/1")
    contact_node = BNode()

    graph.add((dataset_uri, RDF.type, DCAT.Dataset))
    graph.add((dataset_uri, DCAT.contactPoint, contact_node))
    graph.add((contact_node, VCARD.fn, Literal("John Doe")))
    graph.add((contact_node, VCARD.role, Literal("Manager")))
    if include_email:
        graph.add((contact_node, VCARD.hasEmail, URIRef("mailto:john@example.com")))

    return graph, dataset_uri


def _make_service():
    contact_service = Mock(spec=ContactService)
    contact_repository = Mock()
    service = ContactImportService(
        contact_service=contact_service,
        contact_repository=contact_repository,
    )
    return service, contact_service, contact_repository


def test_ensure_contacts_creates_new_when_missing():
    service, contact_service, contact_repository = _make_service()
    graph, dataset_uri = _build_graph()
    identity = IdentityContext(user_id=1, permissions=[])

    contact_repository.get_contact_by_email.return_value = None
    expected_contact = ResourceContact(
        id=1,
        name="John Doe",
        email="john@example.com",
        role="Manager",
        is_deprecated=False,
    )
    contact_service.add_contact.return_value = expected_contact

    result = service.ensure_contacts_from_graph(
        graph,
        dataset_uri,
        organisation_id=10,
        identity=identity,
        skip_permission_validation=True,
    )

    assert len(result) == 1
    assert result[0] == expected_contact
    contact_service.add_contact.assert_called_once()
    args, kwargs = contact_service.add_contact.call_args
    assert args[0] == 10
    assert args[2] == identity
    assert kwargs["skip_permission_validation"] is True


def test_ensure_contacts_updates_when_details_change():
    service, contact_service, contact_repository = _make_service()
    graph, dataset_uri = _build_graph()
    identity = IdentityContext(user_id=1, permissions=[])

    existing_contact = Contact(
        id=5,
        name="Original",
        email="john@example.com",
        role="Analyst",
        organisation_id=10,
        is_deprecated=False,
    )
    contact_repository.get_contact_by_email.return_value = existing_contact

    updated_resource = ResourceContact(
        id=5,
        name="John Doe",
        email="john@example.com",
        role="Manager",
        is_deprecated=False,
    )
    contact_service.update_contact.return_value = updated_resource

    result = service.ensure_contacts_from_graph(
        graph,
        dataset_uri,
        organisation_id=10,
        identity=identity,
        skip_permission_validation=True,
    )

    assert len(result) == 1
    assert result[0] == updated_resource
    contact_service.update_contact.assert_called_once()
    args, kwargs = contact_service.update_contact.call_args
    assert args[0] == 10
    assert args[1] == existing_contact.id
    contact_dto = args[2]
    assert contact_dto.name == "John Doe"
    assert contact_dto.email == "john@example.com"
    assert contact_dto.role == "Manager"
    assert args[3] == identity
    assert kwargs["skip_permission_validation"] is True


def test_ensure_contacts_returns_existing_when_no_changes():
    service, contact_service, contact_repository = _make_service()
    graph, dataset_uri = _build_graph()
    identity = IdentityContext(user_id=1, permissions=[])

    existing_contact = Contact(
        id=5,
        name="John Doe",
        email="john@example.com",
        role="Manager",
        organisation_id=10,
        is_deprecated=False,
    )
    contact_repository.get_contact_by_email.return_value = existing_contact

    result = service.ensure_contacts_from_graph(
        graph,
        dataset_uri,
        organisation_id=10,
        identity=identity,
        skip_permission_validation=True,
    )

    assert len(result) == 1
    assert isinstance(result[0], ResourceContact)
    assert result[0].id == existing_contact.id
    assert result[0].name == existing_contact.name
    contact_service.update_contact.assert_not_called()
    contact_service.add_contact.assert_not_called()


def test_ensure_contacts_returns_empty_when_email_missing():
    service, contact_service, contact_repository = _make_service()
    graph, dataset_uri = _build_graph(include_email=False)
    identity = IdentityContext(user_id=1, permissions=[])

    result = service.ensure_contacts_from_graph(
        graph, dataset_uri, organisation_id=10, identity=identity
    )

    assert result == []
    contact_service.add_contact.assert_not_called()
    contact_service.update_contact.assert_not_called()
