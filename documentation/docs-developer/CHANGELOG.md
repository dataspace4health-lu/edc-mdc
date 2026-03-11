# Changelog

This page documents all notable changes to the Metadata Capture application.

Use this changelog to track new features, improvements, and bug fixes across different versions of the application. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [v4.0.54] - 2026-02-19

### Added
- feat: Implement auto-selection of health themes based on dataset themes by @Kacem Bechka in 9e78ed5650e

### Changed
- docs: Update CHANGELOG for v4.0.53 by @ci-push-tag in 9ee723b3100

### Fixed
- fix: resolve Windows-specific URL duplication issue in distribution forms by @Inderpal Singh in f22d2a2ac95


## [v4.0.53] - 2026-02-19

### Added
- feat: add personal_data field to dataset by @Ahmad Habib in 578c354a2b3
- feat: make conforms_to a list instead of set by @Inderpal Singh in 91a21ca3052
- feat: We dont show submit btn on preview form anymore by @Inderpal Singh in 6139ef44325
- feat: add coding system field to dataset by @Ahmad Habib in 3d3e93e26e8
- feat: add health legal basis to dataset by @Emiliana Pali in 780e640ab61
- feat: add multi-value dataset purpose support by @[name] in f124eb6be09

### Changed
- refactor: change codingSystem to hasCodingSystem in RDF by @Ahmad Habib in 8c0864445a7
- chore(deps): update dependency boto3 to v1.42.52 by @Renovate Bot in 56089f328d4
- add dataset relation to versioning changes by @Emiliana Pali in 11e58ec96f0
- Fix encoding of health Theme for health dcat compliance by @Alessandro in 16f3a7709fc
- refactor: update dataset landing pages and documentation handling to use lists instead of sets by @Kacem Bechka in 07c99f7e299
- Fix byte size negative values by @Alessandro in caea9999e16
- Update health category encoding to RDF by @AM in b084fa3ff4a
- chore(deps): update dependency boto3 to v1.42.50 by @Renovate Bot in 34b2f5c3b64
- ART-21415-bulk-upload-dataset by @Patel Suchitha in 8efd0d00e8e
- Docs/art 21415/add a data dictionary by @Patel Suchitha in d9c94b2166c
- Merge branch 'docs/ART-21415/changing-example' into 'main' by @Inderpal Singh in 95742e43979
- chore(deps): update dependency redis to v7.2.0 by @Renovate Bot in ccd0bf36a50
- Docs/art 21415/approve dataset by @Patel Suchitha in 9002a96455c
- Docs/art 21415/url warning rephrasing by @Patel Suchitha in fdcabff23f6
- Merge branch 'ART-22558/replace-legal-basis-with-applicable-legislation' into 'main' by @Emiliana Pali in 7d993bd3fea

### Fixed
- fix: unit tests by @Inderpal Singh in e7ba6dc6bbc
- Bugfix: add qualified attributions version changes by @Rania Hamdani in 5b501325655
- fix: preserving order for url fields in distribution by @Emiliana Pali in 19d1d854ca1
- fix: make all the list items in UI appear consistently by @Inderpal Singh in 1440556c501
- fix: issues in single value fields by @Rania Hamdani in 4587a7a82d0
- fix: Resolve dataset diff rendering issue by @Ahmad Habib in fe931ec3255
- fix(rdf-import): normalize documentation values and extend multi-value import coverage by @Inderpal Singh in f8508a265d8
- fix: Distributions import was broken in import by @Inderpal Singh in 0dd34af00b6
- fix(ActivityLogList): enhance layout and styling for better responsiveness and readability by @[name] in a486a187ca5
- fix: no need to show banner (metadata only / underlying change) on deprecated datasets by @Inderpal Singh in 83aadceabd8
- fix(bulk-upload): make distribution title optional and stabilize reverse distribution ordering by @Inderpal Singh in 83b4d968998
- fix: no need to show dist tab in preview because distributions are moved out of dataset form by @Inderpal Singh in 87de4bbb808
- fix: preserve spatial resolution order as they are entered in the system by @Inderpal Singh in cc4d1b0c4ea
- fix(distributions): auto-fill default access URL only on rights transition to non-public by @Inderpal Singh in 01e1503aede
- fix(distributions): prevent access URL re-insertion and duplication issues by @Inderpal Singh in cb761bf15e0
- fix(tests): clean provenance/version-note tables to prevent cross-test diff flakiness by @Inderpal Singh in b36edd0143f
- fix: add dynamic browser titles by @Rania Hamdani in 51ba98f3b2f
- fix: distribution doc validation in schema by @Rania Hamdani in 8a637c272e8


## [v4.0.52] - 2026-02-16

### Added
- feat: make distribution documentation multi value by @Rania Hamdani in c21bf8d1a4
- feat: show indicator that modifcation date must be changed by @Inderpal Singh in e486654eef
- feat: implement validation for duplicate values in dataset and distribution forms by @Kacem Bechka in 0cb20d2261
- feat: #22882 make download url in distribution multi value by @Kacem Bechka in d416dd4d8c

### Changed
- chore(deps): update dependency authlib to v1.6.8 by @Renovate Bot in 83d347e825
- chore(deps): update dependency boto3 to v1.42.49 by @Renovate Bot in a0b9dd9dd4
- chore(deps): update docker.io/postgres docker tag to v18.2 by @Renovate Bot in 635472e262
- chore(deps): update dependency rdflib to v7.6.0 by @Renovate Bot in 7a17f6c6df
- refactor(audit): retain activity logs on entity/user deletion and make actor resolution null-safe by @Inderpal Singh in 7750263005
- chore(deps): update dependency boto3 to v1.42.48 by @Renovate Bot in b7cb6f8df5
- chore(deps): update dependency brace-expansion to v5 by @Renovate Bot in 4698332862
- docs: Update CHANGELOG for v4.0.51 by @ci-push-tag in 7dc7a204f9

### Fixed
- fix(ui): always scroll to top on distribution submit errors by @Inderpal Singh in c58710d96d
- fix:  do not show tooltip body if text is empty by @Inderpal Singh in 4f0d5024ca
- fix: validations errors were not shown in creatable dropdown by @Inderpal Singh in 1d4897a8b4
- fix: do not allow duplication distributions with same title by @Inderpal Singh in 382e743918
- fix: tooltip and also if handle case when dataset is missing by @Inderpal Singh in 23ca409150


## [v4.0.51] - 2026-02-12

### Added
- feat: display all modified dataset, distribution and data dictionary fields during dataset versioning by @Ahmad Habib in ecbc86168c
- feat: #22880 make access url in distribution multi value by @Emiliana Pali in c5dc7e1aba
- feat: rewording and disable create a version btn if already exist by @Inderpal Singh in 343e4e12b7
- feat(versioning): add validation for version and version notes when new dataset version is created by @Inderpal Singh in 1c7e91c540
- feat:  Add explicit version change type to dataset versioning flow by @Inderpal Singh in 614a5679cd
- feat(distributions): make internalOnly field always visible (remove feature-flag hide) by @Inderpal Singh in a067d41bf2
- feat: Check dataset validation (including 1 distribution required) when moved from DRAFT -> COMPLETED by @Inderpal Singh in 822c472426

### Changed
- chore(deps): update dependency boto3 to v1.42.47 by @Renovate Bot in 6df1871044
- refactor: remove description if external relation role is referenced by by @Emiliana in e067d73981
- chore: alembic, cryptography: Add curations for versions 1.18.4 and 46.0.5 by @Inderpal Singh in 5d60d9e7fb
- chore(deps): update dependency boto3 to v1.42.46 by @Renovate Bot in 6875f5fb7c
- chore(deps): update dependency alembic to v1.18.4 by @Renovate Bot in da4259f192
- Art 22579/add is referenced by external resources by @Emiliana Pali in 283b9ba7b4
- Merge branch 'ART-22580/make-provenance-version-notes-multi-value' into 'main' by @Emiliana Pali in abc451a570

### Fixed
- fix: wording by @Inderpal Singh in ecd59c1980
- fix(distributions): prefill access URL when rights are non-public by @Inderpal Singh in 3554d80eeb
- fix(ui): align hasCodeValues icon and text, change has coded to has code by @Ahmad Habib in 498db26b81
- fix(activity-log): include dataset language changes in diff output by @Inderpal Singh in 648af6e8a2
- fix: restore submit button visibility when distributions are empty by @Inderpal Singh in c9b9669a2a
- fix(bug): remove APP_URL dependency from catalogue homepage RDF by @Inderpal Singh in 8d2b01d9e8
- fix(catalogues): emit IANA media type URIs as http in RDF output by @Inderpal Singh in 3824c95fef


## [v4.0.50] - 2026-02-02

### Changed
- chore: PyPI::wcwidth:0.5.3 and PyPI::pyjwt:2.11.0 by @Inderpal Singh in f6cabc094d5
- chore(deps): update dependency jsdom to v28 by @Renovate Bot in 2681f555d6e
- chore(deps): update dependency pyjwt to v2.11.0 by @Renovate Bot in 2a7b3d5d73f
- chore(deps): update dependency boto3 to v1.42.39 by @Renovate Bot in aac5cc5dc51
- chore(deps): update mcr.microsoft.com/playwright docker tag to v1.58.1 by @Renovate Bot in 3e66a454a4d
- chore: Add license information for PyPI::alembic:1.18.3 and PyPI::wcwidth:0.5.2 by @Inderpal Singh in a4af810dd84
- chore(deps): update dependency protobuf to v6.33.5 by @LNDS Renovate service account in 77678e8de98
- docs: Update CHANGELOG for v4.0.49 by @ci-push-tag in b6720601aca
- chore(deps): update dependency boto3 to v1.42.38 by @Renovate Bot in 9e6ffad2ec4
- chore(deps): update dependency alembic to v1.18.3 by @Renovate Bot in c560a7b3843

### Fixed
- fix: Handle null is_analytics field in distribution DTO conversion by @Inderpal Singh in 06716880b4f
- fix: prevent crash in OrganisationList and phantom contact updates by @Inderpal Singh in 42181848fa5
- fix: enable STARTTLS on all SMTP ports to support production mail server by @Inderpal Singh in d536e32ae99


## [v4.0.49] - 2026-01-29

### Added
- feat: #ART-22581 make start date optional by @Emiliana Pali in a4c341b0bc7
- feat: Make distribution description optional by @Inderpal Singh in af82f9dc12c
- feat: byte size is required if rights are non-public by @Inderpal Singh in 0e1dae071c1
- feat: File format becomes required field when rights are non-public by @Inderpal Singh in 5140f4e8d8b
- feat: Make landing page a multi-value field by @Inderpal Singh in 0c009568c86

### Changed
- Art 22441/enable multi value for documentation by @Rania Hamdani in 1131fef26d3
- Improve service account authentication error logging by @Inderpal Singh in 5ccc65f7ead
- Art 22433/make keywords & frequencies recommended by @Emiliana Pali in 06e7c5f69c0
- Art 22435: add multi valued and non negative validation for spatial resolution by @Rania Hamdani in accf30ed2f9
- chore(deps): update dependency boto3 to v1.42.36 by @Renovate Bot in ca9fce2808d
- chore(deps): update docker docker tag to v29.2.0 by @Renovate Bot in 0296742cc73
- Art 22439/enable multi value for conforms to by @Emiliana Pali in 27ea5c826a8
- chore: Add license information for PyPI::wcwidth:0.5.0 by @Inderpal Singh in c523619385a
- chore: Add license information for PyPI::greenlet:3.3.1 and PyPI::wcwidth:0.4.0 by @Inderpal Singh in 7773db16781
- chore(deps): update dependency boto3 to v1.42.35 by @Renovate Bot in 585fd8e6049
- Merge branch 'renovate/mcr.microsoft.com-playwright-1.x' into 'main' by @Inderpal Singh in 3cc796b2c24

### Fixed
- fix: #22433 remove keyword from dataset card also from bulk upload req... by @Emiliana Pali in e809a080214
- fix: handle single number for spatialResolutions and reorder rights field by @Inderpal Singh in 2a1e1a20dcb
- chore: temp disable ORT because the lib fix is not yet available and is blocking pipeline by @Inderpal Singh in 9af547e0493
- fix: Change spatial_resolutions from FrozenSet to List to fix TypeError by @Inderpal Singh in 634019cd3f5
- fix: pin protobuf to 6.33.3 to avoid vulnerability in 6.33.4 & Add license information for PyPI::cryptography:46.0.4 by @Inderpal Singh in 8f0fc1d2b07


## [v4.0.48] - 2026-01-21

### Changed
- docs: Update CHANGELOG for v4.0.47 by @ci-push-tag in d0648abb40c

### Fixed
- fix: anyone should be able to create a version of dataset by @Inderpal Singh in e3f3f2ae0b4


## [v4.0.47] - 2026-01-20

### Added
- feat: Add ISO 8601 validation for temporal resolution fields by @Inderpal Singh in 88129f5d6c
- feat: Remove confusing "present" by @Inderpal Singh in bc25ac5939
- feat: enforce data type validation for bulk upload data dictionary by @Inderpal Singh in d26e9e672c
- feat: Generate unique keys for legal basis using link hash by @Inderpal Singh in 09e1936e6b
- feat: Improve legal basis data quality in bulk import by @Inderpal Singh in cca6f74f16

### Changed
- chore: Add license information for PyPI::black:26.1.0 by @Inderpal Singh in 06a90e973b
- chore(deps): update dependency black to v26 by @LNDS Renovate service account in d15981b909
- chore(deps): update docker docker tag to v29.1.5 by @Renovate Bot in a80cdcac25
- chore(deps): update dependency boto3 to v1.42.30 by @Renovate Bot in 49cc63d3bf
- docs: Update CHANGELOG for v4.0.46 by @ci-push-tag in 6ec96d8cd4

### Fixed
- fix: prevent email addresses from appearing in generated changelog by @Inderpal Singh in d330e8a4e9
- fix: make data dictionary table header sticky by @Inderpal Singh in f26b7d809d
- fix: close user menu dropdown when clicking outside by @Inderpal Singh in 3ad696007c
- fix(deps): update dependency zod to v4 by @LNDS Renovate service account in e60d0da68c


## [v4.0.46] - 2026-01-15

### Added
- feat: #22278 add population coverage to dataset by @Emiliana Pali in 7320c9eba1
- feat: Add detailed logs while doing bulk import for better debugging by @Inderpal Singh in 03425bf51b
- feat: Add URL validation for legal basis link field by @Inderpal Singh in 8be34d4d7d
- feat: Add scheduled job to push catalogue.rdf to front office by @Inderpal Singh in 9dcf9e40fd
- feat: Add minTypicalAge and maxTypicalAge to RDF export and import by @Inderpal Singh in 874ae0e46d
- feat: end to end test for importing dataset flow by @Rania Hamdani in 93e5030ae4

### Changed
- chore: Add license information for PyPI::alembic:1.18.1 by @Inderpal Singh in 94398a286b
- chore(deps): update node.js to v22.22.0 by @Renovate Bot in a446235b36
- chore(deps): update dependency boto3 to v1.42.28 by @Renovate Bot in 8b588e151e
- chore(deps): update dependency alembic to v1.18.1 by @Renovate Bot in 9b9a263b68
- add nr of records and unique individuals for health datasets by @Emiliana Pali in 804d9826dc
- chore(deps): update dependency boto3 to v1.42.27 by @Renovate Bot in 67a6a32f07
- Add hdab in dataset by @Emiliana Pali in a6224e5a4b
- chore(deps): update dependency boto3 to v1.42.26 by @Renovate Bot in 9f4ed4f2d8
- chore(deps): update dependency alembic to v1.18.0 by @Renovate Bot in 1565d6d002
- docs: Update CHANGELOG for v4.0.45 by @ci-push-tag in ee945b9d48

### Fixed
- fix: Trigger front office push when dataset status is updated from source by @Inderpal Singh in d55b3e97c4
- fix: correct organisation filtering for legal bases and keywords by @Inderpal Singh in 48b0451660
- fix: Use service account user for dataset imports by @Inderpal Singh in 919e751e0e
- fix: Add license information for PyPI::alembic:1.18.0 by @Inderpal Singh in 98bcf6ff40


## [v4.0.45] - 2026-01-12

### Added
- feat: add health theme and category to the rdf by @Emiliana Pali in ed3f7b91ff
- feat: Frontend for HealthDCAT Max Typical Age and Min Typical Age by @Inderpal Singh in 61717277d9
- feat: Add HealthDCAT max typical age and min typical age (backend) + tests refactoring by @Inderpal Singh in 818f479fd3
- feat: migration to insert values for health category and theme by @Emiliana in 93b7d5cb4e
- feat: Remove flag, as the logic to enable health dcat has been moved at dataset level in the UI form by @Inderpal Singh in 31433a453f
- feat: add user-driven HealthDCAT-AP profile selector by @Inderpal Singh in d90659f22e

### Changed
- chore(deps): update docker docker tag to v29.1.4 by @Renovate Bot in 343cbf0838
- chore(deps): update dependency boto3 to v1.42.25 by @Renovate Bot in baec545416
- chore(deps): update dependency certifi to v2026 by @Renovate Bot in e0fdee796f
- chore(deps): update dependency pre-commit to v4.5.1 by @Renovate Bot in 574b7c370f
- Fix dataset import ordering issue by @Inderpal Singh in 7846ebb265
- Move cron schedule to environment variable by @Inderpal Singh in 3461836d77
- Fix RDF import endpoint dependency injection issue by @Inderpal Singh in ef9ced5622
- chore(deps): update dependency jsonschema to v4.26.0 by @Renovate Bot in 389a02683a
- chore(deps): update dependency asyncssh to v2.22.0 by @Renovate Bot in 9518e3e7b4
- chore(deps): update dependency celery to v5.6.2 by @Renovate Bot in 4e48da7aca
- chore(deps): update dependency boto3 to v1.42.24 by @Renovate Bot in f971198a99
- chore(deps): update dependency authlib to v1.6.6 by @Renovate Bot in da92caf982
- chore(deps): update dependency anyio to v4.12.1 by @Renovate Bot in 87fb5fa89f
- chore(deps): update dependency opentelemetry-proto to v1.39.1 by @LNDS Renovate service account in 7a37c0ecd3
- Docs/art 22166/how to add users to orgs by @Rose Pasigna in 1eb27059ee
- docs: Update CHANGELOG for v4.0.44 by @ci-push-tag in f37f495d5d

### Fixed
- fix: add curations for updated libraries by @Inderpal Singh in a5ab2a7413
- fix: The package 'PyPI::urllib3:2.6.1' has a vulnerability. by @Inderpal Singh in d981647977
- fix: properly reset health fields when toggling dataset type using React key prop by @Inderpal Singh in 83861f6669
- fix: Move external dataset import logging to occur before child entity additions by @Inderpal Singh in 19048b0140


## [v4.0.44] - 2026-01-06

### Added
- feat: #21801 add health category and theme by @Emiliana Pali in fdff475b9c5
- feat: add logs for importing datasets form fields by @Emiliana Pali in acb16928fc1
- feat: Add bot-mdc-service-client with BOT_USER role by @Inderpal Singh in 4ef4539cc20

### Changed
- Docs/art 22113/address dga feedback by @Rose Pasigna in 4c238ec97e7
- Add read:published permission to HDAB bot by @Alessandro in 01dc71af3c0
- Restrict published dataset visibility to organization scope by @Inderpal Singh in 51014f63684
- docs ART-22028 Refine dataset enhancements and vocab by @Rose Pasigna in 3f98012511b
- docs/ART-22006 Enhance bulk upload how-to by @Rose Pasigna in 0cb76b1cba8
- docs: ART-21976 Categorise core dataset milestones for better user journey by @Rose Pasigna in b8301a11dee
- Add health dcat flag by @Emiliana Pali in 4d7ab94c310
- docs: ART-21422 Approval workflow without Accord de Principe by @Rose Pasigna in 63b770a14f1
- docs: ART-21959 Apply docusaurus v4 linking by @Rose Pasigna in f06148c5f64
- Docs/art 21948/versioning and duplicating datasets by @Rose Pasigna in 3cf6f315c47
- docs: ART-21941 Activity logs and dataset comments by @Rose Pasigna in 9d6841868d8
- docs: ART-21891 Documentation tracker by @Rose Pasigna in 79d2e35aa67
- docs: Update CHANGELOG for v4.0.43 by @ci-push-tag in 90b0f5331a3
- Fix: Don't copy released_at when creating new dataset version by @Inderpal Singh in fd6d0b94208

### Fixed
- fix: Re-enable keyword test by @Inderpal Singh in 01088b473a2
- fix: include released_at in Dataset.to_dict_for_diff() to prevent false activity log entries by @Inderpal Singh in ff34f01882b
- fix: license information for importlib-metadata 8.7.1 and pyparsing 3.3.1 by @Inderpal Singh in ad095f7e675
- Merge branch 'fix/service-account-ssl-verification' into 'main' by @Inderpal Singh in 987e00c256e


## [v4.0.43] - 2025-12-11

### Added
- feat: add service account authentication for released datasets API by @Inderpal Singh in f55255085d6
- Docs: ART-19983 update concepts, diagrams, and use cases for each feature by @Rose Pasigna in 4059abc5d44

### Changed
- Fix license information for urllib3 2.6.1 by @Inderpal Singh in 18af646e658
- chore(deps): update dependency boto3 to v1.42.7 by @Renovate Bot in 7914d09e9ba
- chore(deps): update dependency urllib3 to v2.6.1 by @Renovate Bot in 95288ef08d7
- chore(deps): update dependency sqlalchemy to v2.0.45 by @Renovate Bot in 97978112e19
- Fix license information for black 25.12.0 and pytest 9.0.2 by @Inderpal Singh in 4931548bbc9
- chore(deps): update sonarsource/sonar-scanner-cli docker tag to v12 by @Renovate Bot in ba3a38353ee
- chore(deps): update dependency black to v25.12.0 by @Renovate Bot in 5bc09aca20d
- chore(deps): update dependency pytest to v9.0.2 by @Renovate Bot in 06cefa3321d
- chore(deps): update docker docker tag to v29.1.2 by @Renovate Bot in 8c222d7fff8
- chore(deps): update dependency urllib3 to v2.6.0 by @Renovate Bot in a0f15494e63
- chore(deps): update dependency boto3 to v1.42.4 by @Renovate Bot in 8f73ec113dd
- chore(deps): update dependency boto3 to v1.42.3 by @Renovate Bot in 8bad5c9722e
- docs: ART-21095 Add distributions by @Rose Pasigna in d93aff1d5e8
- chore(deps): update redis docker tag to v8 by @Renovate Bot in 4e4c172445b
- end to end test for dataset versioning by @Rania Hamdani in 745dcb4d9e8
- chore(deps): update dependency boto3 to v1.42.2 by @Renovate Bot in 73785da261a
- chore(deps): update dependency celery to v5.6.0 by @Renovate Bot in 74408114524
- chore(deps): update dependency anyio to v4.12.0 by @Renovate Bot in d425bbac7a5
- chore(deps): update dependency black to v25 by @LNDS Renovate service account in 1551769eea0
- docs: Update CHANGELOG for v4.0.42 by @ci-push-tag in cba30595786
- chore(deps): update dependency opentelemetry-exporter-otlp-proto-common to v1.38.0 by @LNDS Renovate service account in 18633d89591
- chore(deps): update dependency rdflib to v7.5.0 by @Renovate Bot in 1441324eda3

### Fixed
- fix: resolve foreign key violation when deleting distribution with legal basis by @Inderpal Singh in 3e4cf71013e
- chore: fix urllib curation by @Alessandro in 5cbc478b359
- fix(deps): update dependency tailwind-merge to v3 by @Renovate Bot in a47824f2523
- fix(deps): update dependency framer-motion to v12 by @Renovate Bot in 687137aa42b
- chore: fix curation for opentel, black, rpds, anyio by @Alessandro in caa23effc84
- chore: Restore black check and fix format by @AM in 0966195bb0f


## [v4.0.42] - 2025-12-03

### Changed
- docs: ART-20073 Add authentic source page by @Rose Pasigna in 7c4bacf94
- ci: push Docker images directly to library namespace by @Inderpal Singh in e65910e4e
- docs: keep only one changelog in dev (and link in footer) by @Rose Pasigna in 3229964fd
- docs: ART-20175 Add organisation and contact management guides by @Rose Pasigna in 73390a1d1
- chore(deps): update docker.io/postgres docker tag to v18 by @Renovate Bot in 1aa518419

### Fixed
- fix: CONTRIBUTOR (non multi tenancy setup) role cannot complete datasets by @Inderpal Singh in 47345f56b
- fix: update changelog script to only target existing file by @Inderpal Singh in ca667315c


## [v4.0.41] - 2025-11-28

### Added
- feat: use repository for data dictionary ordering in RDF builder by @Inderpal Singh in 3741fa7b
- feat: preserve released_at timestamp during cross-instance dataset import by @Inderpal Singh in de017027

### Changed
- refactor: #20597 reuse insert form for dd entries by @Emiliana Pali in 7a351b77
- chore(deps): update dependency vite to v7 by @Renovate Bot in 0f581955
- chore(deps): update dependency pydantic to v2.12.5 by @Renovate Bot in b57e205a
- chore(deps): update dependency boto3 to v1.41.5 by @Renovate Bot in 1aa0777e
- Fix flaky test: assign unique versions to mock datasets by @Inderpal Singh in dbb46308
- chore(deps): update docker docker tag to v29 by @Renovate Bot in 50f05bd3
- chore: add two script to run and stop mdc by @Alessandro in e6b69402
- docs: ART-20754 Refine outdated language, site layout, and page structures by @Rose Pasigna in 24d6aeeb
- chore(deps): update dependency vitest to v4 by @Renovate Bot in 9d471e79
- chore(deps): update mcr.microsoft.com/playwright docker tag to v1.57.0 by @Renovate Bot in 146825f6
- chore(deps): update dependency boto3 to v1.41.4 by @Renovate Bot in 702b8a50
- chore(deps): update dependency pytest to v9 by @Renovate Bot in 9a9b61a1
- chore(deps): update dependency fastapi to v0.122.0 by @Renovate Bot in 11aa59ce
- docs: Update CHANGELOG for v4.0.40 by @ci-push-tag in 4b0b7d51
- chore(deps): update dependency pytest-cov to v7 by @Renovate Bot in e64bc886
- chore(deps): update dependency pytest-asyncio to v1 by @Renovate Bot in 5bfc1d0d

### Fixed
- fix: fix curation for pydantic by @Alessandro in 6c749307
- fix-pytest-license-curations by @Inderpal Singh in bbe90bc1
- fix: add enable dual instance to FeatureOptions by @Rania Hamdani in 18da831e
- fix: add system:admin permission to bypass validation for RDF imports by @Inderpal Singh in 7a8aeabe


## [v4.0.40] - 2025-11-25

### Added
- feat: enqueue FTPS push after import by @Rania Hamdani in e40f4ec2ffd
- feat: org access guardrails between ctie and lnds for role assignment, dataset creation and bulk import by @Rania Hamdani in 29cbd806669
- feat: Replace toggle buttons with dropdowns for boolean fields in data dictionary by @Inderpal Singh in 26fe47aa252
- feat: Add e2e for data dictionary reordering by @Inderpal Singh in d2ee8ac579b

### Changed
- test: Add boolean dropdown selections to E2E data dictionary test by @Inderpal Singh in 17a69a8e6a3
- Art 20597/edit data dictionary entries by @Emiliana Pali in cd471f26575
- chore(deps): update dependency packaging to v25 by @Renovate Bot in 152a999e8d9
- chore(deps): update dependency minimatch to v10 by @Renovate Bot in 95023f5c8dc
- chore(deps): update dependency jsdom to v27 by @Renovate Bot in 82660a80712
- chore(deps): update dependency certifi to v2025 by @Renovate Bot in b9a42f1fd29

### Fixed
- fix: Replace toggle buttons with dropdowns for nullable boolean fields by @Inderpal Singh in ba0ebb031b1
- fix: extend license curation for packaging to cover version 25.0 by @Inderpal Singh in 1c830b33086
- fix: Remove redundant git add/commit in changelog CI job by @Inderpal Singh in 81d9faacde9



## [v4.0.39] - 2025-11-24

### Added
- feat: Add activity logs for dictionary reordering by @Inderpal Singh in e6907af6
- feat: UI to reorder data dictionaries using up/down arrows by @Inderpal Singh in 761b32d1
- feat: Reorder data dictionary entries (backend) by @Inderpal Singh in 99b888d2
- feat: Use JWT sub claim for service account users by @Inderpal Singh in 9fd633ab

### Changed
- Art 20567/update dataset type vocabulary by @Emiliana Pali in bd9e7a9c
- chore(deps): update docker.io/postgres docker tag to v17.7 by @Renovate Bot in 31b8d2ae
- chore(deps): update dependency redis to v7.1.0 by @Renovate Bot in ce827978
- chore(deps): update dependency pre-commit to v4.5.0 by @Renovate Bot in 8704a4ce
- chore(deps): update dependency fastapi to v0.121.3 by @Renovate Bot in 3e8851d1
- chore(deps): update dependency boto3 to v1.41.2 by @Renovate Bot in b2171a10
- chore(deps): update dependency click to v8.3.1 by @Renovate Bot in b23f25ac
- chore(deps): update dependency alembic to v1.17.2 by @Renovate Bot in 30265ece
- chore(deps): update dependency @types/react to v18.3.27 by @Renovate Bot in 18ea703f

### Fixed
- fix: currently changelog markdown is kept at 3 places. So this script updates all of them by @Inderpal Singh in cb2a0709
- fix: add license curation for alembic 1.17.2 by @Inderpal Singh in 44de9250


## [v4.0.38] - 2025-11-21

### Added
- feat: Add landing page and documentation fields to bulk upload by @Inderpal Singh in c3c9713b
- feat: add default access URL for NON_PUBLIC distributions by @Inderpal Singh in 62480069
- feat: Access URL is mandatory by @Inderpal Singh in 8711d6c9
- feat: clean up accord de principe by @Emiliana Pali in 43e58752

### Changed
- refactor: Modularize authentication code into dedicated auth modules (also add service account support) by @Inderpal Singh in 03426ac3
- chore(deps): update python docker tag to v3.14 by @Renovate Bot in a115bf6d
- chore(deps): update dependency brace-expansion to v4 by @Renovate Bot in fad3189d
- chore(deps): update dependency @vitejs/plugin-react to v5 by @Renovate Bot in c7e582f9
- chore(deps): update dependency pydantic to v2.12.4 by @Renovate Bot in 1ed79e7c
- RDF Import:  Enqueue FTPS Push After Import by @Rania Hamdani in d47d3f0c
- chore: restore ort scan by @AM in e82d75a7
- chore: disable ort temporaly by @Emiliana in 2ab34483
- Update approval flow by @Emiliana Pali in 4fc6fe63

### Fixed
- fix: Handle empty strings in parseNumber to prevent 0 from being set for null values by @Inderpal Singh in fd8bf00a
- fix: Add comment step before approving by @Emiliana Pali in cdff7a94
- fix: Only show btn if user has the permission by @Inderpal Singh in 4970e0f1
- fix: Add license curations for PyPI packages by @Inderpal Singh in a2450de7
- chore: fix ort scan by @Alessandro in cd80b597
- Typo fixed by @Emiliana Pali in 5565a0de
- fix: temp remove call by @Inderpal Singh in 4dc7145c


## [v4.0.37] - 2025-11-13

### Added
- feat: Data dictionaries are also imported via RDF by @Inderpal Singh in 1f6a7d6d
- feat: Add contact import service for dataset synchronization by @Inderpal Singh in 45593120
- feat: UI enhancements on imported datasets (direct link to source and restrict changes) by @Inderpal Singh in fdb9f278
- feat: Import datasets should have same status as on source system by @Inderpal Singh in e73216c8
- feat: Ensure RDF imports pre-create keywors and legislations data by @Inderpal Singh in f989d9d4
- feat: Restrict imported datasets status to be changed from backend (instead of frontend) by @Inderpal Singh in 1c228307
- feat: Allow it to take markdown links by @Inderpal Singh in 1e051759

### Changed
- chore(deps): update dependency boto3 to v1.40.72 by @Renovate Bot in 50338cb7
- chore(deps): update sonarsource/sonar-scanner-cli docker tag to v11.5 by @Renovate Bot in 82571bcc
- chore(deps): update node.js to v22.21.1 by @Renovate Bot in d0bbe388
- chore(deps): update mcr.microsoft.com/playwright docker tag to v1.56.1 by @Renovate Bot in 80d7db61
- chore(deps): update docker.io/postgres docker tag to v17.6 by @Renovate Bot in 92e60f99
- chore(deps): update docker docker tag to v27.5.1 by @Renovate Bot in 8c68dda1
- chore(deps): update dependency typing_extensions to v4.15.0 by @Renovate Bot in 5f531fae
- chore(deps): update dependency rdflib to v7.4.0 by @Renovate Bot in 72e015e4
- chore(deps): update dependency python-dotenv to v1.2.1 by @Renovate Bot in 5af82372
- chore(deps): update dependency fastapi to v0.121.1 by @Renovate Bot in b0576ba7
- chore(deps): update dependency boto3 to v1.40.70 by @Renovate Bot in 1b35cfee
- chore(deps): update dependency pyjwt to v2.10.1 by @Renovate Bot in 85581811
- chore(deps): update dependency pre-commit to v4.4.0 by @Renovate Bot in 91425b82
- chore: add pytest-asyncio 0.26.0 curation by @Inderpal Singh in 9907955b
- chore(deps): update dependency pytest-cov to v6.3.0 by @Renovate Bot in f463eb1b
- chore(deps): update dependency pytest-asyncio to v0.26.0 by @Renovate Bot in 6892b4f2
- chore(deps): update dependency pytest to v8.4.2 by @Renovate Bot in ec507434

### Fixed
- fix: data dictionary allowed_values RDF serialization by @Inderpal Singh in 562d464d
- fix: Add license curations for typing-extensions and python-dotenv by @Inderpal Singh in 283cbe4b
- Add license curation for PyPI::annotated-doc:0.0.4 to fix NO_LICENSE_IN_DEPENDENCY by @Inderpal Singh in d1f53295
- fix: show publish to front office btn for imported datasets by @Inderpal Singh in 11adba57
- fix base url issue for CDSP by @Rose Pasigna in 1b57fd6f


## [v4.0.36] - 2025-11-11

### Added
- feat: Contacts are also imported from RDF by @Inderpal Singh in b55e5d59

### Changed
- chore(deps): update dependency boto3 to v1.40.67 by @Renovate Bot in de2f8554
- chore(deps): update dependency packaging to v24.2 by @Renovate Bot in 831fd860
- chore(deps): update dependency jsonschema to v4.25.1 by @Renovate Bot in 3f5cfcf6
- chore(deps): update dependency iniconfig to v2.3.0 by @Renovate Bot in 8a4fd88c
- chore(deps): update dependency email-validator to v2.3.0 by @LNDS Renovate service account in f3427795
- chore(deps): update dependency fastapi to v0.121.0 by @Renovate Bot in 33ccc334
- chore(deps): update dependency click to v8.3.0 by @Renovate Bot in 18886ca3
- chore(deps): update dependency psycopg2-binary to v2.9.11 by @Renovate Bot in 191a627c
- chore(deps): update dependency markupsafe to v3.0.3 by @Renovate Bot in 6fed7d40
- chore(deps): update dependency dnspython to v2.8.0 by @Renovate Bot in 844cd3a8

### Fixed
- fix: idna-license-curation by @Inderpal Singh in 9ee422ba
- fix: add license details for iniconfig, jsonschema by @Inderpal Singh in ba9cea80
- fix: Add declared_license_mapping for psycopg2-binary to fix UNMAPPED_DECLARED_LICENSE warning by @Inderpal Singh in 0168f533
- fix: ORT Update license curations for markupsafe and psycopg2-binary by @Inderpal Singh in 9ec9512c


## [v4.0.35] - 2025-11-06

### Added
- feat: Add version tag to custom log handler to improve Splunk filtering by @Inderpal Singh in 3f50be5e

### Changed
- chore(deps): update dependency boto3 to v1.40.66 by @Renovate Bot in e2d67b94


## [v4.0.34] - 2025-11-05

### Added
- feat: add Splunk-compatible file-based JSON logging with flexible formats by @Inderpal Singh in 11b8a1fe7
- feat: Add endpoint to list released datasets for cross-instance polling by @Inderpal Singh in 5f0317889
- feat: During bulk import datasets, try to find legilsations using eur-lex while importing by @Inderpal Singh in a31448571
- feat: Data dictionary RDF now exports every field directly by @Inderpal Singh in d988a4fc6
- feat: Import qualified attributions for a dataset from rdf by @Inderpal Singh in ab49a9ee1
- feat: Import distributions within dataset from RDF by @Inderpal Singh in 619f5a758
- feat: UI to import datasets from rdf by @Inderpal Singh in 69f9cf28e
- feat: Skeleton service (with basic fields) to import Datasets from RDF by @Inderpal Singh in c8852a0cb

### Changed
- chore(deps): update dependency anyio to v4.11.0 by @Renovate Bot in 9e0a499a5
- chore(deps): update dependency alembic to v1.17.1 by @Renovate Bot in fb406dc04
- chore(deps): update devdependencies by @Renovate Bot in 23e102369
- chore(deps): update dependency transitions to v0.9.3 by @LNDS Renovate service account in 22771ec02
- chore(deps): update dependency boto3 to v1.40.66 by @Renovate Bot in 3996fc8ea
- chore(deps): update dependency sqlalchemy to v2.0.44 by @Renovate Bot in 7a4511f95
- chore(deps): update dependency mako to v1.3.10 by @Renovate Bot in e0daba2d6
- chore(deps): update dependency asyncssh to v2.21.1 by @Renovate Bot in e5b45a16b
- Upgrade all docusaurus/* packages at 3.9.2 by @Rania Hamdani in e3bbc8d04
- docs: Update CHANGELOG for v4.0.33 by @ci-push-tag in 522ade70d
- docs: ART-19800 Update mark as internal workflow by @Rose Pasigna in 97ba60fa0

### Fixed
- fix: add-alembic-anyio-curations by @Inderpal Singh in 9a3749c93
- fix: upgarde babel/runtime, brace-expansion and esbuild by @Rania Hamdani in 6f2c2fbe3
- fix: Missing permission to delete datasets of your own org by @Inderpal Singh in 83361f3c3
- fix: EUR-Lex search failures with operator substrings and CELEX URLs by @Inderpal Singh in a86c1779e
- docs: ART-20071 Assign fixed slugs to all pages by @Rose Pasigna in b43fbb09c
- fix: own reuse job and remove leftover CC0 license by @Inderpal Singh in 923ceafcc


## [v4.0.33] - 2025-11-03

### Added
- feat: Integrate Eur-lex with UI by @Inderpal Singh in a95f3400
- feat: Eur-lex service to fetch legislations by @Inderpal Singh in f071faab
- feat: Also show email now on the page by @Inderpal Singh in 45da927f

### Changed
- docs: ART-20070 Deprecate workflow by @Rose Pasigna in a8f1b49b
- chore: Update Python dependencies - authlib 1.6.5, urllib3 2.5.0, boto3 1.40.60 by @Rania Hamdani in 8fd57618
- docs: Update CHANGELOG for v4.0.32 by @ci-push-tag in f7014715

### Fixed
- fix: Users in envs with no-multi-tenancy enabled should also be able to import datasets for any org by @Inderpal Singh in 0100a05f
- fix: User with permission to delete their org datasets by @Inderpal Singh in 590fd589
- fix: Update FastAPI to 0.120.1 to resolve Starlette DoS vulnerability by @Rania Hamdani in 820bd651
- fix: upgrade Frontend libraries + resolve ORT scan issues by @Rania Hamdani in 9837a711


## [v4.0.32] - 2025-10-28

### Added
- feat: Make license recommended by @Inderpal Singh in 79a222040
- feat: Flatten dataset version history and reuse full metadata rendering by @Inderpal Singh in c796d73e9
- feat: Send list of all keywords to front office by @Inderpal Singh in 97f7ea829

### Changed
- docs: Update CHANGELOG for v4.0.31 by @ci-push-tag in e3e335447

### Fixed
- fix: send label of keyword instead of key (eg: "Population Data" instead of "populaiton_data") in rdf by @Inderpal Singh in 5553404eb


## [v4.0.31] - 2025-10-27

### Added
- feat: Enhance RDF Serialization for Front Office rendering by @Inderpal Singh in a97d4f57
- feat: Simplify authentic source rdf by removing unnecessary semantic complexity by @Inderpal Singh in 828f7e15

### Changed
- docs: Update CHANGELOG for v4.0.30 by @ci-push-tag in 136f7c08
- docs: ART-19707 Add user guides for keywords and legislations by @Rose Pasigna in b8bf4fcf

### Fixed
- fix: legilux changed their endpoint URI by @Inderpal Singh in 0e368755


## [v4.0.30] - 2025-10-24

### Added
- feat: Also suggest to add dictionaries & relations if not done by @Inderpal Singh in 0edaf5497
- feat: Next Steps UI helper by @Inderpal Singh in b0589a04c

### Changed
- docs: ART-19706 add data relations guide by @Rose Pasigna in e374f9a6f
- docs: Update CHANGELOG for v4.0.29 by @ci-push-tag in 8560f963a
- Delete accord de principe permission + read permission for get comments and version chains by @Rania Hamdani in 9eb0c633a

### Fixed
- fix: Add rpds-py curation by @Inderpal Singh in f17d54dca


## [v4.0.29] - 2025-10-22

### Added
- feat: Introduce category field and boolean flag to indicate if user of certain org has access to CTIE network or not by @Inderpal Singh in e16ea076e
- feat: Show next steps by @Inderpal Singh in 1d091cc68
- feat: Special permission to move datasets to Internal Only by @Inderpal Singh in fdae45c02

### Changed
- refactor: RDF improvements by @Inderpal Singh in 4484b1618
- docs: ART-19705 add qualified attributions guide by @Rose Pasigna in 29916c79a
- docs: Update CHANGELOG for v4.0.28 by @ci-push-tag in 6913f6e2e
- chore: Move out activity logs for dataset by @Inderpal Singh in 60df71f60

### Fixed
- fix: generate unique URIs for dataset versions using fragments by @Inderpal Singh in b9ec208c1
- fix: add permission validation to update dataset status by @Rania Hamdani in 71a485afa
- fix: distributions are now nested inside datasets by @Inderpal Singh in cb0dbdc38
- fix: RDF Genertion by @Inderpal Singh in 9e144411d
- fix: data services uri in rdf was not generated based on config uri template by @Inderpal Singh in f163a8863
- fix: use get_user_organisation_assignment instead of get_user_organisation_assignments (typo) by @Inderpal Singh in 6f1f8954f
- fix: improper access control by @Rania Hamdani in b53ed7f67
- fix: logic to show keywords in dropdown based on selected organisaiton by @Inderpal Singh in 351da8248
- fix: Fix markdown by @Aleksandar KMETOV in 0afb1d633


## [v4.0.28] - 2025-10-20

### Added
- feat: Provide env var to override legilux endpoint by @Inderpal Singh in 4ae792c94
- feat: #19676 back to draft for AEV by @Emiliana Pali in d3421c038
- feat: Add Logos and redesigned Footer by @Inderpal Singh in 9b227f0d5
- feat: creator membership validation by @Inderpal Singh in 75dae0c81
- feat: can read all datasets of your org with this permission "datasets:read:all-after-draft:organisation" by @Inderpal Singh in abb9385da
- feat: anyone from org can now submit dataset (not just the creator) by @Inderpal Singh in e02a99383

### Changed
- Art 19675/display activity logs immediately by @Emiliana Pali in 7e03b61ec
- docs: Update CHANGELOG for v4.0.27 by @ci-push-tag in 3450797b9

### Fixed
- fix: Use dataset contact for RDF contactPoint instead of publisher by @Inderpal Singh in e56f558cb
- fix: A published dataset can now be deprecated manually via btn by @Inderpal Singh in 4d08878d5
- fix: sync reviewed flag with Step 1 (uncheck reverts to draft) by @Rania Hamdani in 1e81b3166


## [v4.0.27] - 2025-10-16

### Added
- feat: Send email to not just creator but all metadata editors by @Inderpal Singh in 28f270dc
- feat: Introduce "datasets:edit:draft:organisation" permission to allow edit/view your org DRAFT datasets by @Inderpal Singh in 329435ef
- feat: add status mapping for unpublished datasets in Front Office RDF by @Inderpal Singh in b831f79c
- feat: Send dataset status along with dataset during ftps export by @Inderpal Singh in 18bb1057
- feat: Antivirus scanning for dataset bulk import by @Inderpal Singh in 9074348b
- feat: Return versions in RDF file for a dataset by @Inderpal Singh in 2f8c2045
- Art 16409/implement new structure for qualified attribute by @Emiliana Pali in afeddbb7

### Changed
- docs: ART:18879 add data dictionary workflow by @Rose Pasigna in e4211c6c
- docs: reoriented footer, added demo link by @Rose Pasigna in fcb3bec9
- docs: Update CHANGELOG for v4.0.26 by @ci-push-tag in a9a19734
- chore: Improve contirbuting by @Inderpal Singh in 984f44c9

### Fixed
- fix: The cryptography curation has been updated from version 46.0.2 to 46.0.3 by @Inderpal Singh in 2df9e218
- fix: ♯19698 fix Begin Approval Process bug by @Rania Hamdani in 3ef19c61
- fix: For different versions of dataset, we want identifier to be same by @Inderpal Singh in e1064d15
- fix: ignore false flag sonar issues by @Inderpal Singh in ca115748


## [v4.0.26] - 2025-10-14

### Changed
- Art 19399/rename specific location to monitoring location by @Rania Hamdani in 3bda8530
- Integrate reuse by @Inderpal Singh in 02113e9c
- docs: Update CHANGELOG for v4.0.25 by @ci-push-tag in 70e5b909

### Fixed
- fiz: bump version to fix vunerability by @Inderpal Singh in 9b9c18c0
- fix: migration (different head) by @Inderpal Singh in 90763eae
- fix: URL to publish releases to gitlab was missing by @Inderpal Singh in 2f373cbc


## [v4.0.25] - 2025-10-13

### Added

- Docs/art 18917/use featureflag to hide dga content and added screenshots to dataset howtos by @Rose Pasigna in 3d93b7f8
- feat: add antivirus scanning for CSV file uploads by @Inderpal Singh in 64cae5f8
- feat: documentation to run app on windows by @Inderpal Singh in ed8d1d33
- fix: roles and permissions feature-flag typo by @Inderpal Singh in 57f15bcf
- feat: add endpoint to remove IAM roles for users by @Inderpal Singh in f8a19a21
- feat: Reduce session length to 1 day by @Inderpal Singh in f07bea4f

### Changed

- docs/ART-19445/write-contributors-guide-for-docs-in-docsreadme by @Rose Pasigna in e26f7dc8
- test: add e2e for user deprecation by @Rania Hamdani in 350f30f4
- docs: Update CHANGELOG for v4.0.24 by @ci-push-tag in 5f299ce3

### Fixed

- fix: Missing migration to update dataset status from ARCHIVED to DEPRECATED by @Inderpal Singh in 8eaca025
- fix: Use partial text matching for applicable legislation lookup + increase length of label by @Inderpal Singh in 976d5505
- fix: the older condition $CI_COMMIT_TAG && $CI_COMMIT_BRANCH == "main" would never be true because $CI_COMMIT_BRANCH is empty when pushing tags by @Inderpal Singh in 6eabcae5
- fix: changelog link by @Inderpal Singh in 753059f8
- fix: terminate session after max age (14 days) by @Inderpal Singh in 9b32e548

## [v4.0.24] - 2025-10-09

### Added

- feat: Integrate legilux search into bulk upload legislation flow by @Inderpal Singh in ed30971260
- feat: Provide a search option to add applicable legislations via legilux by @Inderpal Singh in 1f0aaad515

### Changed

- chore: update design system by @Inderpal Singh in e2e00b2c08
- docs: Update CHANGELOG for v4.0.23 by @ci-push-tag in 1e74b35685

### Fixed

- fix: Normalize legislation URLs for consistent matching across bulk upload by @Inderpal Singh in 5e3ccdd639
- fix: Show org name in navbar, remove abbreviation from org-switcher component by @Inderpal Singh in c37251b0e6
- fix: When validating publisher, the condition should be AND and not OR to check if user is catalogue manager and has multi-tenancy enabled by @Inderpal Singh in 9dba16944e
- fix: ensure dataset modal footer buttons remain visible on small screens by @Inderpal Singh in 05f34f31e6
- fix: prevent duplicate applicable legislation creation errors by @Inderpal Singh in a457c9ec52
- fix: normalize email to lowercase for case-insensitive user matching by @Inderpal Singh in 98ae43be5b

## [v4.0.23] - 2025-10-07

### Added

- feat: support IAM login with email-based user matching by @Inderpal Singh in 562410aae

### Changed

- docs: Update CHANGELOG for v4.0.22 by @ci-push-tag in 51453ac26

## [v4.0.24] - 2025-10-09

### Added

- feat: Integrate legilux search into bulk upload legislation flow by @Inderpal Singh in ed30971260
- feat: Provide a search option to add applicable legislations via legilux by @Inderpal Singh in 1f0aaad515

### Changed

- chore: update design system by @Inderpal Singh in e2e00b2c08
- docs: Update CHANGELOG for v4.0.23 by @ci-push-tag in 1e74b35685

### Fixed

- fix: Normalize legislation URLs for consistent matching across bulk upload by @Inderpal Singh in 5e3ccdd639
- fix: Show org name in navbar, remove abbreviation from org-switcher component by @Inderpal Singh in c37251b0e6
- fix: When validating publisher, the condition should be AND and not OR to check if user is catalogue manager and has multi-tenancy enabled by @Inderpal Singh in 9dba16944e
- fix: ensure dataset modal footer buttons remain visible on small screens by @Inderpal Singh in 05f34f31e6
- fix: prevent duplicate applicable legislation creation errors by @Inderpal Singh in a457c9ec52
- fix: normalize email to lowercase for case-insensitive user matching by @Inderpal Singh in 98ae43be5b

## [v4.0.23] - 2025-10-07

### Added

- feat: support IAM login with email-based user matching by @Inderpal Singh in 562410aae

### Changed

- docs: Update CHANGELOG for v4.0.22 by @ci-push-tag in 51453ac26

## [v4.0.22] - 2025-10-07

### Added

- feat: add IAM role name mapping support to application roles (optional) by @Inderpal Singh in 0f0a9059b

### Fixed

- Art 17077/rdf builder fix and small corrections by @Emiliana Pali in d3e08e61c

## [v4.0.20] - 2025-09-29

### Added

- feat: When dataset is unpublished from UI, upload the rdf to front office (ftps) by @Inderpal Singh in cecc225d5

### Changed

- docs: Update CHANGELOG for v4.0.19 by @ci-push-tag in 71e054150

### Fixed

- fix:#17583 migration of data policy action types by @Emiliana in ded374bce
- fix: seperate document text for non cdsp by @Inderpal Singh in 13ed3d9b3

## [v4.0.19] - 2025-09-26

### Changed

- Art 17583/improve design of policy actions by @Emiliana Pali in d88f660f8bd

### Fixed

- fix: make push_tag_to_library job non-blocking for merges by @Inderpal Singh in 60c09a6b43b

## [v4.0.15] - 2025-09-22

### Added

- feat: backend clean up qualified relations by @alessandro.merola in fe517ec7328

### Changed

- chore: change flag name by @Inderpal Singh in 020698e8684
- docs: Update CHANGELOG for v4.0.14 by @ci-push-tag in c5cba738ca9

### Fixed

- fix: license field was not highlighted if there is an error by @Inderpal Singh in 5d6eefe6d75
- fix: pyparsing license declaration by @Inderpal Singh in 698745ca282
- fix: add cryptography concluded license by @Inderpal Singh in 282e102e060
- fix: Showing date time in front office list, also upload result should be green by @Inderpal Singh in 1a60e5375ac
- fix: add license for cryptography by @Inderpal Singh in b76d6d77bc5

## [v4.0.14] - 2025-09-17

### Added

- feat: SFTP -> FTPS by @Inderpal Singh in 6eb8447a
- feat: Add dedicated page for first time login unauthorised screen by @Inderpal Singh in 65fa58de

### Changed

- Fix UI message activity log for org deprecation by @Alessandro in ccab92bd
- docs: Update CHANGELOG for v4.0.13 by @ci-push-tag in b11efbc2

### Fixed

- fix; pyparsing license information by @Inderpal Singh in 13abe04b
- fix: During bulk import datasets, the permission to check if datasets can be... by @Inderpal Singh in c2ef4d44

## [v4.0.13] - 2025-09-10

### Added

- feat: Show newer version link on edit relations page by @Inderpal Singh in d283a7efc6
- feat: Deprecate old dataset if newer got published/ prevent publishing dataset that has newer published version by @Inderpal Singh in 98dba75801
- feat: Unpublish dataset (new trigger moves from PUBLISHED -> APPROVED) by @Inderpal Singh in 8c93adf965
- feat: Add activity logs for deprecation/restoration of user by @Inderpal Singh in 9a53d207a7
- feat: Only Catalogue Managers can update keywords that have more than 1 org assigned by @Inderpal Singh in 84235710d5
- feat: When new legal basis with already existing link gets created for another org, another org gets added to the existing basis by @Inderpal Singh in ab24aac444
- feat: remove key capture from ui by @Inderpal Singh in bf67a8b868
- feat: upload authentic source on the SFTP by @alessandro.merola in 39d0ba5a28
- feat: restore deprecated organisation by @Inderpal Singh in bd61ca6ba1
- feat: Make deprecation UI consistent across all entities, show alert message when SA labels got deprecated/restored by @Inderpal Singh in cf26a2b1d4
- feat: Add tooltip to actionable icons by @Inderpal Singh in 45223e84c0
- feat: Show the link to newer verson on the deprecated dataset card by @Inderpal Singh in ecc3e89e7f

### Fixed

- fix: demo env data seed generation script by @Inderpal Singh in a9466d180a
- fix: Permission should be form-fields:edit and not roles:manage by @Inderpal Singh in 4233426d99
- fix: improve UI redability upon upload by @Alessandro in 127fd2311f
- fix: If duplicate keyword is added for different org, we assign the org to original keyword but activity log was saying we created new keyword by @Inderpal Singh in d90ce79ffe
- fix: fix some syntax errors on the sftp authentic source upload by @alessandro.merola in 8214b0708f
- fix: make activity logs more informative for form fields like keywords by @Inderpal Singh in 041bb9b536
- fix: cffi license missing by @Inderpal Singh in 3d31089bcb
- fix: bump deepdiff to 8.6.1 and fix failing tests caused by this by @Inderpal Singh in f1686764f9
- fix: jsonschema-specifications ort version update by @Inderpal Singh in 2d204aebc4
- fix: Only return keywords from current organisation (rather than all assigned organisations) by @Inderpal Singh in 1c23142d96
- fix: Correct response type for list of applicable legislations endpoint by @Inderpal Singh in 5cd5b45999
- Merge branch 'fix/overlapping-warnings' into 'main' by @Inderpal Singh in 6d980722b4

## [v4.0.12] - 2025-09-02

### Added

- feat: add logic to restore a deprecated user by @alessandro.merola in 6b128135108
- feat: Upload data dictionaries to sftp server by @Inderpal Singh in c8c9b938af5
- feat: Add UI to send published datasets to sftp by @Inderpal Singh in 3a8f30fcc8c
- feat: Only published datasets can be uploaded to sftp by users with publish permission by @Inderpal Singh in 9397e34679e
- feat: implement the fetch for applicable legislation by @Alessandro in 5e1aaebc234
- feat: Added route to push dataset rdf/ttl/json to sftp server by @Inderpal Singh in cced6bfe89b
- feat: Pagination in keywords/legal basis list frontend by @Inderpal Singh in 6f6ffaf2e02
- feat: Show info message to Inventory Coordinators about new users without role not appearing in list by @Inderpal Singh in 7017393ac3f
- feat: #17356 activity logs for global promotions by @Emiliana Pali in d2ef7d1d6f5
- feat: Provide sample xls from the official repo of MinDigi by @Inderpal Singh in 297d59482e1
- feat: add the new protection type to dataset form by @Alessandro Merola in 53e74cd5b18
- feat: enhancements user deprecation by @Alessandro in 79575404587
- feat: #17356 allow cm to promote form fields to global by @Emiliana Pali in 4037ab44c58
- feat: user deprecation feature complete by @Alessandro in 27e09ccc33a
- feat: Assign form field to multiple orgs by @Inderpal Singh in 56c1ec88f2c
- feat: Add the deprecation for the user by @Alessandro Merola in 4caa750c1f3
- feat: Backend: Add service and repo method to get keywords/legal_basis via pagination by @Inderpal Singh in 5e33cb303cb

### Changed

- Docs/art 17526/batch4 approval and publish by @Inderpal Singh in 435c16e8e46
- chore: Add curations for paramiko, rpds-py by @Inderpal Singh in 5ac674de497
- Merge branch 'ART-17360/legilux-integration' into 'main' by @Inderpal Singh in cd13e6c3f3e
- Merge branch 'chore/remove-dataset-list0endpoint' into 'main' by @Inderpal Singh in 5d522a28644

### Fixed

- docs-fix-the-footer by @Rose Pasigna in 19d012669e6
- fix: Use dataset identifier in filename instead of timestamp by @Inderpal Singh in 4848be50777
- fix: Add skos preflabel for publisher type by @Inderpal Singh in 2573b584d23
- fix: sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[Organisation(organisations)], expression 'keyword_assignments' failed to locate a name ("name 'keyword_assignments' by @Inderpal Singh in aa959a024ef
- fix: use asyncssh instead of paramiko for sftp because of licensing issue by @Inderpal Singh in f58921bc741
- fix legal basis assignment issues by @Emiliana in e4d2060d64e
- fix: Dont use useCallback and fix useEffect dependency array so filters work properly by @Inderpal Singh in c1e2a984353
- fix: Dont show current dataset label, Also status tag is only shown when status is deprecated by @Inderpal Singh in 49cb7157d62
- fix: Authentic source label fixes by @Inderpal Singh in c9534665793
