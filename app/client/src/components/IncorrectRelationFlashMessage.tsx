import { ResourceDatasetType } from "../types";
import hasRelationWithInternalDataset from "../utils/hasRelationWithInternalDataset";
import { FlashMessage } from "@lnds-lu/design-system";

interface IncorrectRelationFlashMessageProps {
  dataset: ResourceDatasetType;
}

export default function IncorrectRelationFlashMessage(
  props: Readonly<IncorrectRelationFlashMessageProps>,
) {
  const { dataset } = props;
  const hasIncorrectRelation = hasRelationWithInternalDataset(dataset);
  let flashMessage = null;

  if (hasIncorrectRelation && dataset.internalOnly) {
    flashMessage =
      "This dataset is marked as internal only, but it has relations with public datasets. All related datasets must be internal-only to safeguard sensitive information.";
  } else if (hasIncorrectRelation) {
    flashMessage =
      "This dataset is part of the public catalogue, but it has relations with internal-only datasets. All related datasets must be public to ensure open access and transparency.";
  } else {
    return null;
  }

  return <FlashMessage messageType='danger' message={flashMessage} />;
}
