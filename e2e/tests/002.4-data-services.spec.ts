import { test } from "@playwright/test";
import { AddDataServicePage } from "../pages/add-data-services-page";
import { loginAsDataManager } from "../test-utils/login-as";

test("002.4.Add a data service", async ({ page }) => {
  await loginAsDataManager(page);
  const dataservicesPage = new AddDataServicePage(page);

  await dataservicesPage.openPage();
  await dataservicesPage.assertPageLoaded();

  await dataservicesPage.addDataServiceEntry();
});
