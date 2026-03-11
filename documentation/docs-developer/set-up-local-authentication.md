---
sidebar_position: 2
sidebar_label: Set up local authentication
---

# Set up local authentication

Configure a local **Keycloak** instance for development to enable user authentication for predefined test users. 

In this guide  
> [Understand development authentication](#understand-development-authentication)  
> [Run Keycloak locally](#run-keycloak-locally)  
> [Sign in with test users](#sign-in-with-test-users)  
> [Manage test users](#manage-test-users)


## Understand development authentication

During development, you need a local authentication provider to test user login, role-based access, and permission systems. The Metadata Capture project includes a pre-configured Keycloak instance with: 

- **Test realm:** `dca-metadata-capture-local` configured for development
- **Predefined test users:** Users with different roles for testing different access levels
- **Role mapping:** Roles with permissions that match the application's default configuration
- **Client configuration:** Ready-to-use OIDC client settings

This local setup mirrors the production authentication flow while providing predictable test data for development.

## Run Keycloak locally

The project includes a Docker Compose configuration that starts Keycloak with the development realm pre-configured.


1. Start Keycloak using Docker Compose:
   
   ```bash
   cd e2e/
   docker compose -f docker-compose.e2e.yaml up -d keycloak
   ```

2. Configure authentication environment variables.

    Edit the `.env` file in your project to include the following Keycloak connection details:

    ```plaintext
    OPENID_CLIENT_ID=dca-metadata-capture-local
    OPENID_CLIENT_SECRET=ypctz2GbUYM4qNMg48BRGNfVzgFTINzJ
    OPENID_AUTH_URL=http://localhost:8080/realms/dca-metadata-capture-local/protocol/openid-connect/auth
    OPENID_TOKEN_URL=http://localhost:8080/realms/dca-metadata-capture-local/protocol/openid-connect/token
    OPENID_JWKS_URL=http://localhost:8080/realms/dca-metadata-capture-local/protocol/openid-connect/certs
    OPENID_END_SESSION_URL=http://localhost:8080/realms/dca-metadata-capture-local/protocol/openid-connect/logout
    ```

    This connects your application to the locally running Keycloak instance.

3. Access the application using the [predefined test users](#sign-in-with-test-users).

## Sign in with test users

The local Keycloak instance includes predefined test users with different roles and permissions for comprehensive testing. Sign in to the Metadata Capture app locally using the predefined test accounts.

1. [Run the app locally](set-up-a-developer-env.md#run-the-app-locally) at `http://localhost:5173`.

2. Select **Sign in** to open the Keycloak login page.

3. Find the list of available test users and their credentials in [login-as.ts](https://gitlab.com/lnds-lu/service-library/dca-metadata-capture/-/blob/main/e2e/test-utils/login-as.ts?ref_type=heads). 

    The test user accounts include the following roles:
    - **Administrator:** Full system access and management permissions
    - **Data Manager:** Can create, edit, and manage datasets
    - **Validator:** Can review and validate submitted datasets
    - **Viewer:** Read-only access to published datasets


4. Verify role-based access by logging in with different test users and notice how the application interface changes based on permissions.

## Manage test users

Use the Keycloak admin console to modify test users, their roles, and client configurations during development.

1. Open the Keycloadmin console at `http://localhost:8080/admin/`.

2. Sign in with admin credentials:
    - **Username:** admin
    - **Password:** admin

3. Perform admin tasks for managing test user accounts:
    - **Manage users:** Add, edit, or delete test users
    - **Configure roles:** Modify role assignments and permissions
    - **Client settings:** Adjust OIDC client configuration if needed
    - **View logs:** Monitor authentication events and troubleshoot issues