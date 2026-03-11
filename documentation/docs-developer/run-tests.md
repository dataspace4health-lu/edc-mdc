---
slug: run-tests
sidebar_position: 5
sidebar_label: Run tests
---

# Run tests

Verify your code changes by running unit and functional tests for the Metadata Capture application.

In this guide  
> [Understand the testing strategy](#understand-the-testing-strategy)  
> [Run unit tests](#run-unit-tests)  
> [Run functional tests](#run-functional-tests)  

## Understand the testing strategy

The Metadata Capture application uses the following testing approaches to ensure code quality and functionality:

- **Unit tests:** Fast, isolated tests for individual functions and components using pytest
- **Functional tests:** Browser-based tests that verify user workflows using Playwright

## Run unit tests

 Test individual functions, classes, and components.

1. Go to the backend directory and activate your virtual environment:

   ```bash
   source venv/bin/activate   
    ```
2. Run all unit tests:

    ```bash
    pytest
    ```

    This command discovers and runs all tests in the `app/tests/` directory.


## Run functional tests

Verify complete user workflows using end-to-end (E2E) tests.

1. Start the required services for the testing environment:

    ```bash
    docker compose -f docker-compose.e2e.yaml down -v
    docker compose -f docker-compose.e2e.yaml build
    docker compose -f docker-compose.e2e.yaml up -d
    ```
2. Install test dependencies:

    ```bash
    cd e2e/
    npm install
    npx playwright install
    ```
    
3. Run the tests

    ```bash
    npm run test
