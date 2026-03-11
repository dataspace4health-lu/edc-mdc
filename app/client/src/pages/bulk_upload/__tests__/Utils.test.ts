import { describe, it, expect, vi } from "vitest";
import { getApplicableLegislationValueFromLabel, parseNumber } from "../Utils";

// Mock the zodios client to avoid initialization errors in tests
vi.mock("../../../zodiosClient/client", () => ({
  default: {},
}));

const createMockRawData = () => ({
  dataset: {
    applicable_legislations: [
      {
        key: "directive_2000_60_ec",
        value: "directive_2000_60_ec",
        eng_label:
          "Directive 2000/60/EC of the European Parliament and of the Council of 23 October 2000 establishing a",
        description:
          "Directive 2000/60/EC of the European Parliament and of the Council of 23 October 2000 establishing a framework for Community action in the field of water policy",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32000L0060",
        organisation_ids: [3],
      },
      {
        key: "directive_2007_60_ec",
        value: "directive_2007_60_ec",
        eng_label:
          "Directive 2007/60/EC of the European Parliament and of the Council of 23 October 2007 on the assessm",
        description:
          "Directive 2007/60/EC of the European Parliament and of the Council of 23 October 2007 on the assessment and management of flood risks (Text with EEA relevance)",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32007L0060",
        organisation_ids: [3],
      },
      {
        key: "commission_implementing_decision_eu_2020_1161",
        value: "commission_implementing_decision_eu_2020_1161",
        eng_label:
          "Commission Implementing Decision (EU) 2020/1161 of 4 August 2020 establishing a watch list of substa",
        description:
          "Commission Implementing Decision (EU) 2020/1161 of 4 August 2020 establishing a watch list of substances for Union-wide monitoring in the field of water policy pursuant to Directive 2008/105/EC of the European Parliament and of the Council (notified under document number C(2020) 5205) (Text with EEA relevance)",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32020D1161",
        organisation_ids: [3],
      },
      {
        key: "directive_eu_2019_1024",
        value: "directive_eu_2019_1024",
        eng_label:
          "Directive (EU) 2019/1024 of the European Parliament and of the Council of 20 June 2019 on open data ",
        description:
          "Directive (EU) 2019/1024 of the European Parliament and of the Council of 20 June 2019 on open data and the re-use of public sector information (recast)",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32019L1024",
        organisation_ids: [3],
      },
      {
        key: "council_directive_91_676_eec",
        value: "council_directive_91_676_eec",
        eng_label:
          "Council Directive 91/676/EEC of 12 December 1991 concerning the protection of waters against polluti",
        description:
          "Council Directive 91/676/EEC of 12 December 1991 concerning the protection of waters against pollution caused by nitrates from agricultural sources",
        link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:31991L0676",
        organisation_ids: [3],
      },
    ],
  },
});

describe("getApplicableLegislationValueFromLabel", () => {
  describe("CELEX code matching", () => {
    it("should match ELI format URL with CELEX format URL (Directive)", () => {
      const rawData = createMockRawData();
      const eliUrl = "https://eur-lex.europa.eu/eli/dir/2000/60/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("directive_2000_60_ec");
    });

    it("should match ELI format URL with locale parameter", () => {
      const rawData = createMockRawData();
      const eliUrl = "https://eur-lex.europa.eu/eli/dir/2007/60/oj?locale=fr";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("directive_2007_60_ec");
    });

    it("should match Decision ELI format", () => {
      const rawData = createMockRawData();
      const eliUrl = "https://eur-lex.europa.eu/eli/dec/2020/1161/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("commission_implementing_decision_eu_2020_1161");
    });

    it("should match CELEX format URL directly", () => {
      const rawData = createMockRawData();
      const celexUrl = "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32019L1024";
      const result = getApplicableLegislationValueFromLabel(celexUrl, rawData);
      expect(result).toBe("directive_eu_2019_1024");
    });

    it("should match old-style directive from 1991", () => {
      const rawData = createMockRawData();
      const eliUrl = "https://eur-lex.europa.eu/eli/dir/1991/676/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("council_directive_91_676_eec");
    });
  });

  describe("Label and description matching", () => {
    it("should match by partial eng_label", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel("Directive 2000/60/EC", rawData);
      expect(result).toBe("directive_2000_60_ec");
    });

    it("should match by description content", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel(
        "framework for Community action",
        rawData,
      );
      expect(result).toBe("directive_2000_60_ec");
    });

    it("should match by exact value", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel("directive_2007_60_ec", rawData);
      expect(result).toBe("directive_2007_60_ec");
    });
  });

  describe("URL normalization", () => {
    it("should match URLs regardless of case", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel(
        "https://EUR-LEX.EUROPA.EU/eli/dir/2000/60/oj",
        rawData,
      );
      expect(result).toBe("directive_2000_60_ec");
    });

    it("should match with data. subdomain removed", () => {
      const rawData = {
        dataset: {
          applicable_legislations: [
            {
              value: "test_law",
              eng_label: "Test Law",
              link: "https://data.example.com/law/123",
              organisation_ids: [1],
            },
          ],
        },
      };
      const result = getApplicableLegislationValueFromLabel("https://example.com/law/123", rawData);
      expect(result).toBe("test_law");
    });
  });

  describe("Edge cases", () => {
    it("should return null when no match is found", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel(
        "https://example.com/nonexistent",
        rawData,
      );
      expect(result).toBeNull();
    });

    it("should return null when legal_bases is empty", () => {
      const rawData = {
        dataset: {
          legal_bases: [],
        },
      };
      const result = getApplicableLegislationValueFromLabel("some legislation", rawData);
      expect(result).toBeNull();
    });

    it("should return null when legal_bases is undefined", () => {
      const rawData = {
        dataset: {},
      };
      const result = getApplicableLegislationValueFromLabel("some legislation", rawData);
      expect(result).toBeNull();
    });

    it("should handle empty label", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel("", rawData);
      expect(result).toBeNull();
    });

    it("should handle whitespace-only label", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel("   ", rawData);
      expect(result).toBeNull();
    });

    it("should trim whitespace from label", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel("  directive_2000_60_ec  ", rawData);
      expect(result).toBe("directive_2000_60_ec");
    });
  });

  describe("Custom field parameter", () => {
    it("should search in custom field when specified", () => {
      const rawData = {
        dataset: {
          custom_legal_field: [
            {
              value: "custom_law",
              eng_label: "Custom Law",
              link: "https://example.com/custom",
              organisation_ids: [1],
            },
          ],
        },
      };
      const result = getApplicableLegislationValueFromLabel(
        "Custom Law",
        rawData,
        "custom_legal_field",
      );
      expect(result).toBe("custom_law");
    });

    it("should return null when custom field does not exist", () => {
      const rawData = createMockRawData();
      const result = getApplicableLegislationValueFromLabel(
        "Directive 2000/60/EC",
        rawData,
        "nonexistent_field",
      );
      expect(result).toBeNull();
    });
  });

  describe("Complex URL scenarios", () => {
    it("should match ELI directive with 3-digit number", () => {
      const rawData = {
        dataset: {
          applicable_legislations: [
            {
              value: "test_directive",
              eng_label: "Test Directive",
              link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32015L0495",
              organisation_ids: [1],
            },
          ],
        },
      };
      const eliUrl = "https://eur-lex.europa.eu/eli/dir/2015/495/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("test_directive");
    });

    it("should match ELI directive with 4-digit number", () => {
      const rawData = {
        dataset: {
          applicable_legislations: [
            {
              value: "test_directive_2",
              eng_label: "Test Directive 2",
              link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32022D1307",
              organisation_ids: [1],
            },
          ],
        },
      };
      const eliUrl = "https://eur-lex.europa.eu/eli/dec/2022/1307/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("test_directive_2");
    });

    it("should match regulation ELI format", () => {
      const rawData = {
        dataset: {
          applicable_legislations: [
            {
              value: "test_regulation",
              eng_label: "Test Regulation",
              link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32023R0138",
              organisation_ids: [1],
            },
          ],
        },
      };
      const eliUrl = "https://eur-lex.europa.eu/eli/reg/2023/138/oj";
      const result = getApplicableLegislationValueFromLabel(eliUrl, rawData);
      expect(result).toBe("test_regulation");
    });
  });

  describe("Priority of matching methods", () => {
    it("should prioritize CELEX code match over label match", () => {
      const rawData = {
        dataset: {
          applicable_legislations: [
            {
              value: "correct_match",
              eng_label: "Wrong Label",
              link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32000L0060",
              organisation_ids: [1],
            },
            {
              value: "wrong_match",
              eng_label: "Directive 2000/60/EC",
              link: "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32001L0001",
              organisation_ids: [1],
            },
          ],
        },
      };
      // ELI URL that matches CELEX code of first item
      const result = getApplicableLegislationValueFromLabel(
        "https://eur-lex.europa.eu/eli/dir/2000/60/oj",
        rawData,
      );
      expect(result).toBe("correct_match");
    });
  });
});

describe("parseNumber", () => {
  it("should parse valid positive integer", () => {
    expect(parseNumber("42")).toBe(42);
  });

  it("should parse valid negative integer", () => {
    expect(parseNumber("-42")).toBe(-42);
  });

  it("should parse valid decimal number", () => {
    expect(parseNumber("3.14")).toBe(3.14);
  });

  it("should parse zero", () => {
    expect(parseNumber("0")).toBe(0);
  });

  it("should return null for empty string", () => {
    expect(parseNumber("")).toBeNull();
  });

  it("should return null for whitespace-only string", () => {
    expect(parseNumber("   ")).toBeNull();
  });

  it("should return null for invalid number string", () => {
    expect(parseNumber("abc")).toBeNull();
  });

  it("should return null for mixed alphanumeric string", () => {
    expect(parseNumber("12abc")).toBeNull();
  });

  it("should parse number with leading/trailing spaces", () => {
    expect(parseNumber("  42  ")).toBe(42);
  });

  it("should parse scientific notation", () => {
    expect(parseNumber("1e3")).toBe(1000);
  });
});
