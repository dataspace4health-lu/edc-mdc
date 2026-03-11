import { test } from "@playwright/test";
import { KeywordsPage } from "../pages/keywords-page";
import { KeywordFixture } from "../fixtures.ts/keyword-fixture";
import { loginAsDataManager } from "../test-utils/login-as";

test("002.1.create and edit keyword", async ({ page }) => {
  await loginAsDataManager(page);

  const keywordsPage = new KeywordsPage(page);

  await keywordsPage.openPage();
  await keywordsPage.assertPageLoaded();

  await keywordsPage.expandForm();
  await keywordsPage.setKeywordLabel(KeywordFixture.engLabel);
  await keywordsPage.setKeywordOrganisation(KeywordFixture.organisationName);
  await keywordsPage.createKeyword();

  await keywordsPage.assertKeywordCreated(KeywordFixture.engLabel);

  await keywordsPage.assertPromoteButtonVisible(KeywordFixture.engLabel);

  await keywordsPage.editKeyword(KeywordFixture.engLabel);
  await keywordsPage.setKeywordLabel("Updated Dummy Keyword");
  await keywordsPage.updateKeyword();

  await keywordsPage.assertKeywordCreated("Updated Dummy Keyword");
});

test("002.1.a.promote keyword to global", async ({ page }) => {
  await loginAsDataManager(page);

  const keywordsPage = new KeywordsPage(page);

  await keywordsPage.openPage();
  await keywordsPage.assertPageLoaded();

  await keywordsPage.expandForm();
  await keywordsPage.setKeywordLabel("Keyword to Promote");
  await keywordsPage.setKeywordOrganisation(KeywordFixture.organisationName);
  await keywordsPage.createKeyword();

  await keywordsPage.assertKeywordCreated("Keyword to Promote");

  await keywordsPage.promoteKeywordToGlobal("Keyword to Promote");
  await keywordsPage.confirmPromotion();

  await keywordsPage.assertKeywordIsGlobal("Keyword to Promote");
});
