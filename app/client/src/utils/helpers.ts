// eslint-disable-next-line @typescript-eslint/no-explicit-any
const removeKeysFromObj = (obj: { [key: string]: any }, keysToRemove: Array<string>) =>
  Object.keys(obj).reduce((curr, next) => {
    if (keysToRemove.includes(next)) {
      delete curr[next];
    }
    return curr;
  }, obj);

export const Utils = {
  removeKeysFromObj,
};
