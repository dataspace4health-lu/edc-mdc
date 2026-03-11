---
slug: work-with-the-database
sidebar_position: 3
sidebar_label: Work with the database
---

# Work with the database

Manage database schema changes, create migrations, and work with development data in the Metadata Capture application.

In this guide  
> [Understand the database structure](#understand-the-database-structure)  
> [Seed initial data](#seed-initial-data)  
> [Create and apply migrations](#create-and-apply-migrations)

## Understand the database structure

The Metadata Capture application uses PostgreSQL as its primary database and SQLAlchemy as the Object-Relational Mapping (ORM) framework. Key components include:

- **Models**: Python classes in `app/models/` that define database tables and relationships
- **Alembic**: Database migration tool that manages schema changes in a version-controlled manner
- **Migrations**: Python scripts in `app/alembic/versions/` that track and apply database changes
- **Seeds**: Initial data scripts in for development and testing environments

<!-- Review -->

The database schema supports the application's core features including **datasets**, **organisations**, and **roles and permissions**.

## Seed initial data

The Metadata Capture application includes a mechanism that populates your development database with initial data for testing and development through the `app/initial_data.sql` file.

To load initial data when you first set up your environment, edit the `.env` file to include:

```bash
LOAD_INITIAL_DATA=True
```

After your first migration, remove or set this flag to `False` to prevent reloading initial data on subsequent migrations.

```bash
LOAD_INITIAL_DATA=False
```

## Create and apply migrations

After you modify database models, you need to create migration scripts to update the database schema.

Generate a new migration script:

```bash
$ alembic revision -m "a description of your changes"
$ alembic upgrade head
``` 

:::note Well done!

Now that you understand how to work with the database, learn how to [run tests](run-tests.md) to verify your changes, or explore **developing API changes** to extend application functionality.

::: 

