import { expect, test } from "@playwright/test";
import { OrganisationFormPage } from "../pages/organisationform-page";
import {
  loginAsDataManager,
  loginAsContributor,
  loginAsCatalogueManager,
} from "../test-utils/login-as";
import { DummyContact, DummyOrganisation } from "../fixtures.ts/organisation-fixture";
import { Organisation_to_deprecate } from "../fixtures.ts/organisation-fixture";

test("002.create organisation with a contact", async ({ page }) => {
  await loginAsDataManager(page);

  const organisation = DummyOrganisation;
  const contact = DummyContact;
  const organisationFormPage = new OrganisationFormPage(page);

  await organisationFormPage.openPage();
  await organisationFormPage.assertPageLoaded();

  await organisationFormPage.setOrganisationName(organisation.name);
  await organisationFormPage.setOrganisationType(organisation.type);
  await organisationFormPage.setOrganisationEmail(organisation.email);
  await organisationFormPage.submitOrganisation();

  await organisationFormPage.assertOrganisationCreated(organisation.name);
  await organisationFormPage.openOrganisationContactsPage();

  await organisationFormPage.setContactName(contact.name);
  await organisationFormPage.setContactEmail(contact.email);
  await organisationFormPage.setContactRole(contact.role);
  await organisationFormPage.submitContact();
  await organisationFormPage.assertContactCreated();
  await organisationFormPage.DeleteContact();

  await organisationFormPage.setContactName(contact.name);
  await organisationFormPage.setContactEmail(contact.email);
  await organisationFormPage.setContactRole(contact.role);
  await organisationFormPage.submitContact();
  await organisationFormPage.assertContactCreated();

  await expect(page.locator(`text=${contact.name}`).nth(0)).toBeVisible();
  await expect(page.locator(`text=${contact.email}`)).toBeVisible();
  await expect(page.locator(`text=${contact.role}`)).toBeVisible();
});

test("002.a.only data manager can create organisation", async ({ page }) => {
  await loginAsContributor(page);

  const organisationFormPage = new OrganisationFormPage(page);

  await organisationFormPage.openPage();
  await organisationFormPage.assert403Error();
});

test("002.b.Deprecate & Restore Contact", async ({ page }) => {
  await loginAsCatalogueManager(page);

  const organisationFormPage = new OrganisationFormPage(page);

  await organisationFormPage.openPage();
  await organisationFormPage.assertPageLoaded();
  await organisationFormPage.openOrganisationContactsPage();

  await organisationFormPage.DeprecateContact();
  await organisationFormPage.assertContactDeprecated();

  await organisationFormPage.restoreContact();
  await organisationFormPage.assertContactRestored();
});

test("002.c.Deprecate Organisation", async ({ page }) => {
  await loginAsCatalogueManager(page);

  const organisation = Organisation_to_deprecate;
  const organisationFormPage = new OrganisationFormPage(page);

  await organisationFormPage.openPage();
  await organisationFormPage.assertPageLoaded();

  await organisationFormPage.setOrganisationName(organisation.name);
  await organisationFormPage.setOrganisationType(organisation.type);
  await organisationFormPage.setOrganisationEmail(organisation.email);
  await organisationFormPage.submitOrganisation();
  await organisationFormPage.assertOrganisationCreated(organisation.name);
  await organisationFormPage.DeprecateOrganisaton();
  await organisationFormPage.assertOrganisationDeprecated(organisation.name);
});
