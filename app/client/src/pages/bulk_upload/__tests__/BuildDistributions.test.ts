import { describe, it, expect, vi, beforeEach } from "vitest";
import { submitDistributions } from "../BuildDistributions";
import { toDistributionDTO, DistributionFormInputs } from "../../distributions/dto";
import client from "../../../zodiosClient/client";

vi.mock("../../../zodiosClient/client", () => ({
  default: {
    add_distribution_api_v1_datasets__dataset_id__distributions_post: vi.fn(),
  },
}));

describe("BuildDistributions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("toDistributionDTO", () => {
    it("should convert DistributionFormInputs to DTO format", () => {
      const input: DistributionFormInputs = {
        title: "Test Distribution",
        description: "Test description",
        accessURLs: ["https://example.com/data"],
        fileFormat: "CSV",
        distributionRightsStatement:
          "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
        languages: ["http://publications.europa.eu/resource/authority/language/ENG"],
        license: "no_license",
        downloadURLs: ["https://example.com/download"],
        internalOnly: false,
        isAnalytics: false,
        applicableLegislations: ["directive_2000_60_ec"],
        availability: "available",
        byteSize: 1024,
      };

      const result = toDistributionDTO(input);

      expect(result.title).toBe("Test Distribution");
      expect(result.description).toBe("Test description");
      expect(result.access_urls).toEqual(["https://example.com/data"]);
      expect(result.file_type).toBe("CSV");
      expect(result.rights_statement).toBe(
        "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
      );
      expect(result.languages).toEqual([
        "http://publications.europa.eu/resource/authority/language/ENG",
      ]);
      expect(result.license).toBe("no_license");
      expect(result.download_urls).toEqual(["https://example.com/download"]);
      expect(result.internal_only).toBe(false);
      expect(result.is_analytics).toBe(false);
      expect(result.applicable_legislations).toEqual(["directive_2000_60_ec"]);
      expect(result.availability).toBe("available");
      expect(result.byte_size).toBe(1024);
    });
  });

  describe("submitDistributions", () => {
    it("should successfully submit distributions using dedicated endpoint", async () => {
      const distributions: DistributionFormInputs[] = [
        {
          title: "CSV Distribution",
          accessURLs: ["https://example.com/data.csv"],
          fileFormat: "CSV",
          distributionRightsStatement:
            "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
          languages: ["http://publications.europa.eu/resource/authority/language/ENG"],
        },
      ];

      vi.mocked(
        client.add_distribution_api_v1_datasets__dataset_id__distributions_post,
      ).mockResolvedValue({
        id: 1,
        title: "CSV Distribution",
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any);

      const errors = await submitDistributions(123, distributions, "Test Dataset");

      expect(errors).toHaveLength(0);
      expect(
        client.add_distribution_api_v1_datasets__dataset_id__distributions_post,
      ).toHaveBeenCalledTimes(1);
      expect(
        client.add_distribution_api_v1_datasets__dataset_id__distributions_post,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          title: "CSV Distribution",
          access_urls: ["https://example.com/data.csv"],
          file_type: "CSV",
        }),
        expect.objectContaining({
          params: { dataset_id: 123 },
          withCredentials: true,
        }),
      );
    });

    it("should include backend error detail when distribution creation fails", async () => {
      const distributions: DistributionFormInputs[] = [
        {
          title: "Stuff report",
          accessURLs: ["https://example.com/data.csv"],
          fileFormat: "CSV",
          distributionRightsStatement:
            "http://publications.europa.eu/resource/authority/access-right/PUBLIC",
          languages: ["http://publications.europa.eu/resource/authority/language/ENG"],
        },
      ];

      vi.mocked(
        client.add_distribution_api_v1_datasets__dataset_id__distributions_post,
      ).mockRejectedValue({
        response: {
          status: 409,
          data: {
            detail: "A distribution with this title already exists.",
          },
        },
      });

      const errors = await submitDistributions(370, distributions, "Dataset title 1");

      expect(errors).toEqual([
        'Failed to add distribution "Stuff report" to dataset "Dataset title 1": A distribution with this title already exists.',
      ]);
    });
  });
});
