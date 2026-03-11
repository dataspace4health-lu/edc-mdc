---
slug: /
sidebar_label: "Developer Guide"
sidebar_position: 1
---

import Link from '@docusaurus/Link';
import styles from '@site/src/pages/index.module.css';

# Welcome to the Developer Guide

Welcome to the Metadata Capture Developer Guide!

Build integrations and extend the functionality of the Metadata Capture platform to meet your organisation's needs. The platform is built with modern technologies including **FastAPI** and **SQLAlchemy** for the backend, **React with TypeScript** for the frontend, and **PostgreSQL** for data storage, providing a robust foundation for development and customization.

This guide covers development environment setup, local testing, and contribution workflows.

## Get started

<div className={styles.grid}>
  <Link to="set-up-a-developer-env" className={styles.card}>
    <h3>💻 Environment setup</h3>
    <p>Get your development environment ready with all necessary tools and dependencies</p>
  </Link>
  <Link to="set-up-local-authentication" className={styles.card}>
    <h3>🔐 Local authentication</h3>
    <p>Configure authentication setup for local development and testing</p>
  </Link>
  <Link to="work-with-the-database" className={styles.card}>
    <h3>🗃️ Database operations</h3>
    <p>Working with the database during development</p>
  </Link>
  <Link to="run-tests" className={styles.card}>
    <h3>🧪 Running tests</h3>
    <p>How to run and create tests for the platform</p>
  </Link>
</div>

