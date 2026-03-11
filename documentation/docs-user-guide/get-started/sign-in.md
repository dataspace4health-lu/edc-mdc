---
slug: /sign-in
sidebar_label: Sign in
sidebar_position: 1
description: "Access Metadata Capture using your organisation credentials."
---

import FeatureFlag from '@site/src/components/FeatureFlag';
import useBaseUrl from '@docusaurus/useBaseUrl';


# Sign in

Access Metadata Capture using your organisation credentials—you don't need to create a separate account. Your organisation's **Identity and Access Management (IAM)** system determines your access and permissions within Metadata Capture.

<FeatureFlag flag="enable_multi_tenants">

<!-- DGA -->
To sign in to Metadata Capture:
 
1. Obtain the link to Metadata Capture from your [Inventory Coordinator](/user-guide/roles-and-permissions) or [System Administrator](/user-guide/roles-and-permissions).

3. Open Metadata Capture in your web browser.

3. Select your sign-in method and sign in with your organisation credentials.

   <img src={useBaseUrl('/get-started/sign-in.png')} alt="A screenshot of the sign-in page with options to connect using LuxTrust, LNDS, or Email" width="650" />

4. After you sign in, the Metadata Capture home page loads and you can [explore the dashboard](/user-guide/dashboard-overview).

:::info Unauthorised Access?

If you're signing in for the first time, you may get an "**Unauthorized Access**" error that is often related to roles and permissions. Contact your [Inventory Coordinator](/user-guide/roles-and-permissions) or [System Administrator](/user-guide/roles-and-permissions) and make sure you have the appropriate roles assigned.

:::

</FeatureFlag>

