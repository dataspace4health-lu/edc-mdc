/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { processAndAddMissingKeywords, processAndAddMissingApplicableLegislation } from "../Loader";
import client from "../../../zodiosClient/client";

vi.mock("../../../zodiosClient/client", () => ({
  default: {
    create_form_field_api_v1_form_fields__field_type__post: vi.fn(),
    search_legislation_api_v1_legilux_legislation_search_get: vi.fn(),
    search_legislation_api_v1_eurlex_legislation_search_get: vi.fn(),
    create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post:
      vi.fn(),
  },
}));

describe("processAndAddMissingKeywords", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should add keywords successfully", async () => {
    const mockCreate = vi.mocked(client.create_form_field_api_v1_form_fields__field_type__post);
    mockCreate.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingKeywords("1", ["keyword1", "keyword2"], logCallback);

    expect(mockCreate).toHaveBeenCalledTimes(2);
    expect(mockCreate).toHaveBeenCalledWith(
      {
        eng_label: "keyword1",
        organisation_ids: [1],
      },
      {
        params: { field_type: "keyword" },
        withCredentials: true,
      },
    );
    expect(logMessages).toContain('  ✓ Added keyword: "keyword1"');
    expect(logMessages).toContain('  ✓ Added keyword: "keyword2"');
  });

  it("should handle errors when adding keywords", async () => {
    const mockCreate = vi.mocked(client.create_form_field_api_v1_form_fields__field_type__post);
    mockCreate.mockRejectedValue(new Error("API Error"));

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingKeywords("1", ["failing_keyword"], logCallback);

    expect(logMessages).toEqual(
      expect.arrayContaining([expect.stringContaining('Failed to add keyword "failing_keyword"')]),
    );
  });

  it("should use null publisher id when not provided", async () => {
    const mockCreate = vi.mocked(client.create_form_field_api_v1_form_fields__field_type__post);
    mockCreate.mockResolvedValue({} as any);

    await processAndAddMissingKeywords(null, ["keyword1"]);

    expect(mockCreate).toHaveBeenCalledWith(
      {
        eng_label: "keyword1",
        organisation_ids: [],
      },
      {
        params: { field_type: "keyword" },
        withCredentials: true,
      },
    );
  });
});

describe("processAndAddMissingApplicableLegislation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should clean and truncate long descriptions from Legilux results", async () => {
    const longDescription = "A".repeat(1500) + "\n\r" + "B".repeat(100);
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: longDescription,
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"], logCallback);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Test Law",
        description: "A".repeat(997) + "...",
        link: "https://example.com/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });

  it("should clean newlines and carriage returns from descriptions", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: "Line 1\nLine 2\r\nLine 3\rLine 4",
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"]);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Test Law",
        description: "Line 1 Line 2 Line 3 Line 4",
        link: "https://example.com/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });

  it("should handle short descriptions without truncation", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: "Short description",
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"]);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Test Law",
        description: "Short description",
        link: "https://example.com/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });

  it("should clean and truncate long descriptions from EUR-Lex results", async () => {
    const longDescription = "C".repeat(1200) + "\n" + "D".repeat(100);
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockEurlexSearch = vi.mocked(
      client.search_legislation_api_v1_eurlex_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([]);
    mockEurlexSearch.mockResolvedValue([
      {
        label: "EU Law",
        description: longDescription,
        link: "https://eur-lex.europa.eu/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    await processAndAddMissingApplicableLegislation("1", ["EU Law"]);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "EU Law",
        description: "C".repeat(997) + "...",
        link: "https://eur-lex.europa.eu/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });

  it("should use URL as both label and link when no results found and input is HTTP URL", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockEurlexSearch = vi.mocked(
      client.search_legislation_api_v1_eurlex_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([]);
    mockEurlexSearch.mockResolvedValue([]);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["http://example.com/law"], logCallback);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "http://example.com/law",
        description: "",
        link: "http://example.com/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
    expect(logMessages).toContain("    Using URL as both label and link");
  });

  it("should use URL as both label and link when no results found and input is HTTPS URL", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockEurlexSearch = vi.mocked(
      client.search_legislation_api_v1_eurlex_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([]);
    mockEurlexSearch.mockResolvedValue([]);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation(
      "1",
      ["https://example.com/secure-law"],
      logCallback,
    );

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "https://example.com/secure-law",
        description: "",
        link: "https://example.com/secure-law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
    expect(logMessages).toContain("    Using URL as both label and link");
  });

  it("should use original text as label with empty link when no results found and input is not a URL", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockEurlexSearch = vi.mocked(
      client.search_legislation_api_v1_eurlex_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([]);
    mockEurlexSearch.mockResolvedValue([]);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["Some Random Text"], logCallback);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Some Random Text",
        description: "",
        link: "",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
    expect(logMessages).toContain("    Using original text as label");
  });

  it("should handle EUR-Lex failure gracefully and fall back to original text", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockEurlexSearch = vi.mocked(
      client.search_legislation_api_v1_eurlex_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([]);
    mockEurlexSearch.mockRejectedValue(new Error("EUR-Lex is down"));
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"], logCallback);

    expect(logMessages).toContain("    EUR-Lex unavailable, using original text");
    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Test Law",
        description: "",
        link: "",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });

  it("should handle duplicate legislations", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: "Description",
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    await processAndAddMissingApplicableLegislation("1", ["Test Law", "Test Law", "Test Law"]);

    // Should only be called once due to deduplication
    expect(mockLegiluxSearch).toHaveBeenCalledTimes(1);
    expect(mockCreateApplicableLegislation).toHaveBeenCalledTimes(1);
  });

  it("should handle 400 error for already existing legislation", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Existing Law",
        description: "Description",
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockRejectedValue({
      response: {
        status: 400,
        data: {
          detail: "Applicable legislation already exists",
        },
      },
    });

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["Existing Law"], logCallback);

    expect(logMessages).toContain(
      '  ⓘ Applicable legislation "Existing Law" already exists, skipping',
    );
  });

  it("should handle other errors when creating applicable legislation", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: "Description",
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockRejectedValue(new Error("Internal Server Error"));

    const logMessages: string[] = [];
    const logCallback = (msg: string) => logMessages.push(msg);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"], logCallback);

    expect(logMessages).toEqual(
      expect.arrayContaining([
        expect.stringContaining('Failed to add applicable legislation "Test Law"'),
      ]),
    );
  });

  it("should handle null or empty descriptions", async () => {
    const mockLegiluxSearch = vi.mocked(
      client.search_legislation_api_v1_legilux_legislation_search_get,
    );
    const mockCreateApplicableLegislation = vi.mocked(
      client.create_applicable_legislation_form_field_api_v1_form_fields_applicable_legislation_post,
    );

    mockLegiluxSearch.mockResolvedValue([
      {
        label: "Test Law",
        description: null,
        link: "https://example.com/law",
      },
    ] as any);
    mockCreateApplicableLegislation.mockResolvedValue({} as any);

    await processAndAddMissingApplicableLegislation("1", ["Test Law"]);

    expect(mockCreateApplicableLegislation).toHaveBeenCalledWith(
      {
        eng_label: "Test Law",
        description: "",
        link: "https://example.com/law",
        organisation_ids: [1],
      },
      { withCredentials: true },
    );
  });
});
