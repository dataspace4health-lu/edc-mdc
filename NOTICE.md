# Notice for DCA Metadata Capture

    This product was developed by Luxembourg National Data Service (LNDS).

    Copyright (c) 2023 Luxembourg National Data Service (LNDS)

    This product includes no external software components or libraries.

    This product is licensed under the Apache License, Version 2.0 (the "License").
    You may not use this product except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

## Dataspace4Health modifications

This repository is based on the LNDS DCA Metadata Capture project:

https://gitlab.com/lnds-lu/service-library/dca-metadata-capture

The identified Dataspace4Health-specific changes include:

- Added `VITE_BASE_URL=/mdc` in `.env.production`.
- Replaced HTML `<a>` navigation with React `<Link>` navigation in:
  - `ctie_only_access/index.tsx`
  - `first_time_login/index.tsx`
  - `unauthorized/index.tsx`
  - `DataDictionaryTable.tsx`
  - `Breadcrumb.tsx`
  - `LeftSidebarWithLinks.tsx`

These changes address frontend routing when the application is served under
the `/mdc` base path.
