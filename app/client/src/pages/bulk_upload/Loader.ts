import client from "../../zodiosClient/client";

export const fetchFormFields = async () => {
  try {
    return (await client.retrieve_form_fields_api_v1_form_fields_get({
      withCredentials: true,
    })) as Record<string, Record<string, Array<{ value: string; eng_label: string }>>>;
  } catch (error) {
    console.error("Error fetching rawData:", error);
    throw new Error("Unable to fetch raw data.");
  }
};

export const processAndAddMissingKeywords = async (
  publisherId: string | null,
  missingKeywords: string[],
  logCallback?: (message: string) => void,
) => {
  for (const keyword of missingKeywords) {
    try {
      await client.create_form_field_api_v1_form_fields__field_type__post(
        {
          eng_label: keyword,
          organisation_ids: publisherId ? [Number(publisherId)] : [],
        },
        {
          params: {
            field_type: "keyword",
          },
          withCredentials: true,
        },
      );
      if (logCallback) {
        logCallback(`  ✓ Added keyword: "${keyword}"`);
      }
    } catch (err) {
      const errorMsg = `Failed to add keyword "${keyword}": ${err instanceof Error ? err.message : String(err)}`;
      console.error(errorMsg);
      if (logCallback) {
        logCallback(`  ✗ ${errorMsg}`);
      }
    }
  }
};

export const processAndAddMissingApplicableLegislation = async (
  publisherId: string | null,
  missingLegislation: string[],
  logCallback?: (message: string) => void,
) => {
  // Deduplicate legislations to avoid race conditions
  const uniqueLegislations = [...new Set(missingLegislation)];

  for (const applicable_legislation of uniqueLegislations) {
    try {
      let legislationData = null;

      // First, try searching Legilux for the legislation
      if (logCallback) {
        logCallback(`  Searching Legilux for: "${applicable_legislation}"`);
      }
      const legiluxResults = await client.search_legislation_api_v1_legilux_legislation_search_get({
        queries: { query: applicable_legislation },
        withCredentials: true,
      });

      if (legiluxResults.length > 0) {
        const rawDescription = legiluxResults[0].description || "";
        const cleanDescription = rawDescription.replace(/[\n\r]+/g, " ").trim();
        legislationData = {
          eng_label: legiluxResults[0].label,
          description:
            cleanDescription.length > 1000
              ? cleanDescription.substring(0, 997) + "..."
              : cleanDescription,
          link: legiluxResults[0].link,
        };
        if (logCallback) {
          logCallback(`    Found in Legilux: "${legiluxResults[0].label}"`);
        }
      } else {
        // If no Legilux results, try EUR-Lex (often down, so fail fast)
        try {
          if (logCallback) {
            logCallback(`    Not found in Legilux, trying EUR-Lex...`);
          }
          const eurlexResults =
            await client.search_legislation_api_v1_eurlex_legislation_search_get({
              queries: { query: applicable_legislation },
              withCredentials: true,
            });

          if (eurlexResults.length > 0) {
            const rawDescription = eurlexResults[0].description || "";
            const cleanDescription = rawDescription.replace(/[\n\r]+/g, " ").trim();
            legislationData = {
              eng_label: eurlexResults[0].label,
              description:
                cleanDescription.length > 1000
                  ? cleanDescription.substring(0, 997) + "..."
                  : cleanDescription,
              link: eurlexResults[0].link,
            };
            if (logCallback) {
              logCallback(`    Found in EUR-Lex: "${eurlexResults[0].label}"`);
            }
          }
        } catch (eurlexErr) {
          // EUR-Lex is often down - log and continue without blocking bulk import
          console.warn(`EUR-Lex unavailable for "${applicable_legislation}", using fallback`);
          if (logCallback) {
            logCallback(`    EUR-Lex unavailable, using original text`);
          }
          // Continue to fallback (legislationData remains null)
        }
      }

      // If no results from either source, use the original text
      if (!legislationData) {
        // Check if the input is a URL
        const isUrl =
          applicable_legislation.startsWith("http://") ||
          applicable_legislation.startsWith("https://");

        if (isUrl) {
          // If it's a URL, use it as both the link and the label
          legislationData = {
            eng_label: applicable_legislation,
            description: "",
            link: applicable_legislation,
          };
        } else {
          // If it's not a URL, use it as label with empty link
          legislationData = {
            eng_label: applicable_legislation,
            description: "",
            link: "",
          };
        }
        if (logCallback) {
          logCallback(
            `    Using ${isUrl ? "URL as both label and link" : "original text as label"}`,
          );
        }
      }

      await client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post(
        {
          ...legislationData,
          organisation_ids: publisherId ? [Number(publisherId)] : [],
        },
        {
          withCredentials: true,
        },
      );
      if (logCallback) {
        logCallback(`  ✓ Added applicable legislation: "${legislationData.eng_label}"`);
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      // Handle 400 error gracefully - it means the legislation already exists
      if (
        err?.response?.status === 400 &&
        err?.response?.data?.detail?.includes("already exists")
      ) {
        if (logCallback) {
          logCallback(
            `  ⓘ Applicable legislation "${applicable_legislation}" already exists, skipping`,
          );
        }
        console.log(
          `Applicable legislation "${applicable_legislation}" already exists, skipping...`,
        );
      } else {
        const errorMsg = `Failed to add applicable legislation "${applicable_legislation}": ${err?.message || String(err)}`;
        console.error(errorMsg);
        if (logCallback) {
          logCallback(`  ✗ ${errorMsg}`);
        }
      }
    }
  }
};

export const addContactToOrganisation = async (
  organisationId: number,
  contactName: string,
  contactEmail: string,
) => {
  try {
    await client.add_contact_api_v1_organisations__organisation_id__contacts_post(
      {
        name: contactName,
        email: contactEmail,
      },
      {
        params: { organisation_id: organisationId },
        withCredentials: true,
      },
    );
  } catch (error) {
    console.error(`Error adding contact ${contactName} (${contactEmail}):`, error);
    throw error;
  }
};
