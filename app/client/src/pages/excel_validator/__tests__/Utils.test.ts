import { describe, it, expect } from "vitest";
import { splitValues, parseContactLabel } from "../Utils";

describe("splitValues", () => {
  it("should split comma-separated values", () => {
    const result = splitValues("existing keyword| missing keyword|another missing");
    expect(result).toEqual(["existing keyword", "missing keyword", "another missing"]);
  });
});

describe("parseContactLabel", () => {
  it("should parse name and email from standard format", () => {
    const result = parseContactLabel("John Smith (john.smith@company.com)");
    expect(result).toEqual({
      name: "John Smith",
      email: "john.smith@company.com",
    });
  });

  it("should parse name and email with extra whitespace", () => {
    const result = parseContactLabel("Jane Doe   (jane@example.org)");
    expect(result).toEqual({
      name: "Jane Doe",
      email: "jane@example.org",
    });
  });

  it("should parse name and email without space before parentheses", () => {
    const result = parseContactLabel("Bob Johnson(bob@test.com)");
    expect(result).toEqual({
      name: "Bob Johnson",
      email: "bob@test.com",
    });
  });

  it("should handle name only (no email)", () => {
    const result = parseContactLabel("Alice Cooper");
    expect(result).toEqual({
      name: "Alice Cooper",
      email: "",
    });
  });

  it("should handle empty parentheses", () => {
    const result = parseContactLabel("Charlie Brown ()");
    expect(result).toEqual({
      name: "Charlie Brown",
      email: "",
    });
  });

  it("should handle empty string", () => {
    const result = parseContactLabel("");
    expect(result).toEqual({
      name: "",
      email: "",
    });
  });

  it("should handle whitespace-only string", () => {
    const result = parseContactLabel("   ");
    expect(result).toEqual({
      name: "",
      email: "",
    });
  });

  it("should handle malformed input with unmatched parentheses", () => {
    const result = parseContactLabel("Dave Wilson (incomplete");
    expect(result).toEqual({
      name: "Dave Wilson (incomplete",
      email: "",
    });
  });

  it("should handle email with special characters", () => {
    const result = parseContactLabel("Emma Stone (emma.stone+work@company-name.co.uk)");
    expect(result).toEqual({
      name: "Emma Stone",
      email: "emma.stone+work@company-name.co.uk",
    });
  });

  it("should handle names with special characters", () => {
    const result = parseContactLabel("François Müller (francois@example.com)");
    expect(result).toEqual({
      name: "François Müller",
      email: "francois@example.com",
    });
  });

  it("should handle potential ReDoS attack input safely", () => {
    const maliciousInput = "John Smith ((((((((((((((((((((((((((((";
    const result = parseContactLabel(maliciousInput);
    expect(result).toEqual({
      name: "John Smith ((((((((((((((((((((((((((((",
      email: "",
    });
  });

  it("should handle very long names", () => {
    const longName = "A".repeat(200);
    const result = parseContactLabel(`${longName} (test@example.com)`);
    expect(result).toEqual({
      name: longName,
      email: "test@example.com",
    });
  });
});
