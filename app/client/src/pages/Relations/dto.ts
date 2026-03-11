import { z } from "zod";

export type RelationsTypesOption = {
  value: string;
  label: string;
};

export const RelationsTypesOptions: RelationsTypesOption[] = [
  { value: "dct:hasVersion", label: "has Version" },
  { value: "dct:isVersionOf", label: "is Version Of" },
  { value: "dct:source", label: "source" },
  { value: "dct:relation", label: "relation" },
  { value: "dct:hasPart", label: "has Part" },
  { value: "dct:isPartOf", label: "is Part Of" },
  { value: "dct:isReferencedBy", label: "is Referenced By" },
  { value: "dct:references", label: "references" },
  { value: "dct:isReplacedBy", label: "is Replaced By" },
  { value: "dct:replaces", label: "replaces" },
];

export type ExternalRelationsRoleOption = {
  value: string;
  label: string;
};

export const ExternalRelationsRoleOptions: ExternalRelationsRoleOption[] = [
  { value: "about", label: "About" },
  { value: "alternate", label: "Alternate" },
  { value: "canonical", label: "Canonical" },
  { value: "cite-as", label: "Cite As" },
  { value: "copyright", label: "Copyright" },
  { value: "deprecation", label: "Deprecation" },
  { value: "describedby", label: "Described By" },
  { value: "glossary", label: "Glossary" },
  { value: "help", label: "Help" },
  { value: "license", label: "License" },
  { value: "linkset", label: "Linkset" },
  { value: "original", label: "Original" },
  { value: "preview", label: "Preview" },
  { value: "privacy-policy", label: "Privacy Policy" },
  { value: "profile", label: "Profile" },
  { value: "related", label: "Related" },
  { value: "service", label: "Service" },
  { value: "service-desc", label: "Service Description" },
  { value: "service-doc", label: "Service Documentation" },
  { value: "service-meta", label: "Service Metadata" },
  { value: "status", label: "Status" },
  { value: "terms-of-service", label: "Terms of Service" },
  { value: "via", label: "Via" },
  { value: "is-referenced-by", label: "is Referenced By" },
];

export const RelationSchema = z
  .object({
    relationKind: z.enum(["dataset", "external"]),
    sourceId: z.string().nonempty(),

    relationType: z.string().optional(),
    targetId: z.string().optional(),
    externalUrl: z.string().optional(),
    externalRole: z.string().optional(),
    externalDescription: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.relationKind === "dataset") {
        return !!data.relationType && !!data.targetId;
      }
      if (data.relationKind === "external") {
        return !!data.externalUrl;
      }
      return false;
    },
    {
      message: "Invalid relation data based on the chosen relation kind",
    },
  );

export type Relation = z.infer<typeof RelationSchema>;

export const reciprocalMapping: Record<string, string> = {
  "dct:hasVersion": "dct:isVersionOf",
  "dct:isVersionOf": "dct:hasVersion",
  "dct:source": "dct:relation",
  "dct:relation": "dct:relation",
  "dct:hasPart": "dct:isPartOf",
  "dct:isPartOf": "dct:hasPart",
  "dct:isReferencedBy": "dct:references",
  "dct:references": "dct:isReferencedBy",
  "dct:isReplacedBy": "dct:replaces",
  "dct:replaces": "dct:isReplacedBy",
};
