import { Locator, Page } from "@playwright/test";

export const fillAutoComplete = async (
  page: Page,
  index: number,
  value: string | string[],
): Promise<void> => {
  const comboboxes = await page.getByRole("combobox").all();

  if (!Array.isArray(value)) {
    return await insertValue(comboboxes[index], page, value);
  }

  for (const word of value) {
    await insertValue(comboboxes[index], page, word);
  }
};

const insertValue = async (combobox: Locator, page: Page, value: string) => {
  await combobox.fill(value);
  await page.waitForTimeout(500);

  // Check if "No options" message is visible
  const noOptions = page.getByText("No options", { exact: false });
  const hasNoOptions = await noOptions.isVisible().catch(() => false);

  if (hasNoOptions) {
    throw new Error(`No options available in dropdown for value: "${value}"`);
  }

  await page.keyboard.press("Enter");
};
