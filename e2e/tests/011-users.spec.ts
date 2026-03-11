import { test } from "@playwright/test";
import { UsersPage } from "../pages/users-page";
import {
  UserFixture,
  UnassignedUserFixture,
  UserToDeprecateFixture,
} from "../fixtures.ts/user-fixture";
import { loginAsCatalogueManager } from "../test-utils/login-as";
import { updateFeatureFlag } from "../test-utils/config-api";

test("011.create and delete an assignment", async ({ page }) => {
  await loginAsCatalogueManager(page);
  await updateFeatureFlag("enable_multi_tenants", true);

  const usersPage = new UsersPage(page);

  await usersPage.openPage();
  await usersPage.assertPageLoaded();
  await usersPage.SelectExpandForm();

  await usersPage.setUserEmail(UserFixture.email);
  await usersPage.setUserOrganisation(UserFixture.organisation);
  await usersPage.setUserRole(UserFixture.role1);
  await usersPage.createAssignment();
  await usersPage.assertAssignCreated();

  await page.waitForTimeout(500);

  await usersPage.deleteOrganisation();
  await usersPage.assertOrganisationDeleted();
  await usersPage.assertAssignDeleted(UserFixture.role1);

  await usersPage.setUserEmail(UserFixture.email);
  await usersPage.setUserOrganisation(UserFixture.organisation);
  await usersPage.setUserRole(UserFixture.role1);
  await usersPage.createAssignment();
  await usersPage.assertAssignCreated();

  await usersPage.setUserEmail(UserFixture.email);
  await usersPage.setUserOrganisation(UserFixture.organisation);
  await usersPage.setUserRole(UserFixture.role2);
  await usersPage.createAssignment();
  await usersPage.assertAssignCreated();

  await page.waitForTimeout(500);

  await usersPage.deleteRole(UserFixture.role1);
  await usersPage.assertRoleDeleted();
  await usersPage.assertAssignDeleted(UserFixture.role1);

  await usersPage.deleteRole(UserFixture.role2);
  await usersPage.assertRoleDeleted();
  await usersPage.assertAssignDeleted(UserFixture.role2);
});

test("011.a.delete an unassigned user", async ({ page }) => {
  await loginAsCatalogueManager(page);

  const usersPage = new UsersPage(page);

  await usersPage.openPage();
  await usersPage.assertPageLoaded();

  await usersPage.setUserEmail(UnassignedUserFixture.email);

  await usersPage.assertUserDeleted(UnassignedUserFixture.email);
});

test("011.b.Deprecate user", async ({ page }) => {
  await loginAsCatalogueManager(page);
  await updateFeatureFlag("enable_multi_tenants", true);

  const usersPage = new UsersPage(page);

  await usersPage.openPage();
  await usersPage.assertPageLoaded();
  await usersPage.SelectExpandForm();

  await usersPage.setUserEmail(UserToDeprecateFixture.email);
  await usersPage.setUserOrganisation(UserToDeprecateFixture.organisation);
  await usersPage.setUserRole(UserToDeprecateFixture.role);
  await usersPage.createAssignment();
  await usersPage.assertAssignCreated();
  await usersPage.assertUserCreated(UserToDeprecateFixture.email);

  await usersPage.DeprecateUser(UserToDeprecateFixture.email);

  await usersPage.assertUserDeprecated(UserToDeprecateFixture.email);
});
