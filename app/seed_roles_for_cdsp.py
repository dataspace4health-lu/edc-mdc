from dependencies.database import get_script_db_session
from sqlalchemy import text


def main():
    db_session = get_script_db_session()  # Establish a database session

    try:
        db_session.execute(text("""
                INSERT INTO role (name) VALUES
                ('METADATA_EDITOR'),
                ('METADATA_REVIEWER'),
                ('METADATA_APPROVER'),
                ('INVENTORY_COORDINATOR')
            """))
        db_session.commit()
        print("Roles inserted successfully")
    except Exception as e:
        db_session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db_session.close()


if __name__ == "__main__":
    main()
