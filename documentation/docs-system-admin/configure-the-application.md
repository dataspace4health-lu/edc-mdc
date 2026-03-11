---
sidebar_position: 3
---

# Configure the application

After you deploy the Metadata Capture application, configure it to work in your environment. The application uses a configuration file to manage key settings such as feature flags, database connections, and authentication.


Configure the application settings to work in your environment by editing and mounting the configuration file.

1. Open the configuration file located at `/app/config.json` in your Docker container.

    :::tip Default settings

    To see the default configuration, download the [**default config.json**](https://gitlab.com/lnds-lu/service-library/dca-metadata-capture/-/blob/main/app/config.json?ref_type=heads) file from the repository.

    :::

2. Modify the settings in the `config.json` file to match your environment. Key settings include:
    - **Application settings:** Configure `app_title` and `catalogue` information (name, description, publisher).
    - **Feature flags:** Enable or disable features and other functionality flags.

3. Configure the different aspects of the application:
    - [Set up authentication](set-up-authentication.md): Configure your OpenID Connect (OIDC) provider.
    - [Configure roles and permissions](configure-roles-and-permissions.md): Define your organisation's roles and their permissions.
    - [Configure email notifications](configure-email-notifications.md): Customize email templates for dataset record lifecycle events.

    <br/>

    :::tip Schema reference

    For details on the available settings and their expected values and formats, refer to the [**configuration schema**](https://gitlab.com/lnds-lu/service-library/dca-metadata-capture/-/blob/main/app/config.schema.json?ref_type=heads).

    :::

3. Mount the configuration file to make your changes persistent. Use either Docker Compose or the `docker run` command:

    If you are using **Docker Compose:**
    ```yaml
    services:
      app:
        environment:
          - CONFIG_PATH=/app/config.json
        volumes:
          - ./path/to/custom/config.json:/app/config.json
    ```

    If you are using **Docker run:**
    ```bash
    docker run -v $(pwd)/path/to/custom/config.json:/app/config.json <your-app-name> -e CONFIG_PATH=/app/config.json
    ```
