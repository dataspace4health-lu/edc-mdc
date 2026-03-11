import { expect, test } from "vitest";
import { Utils } from "./helpers";

test("removeKeysFromObj cleans object from unwanted keys", () => {
  const data = {
    a: "a",
    b: "b",
    c: "c",
    d: "d",
  };
  const cleanedData = Utils.removeKeysFromObj(data, ["b", "c"]);
  const expected = {
    a: "a",
    d: "d",
  };
  expect(cleanedData).toStrictEqual(expected);
});

test("removeKeysFromObj leaves object untouched if keysToRemove are not present", () => {
  const data = {
    a: "a",
    b: "b",
    c: "c",
    d: "d",
  };
  const cleanedData = Utils.removeKeysFromObj(data, ["x", "y"]);
  const expected = {
    a: "a",
    b: "b",
    c: "c",
    d: "d",
  };
  expect(cleanedData).toStrictEqual(expected);
});
