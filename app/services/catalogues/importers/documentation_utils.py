from rdflib import BNode, Graph, Literal, URIRef


def get_documentation_values(
    graph: Graph, subject: URIRef | BNode, predicate: URIRef
) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for obj in graph.objects(subject, predicate):
        if isinstance(obj, (URIRef, Literal)):
            value = str(obj)
            if value.startswith("file://"):
                value = value.rsplit("/", 1)[-1] or value
            if value not in seen:
                seen.add(value)
                values.append(value)
    return values
