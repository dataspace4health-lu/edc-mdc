import { BASE_URL } from "../config";

export async function updateFeatureFlag(flagName: string, enabled: boolean) {
  const response = await fetch(`${BASE_URL}/api/v1/test/config/feature-flag`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ flag_name: flagName, enabled }),
  });
  if (!response.ok) throw new Error(`Failed to update feature flag: ${response.statusText}`);
}

export async function resetConfig() {
  const response = await fetch(`${BASE_URL}/api/v1/test/config/reset`);
  if (!response.ok) throw new Error(`Failed to reset config: ${response.statusText}`);
}
