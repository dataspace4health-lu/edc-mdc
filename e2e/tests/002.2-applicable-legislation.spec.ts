import { test } from "@playwright/test";
import { ApplicableLegislationPage } from "../pages/applicable-legislation-page";
import { loginAsDataManager } from "../test-utils/login-as";
import { ApplicableLegislationFixture } from "../fixtures.ts/applicable-legislation-fixture";

test("002.2.create Applicable Legislations", async ({ page }) => {
  await loginAsDataManager(page);

  const applicableLegislationPage = new ApplicableLegislationPage(page);

  await applicableLegislationPage.openPage();
  await applicableLegislationPage.assertPageLoaded();

  await applicableLegislationPage.expandForm();
  await applicableLegislationPage.setLabel("General Data Protection Regulation");
  await applicableLegislationPage.setOrganisation(ApplicableLegislationFixture.organisationName);
  await applicableLegislationPage.create();

  await applicableLegislationPage.assertCreated("General Data Protection Regulation");
});

test("002.2.a.promote applicable legislation to global", async ({ page }) => {
  await loginAsDataManager(page);

  const applicableLegislationPage = new ApplicableLegislationPage(page);

  await applicableLegislationPage.openPage();
  await applicableLegislationPage.assertPageLoaded();

  await applicableLegislationPage.expandForm();
  await applicableLegislationPage.setLabel("Applicable Legislation to Promote");
  await applicableLegislationPage.setOrganisation(ApplicableLegislationFixture.organisationName);
  await applicableLegislationPage.create();

  await applicableLegislationPage.assertCreated("Applicable Legislation to Promote");

  await applicableLegislationPage.promoteApplicableLegislationToGlobal(
    "Applicable Legislation to Promote",
  );
  await applicableLegislationPage.confirmPromotion();

  await applicableLegislationPage.assertIsGlobal("Applicable Legislation to Promote");
});
