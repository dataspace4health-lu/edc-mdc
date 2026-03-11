---
slug: /
sidebar_label: "System Admin Guide"
sidebar_position: 1
---

import Link from '@docusaurus/Link';
import styles from '@site/src/pages/index.module.css';

# Welcome to the System Admin Guide

Welcome to the Metadata Capture System Admin Guide!

Deploy, configure, and maintain the Metadata Capture application in your organisation. This guide provides comprehensive instructions for setting up your own instance of Metadata Capture, giving you full control over deployment, configuration, and data management.

This guide covers everything you need to deploy and manage the application in your environment.

## Get started

<div className={styles.grid}>
  <Link to="architecture-overview" className={styles.card}>
    <h3>🏗️ Architecture overview</h3>
    <p>Understand the application structure and components</p>
  </Link>
  <Link to="deploy-metadata-capture" className={styles.card}>
    <h3>🚀 Deployment</h3>
    <p>How to deploy the Metadata Capture application</p>
  </Link>
  <Link to="configure-the-application" className={styles.card}>
    <h3>⚙️ Configuration</h3>
    <p>Set up authentication, email notifications, and other system settings</p>
  </Link>
  <Link to="configure-roles-and-permissions" className={styles.card}>
    <h3>👥 Roles and Permissions</h3>
    <p>Set up user access and permissions within and across organisations</p>
  </Link>
</div>
