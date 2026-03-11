from models.contact import Contact


def create_sample_contact(
    id=None,
    name="Napoleon Bonaparte",
    email="napoleon@lnds.lu",
    role="Emperor",
    organisation_id=1,
    is_deprecated=False,
):
    return Contact(
        id=id,
        name=name,
        email=email,
        role=role,
        organisation_id=organisation_id,
        is_deprecated=is_deprecated,
    )
