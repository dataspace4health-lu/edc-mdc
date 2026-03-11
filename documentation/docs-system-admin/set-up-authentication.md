---
sidebar_position: 4
---

# Set up authentication

Metadata Capture uses an external **OpenID Connect (OIDC)** provider to manage user authentication and permissions. Common OIDC providers include Keycloak, Auth0, and Azure Active Directory. 

In this guide  
> [Prerequisite](#prerequisite)  
> [Configure your OIDC provider](#configure-your-oidc-provider)  
> [Set up environment variables](#set-up-environment-variables)  
> [Configure role mapping](#configure-role-mapping)

## Prerequisite

Ensure your organisation has its own **Identity and Access Management (IAM)** system to control access and role assignments within the application.

## Configure your OIDC provider

Before you deploy the application, configure your OIDC provider with the required settings. 

1. Create a **client application** in your OIDC provider.
2. Generate client credentials, **client ID** and **client secret**.
3. Configure **redirect URIs** to match your application's domain.
4. Set up **role configuration** to ensure roles are included the JWT token.

## Set up environment variables

To connect Metadata Capture to your OIDC provider, configure the following variables in your [`.env` file](deploy-metadata-capture.md#configure-your-environment):

```bash
OPENID_CLIENT_ID=<your-client-id>
OPENID_CLIENT_SECRET=<your-client-secret>
OPENID_AUTH_URL=<https://your-provider.com/auth/realms/your-realm/protocol/openid-connect/auth>
OPENID_TOKEN_URL=<https://your-provider.com/auth/realms/your-realm/protocol/openid-connect/token>
OPENID_JWKS_URL=<https://your-provider.com/auth/realms/your-realm/protocol/openid-connect/certs>
OPENID_END_SESSION_URL=<https://your-provider.com/auth/realms/your-realm/protocol/openid-connect/logout>
```

## Configure role mapping

1. Ensure your OIDC provider returns user roles in the `resource_access` claim of the JWT token. The expected format is:

    ```json
    {
      "resource_access": {
        "your-client-id": {
          "roles": ["role_name_1", "role_name_2"]
        }
      }
    }
    ```

2. Set the roles path in the JWT token by modifying the `config.json` file. See: [Configure roles and permissions](configure-roles-and-permissions.md).

<br/>

:::note Well done!

Now that you have configured authentication, you can [configure roles and permissions](configure-roles-and-permissions.md).

:::
