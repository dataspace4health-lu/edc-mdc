---
sidebar_position: 4
---

# Synchronise API schemas

Keep your frontend and backend in sync by regenerating API schemas after making changes to the backend API. 

In this guide

> [Generate updated schemas](#generate-updated-schemas)  
> [Verify the changes](#verify-the-changes)

 
## Generate updated schemas
Metadata Capture uses automatic OpenAPI schema generation to maintain synchronisation between the frontend and backend. After making changes to backend API endpoints, models, or validation rules, regenerate the frontend schemas.

1. Go to the frontend directory:
```bash
cd app/client/
```
2. Generate the latest API schemas:
```bash
npm run buildOpenAPISchema
```


## Verify the changes

After generating new schemas, verify that the changes are correct and complete.

1. Check the generated files for your new API endpoints or modified types.

2. Update your frontend code to use any new types or API functions.

3. Test the integration by running the frontend application and verifying that API calls work correctly.

