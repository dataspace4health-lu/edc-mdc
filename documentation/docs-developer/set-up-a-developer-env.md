---
sidebar_position: 1
sidebar_label: Set up a developer environment
---

# Set up a developer environment

Set up your local development environment to start developing and testing the Metadata Capture application.

In this guide  
> [Prerequisites](#prerequisites)  
> [Clone the repository](#clone-the-repository)  
> [Set up the backend environment](#set-up-the-backend-environment)  
> [Set up the frontend environment](#set-up-the-frontend-environment)  
> [Run the app locally](#run-the-app-locally)

## Prerequisites

Ensure you have the following tools installed on your development machine:

- **Git:** Version control system for cloning the repository
- **Python 3.12:** For running the backend services
- **Node.js 20.x:** For frontend development and build tools
- **Docker:** For running local services (database, authentication)
- **Redis (optional but required for background jobs):** Task queue broker/back-end


## Clone the repository

1. Clone the Metadata Capture repository to your local machine:

   ```bash
   git clone git@gitlab.com:lnds-lu/service-library/dca-metadata-capture.git
   cd dca-metadata-capture
   ```

2. Install pre-commit hooks to maintain code quality:

   ```bash
   pre-commit install
   ```

## Set up the backend environment

The backend is built with Python.

1. Install Python 3.12 using pyenv:

   ```bash
   pyenv install 3.12
   ```
2. Create and activate a virtual environment in the backend directory:

   ```bash
   python -m venv venv
   source venv/bin/activate   
   ```

3. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   ```bash
   cp .env.<example> .env
   ```

   For first-time setup, edit the `.env` file to include:

   ```bash
   LOAD_INITIAL_DATA=True
   ```
   :::info Initial data loading

   The `LOAD_INITIAL_DATA` flag loads initial data into the database during the **first migration**. Make sure you **disable** this flag in your subsequent migrations to prevent data conflicts. Read more about [seeding initial data](work-with-the-databse.md#seed-initial-data).

   :::

5. Initialise the database:

   ```bash
   alembic upgrade head
   ```

### Run background jobs

Some features rely on Celery workers. To run background jobs locally you need Redis and two Celery processes (worker + beat scheduler).

1. **Install and start Redis**

   - **macOS (Homebrew)**

     ```bash
     brew install redis
     brew services start redis
     ```

   - **Windows (Chocolatey, PowerShell as Administrator)**

     ```powershell
     choco install redis-64
     Start-Service redis
     ```

2. **Start Celery worker and beat**

   ```bash
   cd app
   source venv/bin/activate

   # Load environment variables
   export CELERY_BROKER_URL=redis://localhost:6379/0
   export CELERY_RESULT_BACKEND=redis://localhost:6379/1

   # Start worker (processes tasks)
   celery -A jobs worker --loglevel=info
   ```

   In a second terminal:

   ```bash
   cd app
   source venv/bin/activate
   export CELERY_BROKER_URL=redis://localhost:6379/0
   export CELERY_RESULT_BACKEND=redis://localhost:6379/1

   # Start Beat scheduler (separate process)
   celery -A jobs beat --loglevel=info
   ```

## Set up the frontend environment

The frontend is built with React, TypeScript, and Vite.  

Install frontend dependencies:

```bash
cd app/client/
npm install
```

## Run the app locally

Run the Metadata Capture app locally to verify that your development environment is correctly configured:

1. Start the backend server:

   ```bash
   python main.py
   ```

   The backend starts on `http://localhost:8000`.

2. In a new terminal, start the frontend development server:

   ```bash
   cd app/client/
   npm run dev
   ```

   The frontend starts on `http://localhost:5173`. Open this URL in your browser to access the Metadata Capture application.


:::note Well done!

Your development environment is now set up. Next, [set up local authentication](set-up-local-authentication.md) for the app to function fully.

:::
