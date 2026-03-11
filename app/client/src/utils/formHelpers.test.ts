import { expect, test } from "vitest";
import { FormHelpers } from "./formHelpers";

test("mapFormDataValues concats the FormData fields ending with [] in a dedicated array", () => {
  const formDataEntriesLikeData: Array<[string, string]> = [
    ["name", "bob"],
    ["age", "40"],
    ["colors[]", "red"],
    ["tags[]", "important"],
    ["tags[]", "sensitive"],
    ["city", "Luxembourg"],
    ["security-chkBox#-team1", "team1"],
    ["security-chkBox#-team2", "team2"],
    ["colors[]", "blue"],
  ];
  const jsonLikeFormData = formDataEntriesLikeData.reduce(FormHelpers.mapFormDataValues, {});
  const expected = {
    name: "bob",
    age: "40",
    tags: ["important", "sensitive"],
    city: "Luxembourg",
    security: ["team1", "team2"],
    colors: ["red", "blue"],
  };
  expect(jsonLikeFormData).toStrictEqual(expected);
});

test("gatherPrefixedKeys works", () => {
  const obj = {
    name: "alice",
    age: "35",
    "id-56793-id": "56793",
    "id-56793-message": "Hello",
    "id-56793-time": "12:30",
    "id-65434-id": "65434",
    "id-65434-message": "Bonjour",
  };
  const expected = {
    name: "alice",
    age: "35",
    items: [
      { id: "56793", message: "Hello", time: "12:30" },
      { id: "65434", message: "Bonjour" },
    ],
  };

  expect(FormHelpers.gatherPrefixedKeys(obj, /^id-[0-9a-zA-Z]*-/, "items")).toStrictEqual(expected);
});
