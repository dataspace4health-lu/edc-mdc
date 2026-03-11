import { test, expect } from "@playwright/test";
import { LandingPage } from "../pages/landing-page";
import { loginAsCatalogueManager } from "../test-utils/login-as";
import { DummyDataset, DummyDataset2 } from "../fixtures.ts/dataset-fixture";

test("017.filter by dataset type", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  await landingPage.assertDatasetExists(DummyDataset);
  await landingPage.assertDatasetExists(DummyDataset2);

  await landingPage.selectFilterOption("Dataset Type", "Structured data");
  await landingPage.waitForLoaderToDisappear();

  await expect(page.getByText(DummyDataset.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset2.title).first()).not.toBeVisible();

  await landingPage.removeFilterTag("Structured data");
  await landingPage.waitForLoaderToDisappear();
});

test("017.a.filter by rights statement", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  const rightsCheckbox = page.getByRole("checkbox", { name: "Public", exact: true });
  await rightsCheckbox.check();
  await landingPage.waitForLoaderToDisappear();

  await expect(page.getByText(DummyDataset2.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset.title).first()).not.toBeVisible();

  await rightsCheckbox.uncheck();
  await landingPage.waitForLoaderToDisappear();

  await expect(page.getByText(DummyDataset.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset2.title).first()).toBeVisible();
});

test("017.b.filter by keywords", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  await landingPage.selectFilterOption("Keywords", "connectivity");
  await landingPage.waitForLoaderToDisappear();

  await expect(page.getByText(DummyDataset.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset2.title).first()).not.toBeVisible();

  await landingPage.removeFilterTag("connectivity");
  await landingPage.waitForLoaderToDisappear();
});

test("017.c.combine multiple filters", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  await landingPage.selectFilterOption("Dataset Type", "Structured data");
  await landingPage.waitForLoaderToDisappear();

  await landingPage.selectFilterOption("Keywords", "connectivity");
  await landingPage.waitForLoaderToDisappear();

  await expect(page.getByText(DummyDataset.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset2.title).first()).not.toBeVisible();

  await landingPage.removeFilterTag("Structured data");
  await landingPage.removeFilterTag("connectivity");
  await landingPage.waitForLoaderToDisappear();
});

test("017.d.verify filters persist in url", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  await landingPage.selectFilterOption("Dataset Type", "Structured data");
  await landingPage.waitForLoaderToDisappear();

  const url = page.url();
  expect(url).toContain("datasetTypes=");
  expect(url).toContain("STRUCTURED_DATA");

  await page.reload();
  await landingPage.waitForLoaderToDisappear();

  const filterTag = page.locator(`[class*="multiValue"]`, { hasText: "Structured data" });
  await expect(filterTag).toBeVisible();

  await expect(page.getByText(DummyDataset.title).first()).toBeVisible();
  await expect(page.getByText(DummyDataset2.title).first()).not.toBeVisible();

  await landingPage.removeFilterTag("Structured data");
  await landingPage.waitForLoaderToDisappear();
});

test("017.e.verify filters persist across tabs", async ({ page }) => {
  await loginAsCatalogueManager(page);
  const landingPage = new LandingPage(page);

  await landingPage.openPage();
  await landingPage.assertPageLoaded();
  await landingPage.switchToPublishedTab();
  await landingPage.waitForLoaderToDisappear();

  await landingPage.selectFilterOption("Dataset Type", "Structured data");
  await landingPage.waitForLoaderToDisappear();

  const filterTag = page.locator(`[class*="multiValue"]`, { hasText: "Structured data" });
  await expect(filterTag).toBeVisible();

  const url = page.url();
  expect(url).toContain("status=PUBLISHED");
  expect(url).toContain("datasetTypes=");

  // manual switching because uitility method assumes status filter is always first
  const draftTabLink = page.getByRole("link", { name: "Draft" });
  await draftTabLink.click();
  await page.waitForURL(/status=DRAFT/);
  await landingPage.waitForLoaderToDisappear();

  const draftUrl = page.url();
  expect(draftUrl).toContain("status=DRAFT");
  expect(draftUrl).toContain("datasetTypes=");
  await expect(filterTag).toBeVisible();

  const publishedTabLink = page.getByRole("link", { name: "Published" });
  await publishedTabLink.click();
  await page.waitForURL(/status=PUBLISHED/);
  await landingPage.waitForLoaderToDisappear();

  await landingPage.removeFilterTag("Structured data");
  await landingPage.waitForLoaderToDisappear();
});
