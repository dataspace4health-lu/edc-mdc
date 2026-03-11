import { expect } from "@playwright/test";
import type { Page } from "playwright";
import { BASE_URL } from "../config";
import { readFileSync } from "fs";
import {
  DummyDataset,
  RightsLabelValueMapping,
  ApplicableLegislationsLabelValueMapping,
  DummyDistribution,
  LanguagesLabelValueMapping,
} from "../fixtures.ts/dataset-fixture";

export class CataloguePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async downloadCatalogue() {
    const promise = this.page.waitForEvent("download");
    try {
      await this.page.goto(`${BASE_URL}/api/v1/catalogue.rdf`);
      // eslint-disable-next-line no-empty, @typescript-eslint/no-unused-vars
    } catch (error) {}

    await this.page.waitForLoadState("networkidle");
    const download = await promise;

    await download.path();
    await download.saveAs(`./${download.suggestedFilename()}`);

    expect(download.suggestedFilename()).toBe("catalogue.rdf");
  }

  async assertDataset() {
    const content = readFileSync("./catalogue.rdf", { encoding: "utf8" });

    expect(content).toContain("Luxembourg National Data Service");
    expect(content).toContain(
      '<dct:description xml:lang="eng">The Luxembourg National Data Catalogue aims to provide a comprehensive overview of all data available in the public sector in Luxembourg</dct:description>',
    );
    expect(content).toMatch(
      /<dcat:Dataset rdf:about="http:\/\/localhost:8000\/api\/v1\/datasets\/[0-9a-f-]{36}">/i,
    );
    expect(content).toContain(`<dct:title xml:lang="eng">${DummyDataset.title}</dct:title>`);
    expect(content).toContain(DummyDataset.description);
    expect(content).toContain(DummyDataset.publisherName);
    expect(content).toContain(RightsLabelValueMapping[DummyDataset.rights]);
    expect(content).toContain(
      `<r5r:applicableLegislation rdf:resource="${
        ApplicableLegislationsLabelValueMapping[DummyDataset.applicableLegislations[0]]
      }"/>`,
    );
    expect(content).toContain(
      `<rdfs:label xml:lang="eng">${DummyDataset.applicableLegislations[0]}</rdfs:label>`,
    );

    DummyDataset.keywords.forEach((keyword) => {
      expect(content).toContain(`<dcat:keyword xml:lang="eng">${keyword}</dcat:keyword>`);
    });

    expect(content).toContain("http://publications.europa.eu/resource/authority/data-theme/ENER");
    expect(content).toContain("http://publications.europa.eu/resource/authority/data-theme/HEAL");
    expect(content).toContain("http://publications.europa.eu/resource/authority/country/LUX");
    expect(content).toContain("http://publications.europa.eu/resource/authority/frequency/ANNUAL");

    expect(content).toContain(DummyDataset.creatorNames[0]);
    expect(content).toContain(DummyDataset.version);
    expect(content).toContain(DummyDataset.version_notes[0]);
    expect(content).toContain(DummyDataset.provenance[0]);
    expect(content).toContain(DummyDataset.documentation[0]);
    expect(content).toContain(LanguagesLabelValueMapping[DummyDataset.languages[0]]);
    expect(content).toContain("<dct:provenance");
    expect(content).toContain("<dcat:landingPage>");
    expect(content).toContain(
      `<rdfs:label xml:lang="eng">${DummyDataset.provenance[0]}</rdfs:label>`,
    );
    expect(content).toContain(`<foaf:Document rdf:about="${DummyDataset.landingPages[0]}"`);
    expect(content).toContain(DummyDataset.conforms_to[0]);
    expect(content).toContain(DummyDataset.conforms_to[1]);
    // Check that at least one spatial resolution value is in the RDF
    expect(content).toContain(DummyDataset.spatial_resolutions[0].toString());
    expect(content).toContain(DummyDataset.temporal_resolution);
    expect(content).toContain(DummyDataset.other_identifiers[0]);

    expect(content).toContain(DummyDistribution.title);
    expect(content).toContain(DummyDistribution.description);
    DummyDistribution.documentation.forEach((doc) => {
      expect(content).toContain(doc);
    });
    DummyDistribution.applicableLegislations.forEach((applicableLegislation) => {
      expect(content).toContain(applicableLegislation);
    });
    expect(content).toContain("<adms:status>");
    expect(content).toContain(
      `<skos:Concept rdf:about="http://publications.europa.eu/resource/authority/distribution-status/${DummyDistribution.distributionDCATStatus.toUpperCase()}">`,
    );
    expect(content).toContain(
      `<skos:prefLabel xml:lang="eng">${DummyDistribution.distributionDCATStatus}</skos:prefLabel>`,
    );
    expect(content).toContain("<r5r:availability>");
    expect(content).toContain(
      `<skos:Concept rdf:about="http://publications.europa.eu/resource/authority/planned-availability/${DummyDistribution.availability.toUpperCase()}">`,
    );
    expect(content).toContain(
      `<skos:prefLabel xml:lang="eng">${DummyDistribution.availability}</skos:prefLabel>`,
    );
    expect(content).toContain(DummyDistribution.modification_date);
    expect(content).toContain(DummyDistribution.distribution_release_date);
    expect(content).toContain(DummyDistribution.size_bytes.toString());
    expect(content).toContain(DummyDistribution.checksum);
    if (DummyDistribution.policy_actions && DummyDistribution.policy_actions.length > 0) {
      expect(content).toContain("odrl:hasPolicy");
      expect(content).toContain("http://www.w3.org/ns/odrl/2/Set");

      const firstAction = DummyDistribution.policy_actions[0];
      if (firstAction.policyActionType === "permission") {
        expect(content).toContain("odrl:permission");
      } else if (firstAction.policyActionType === "prohibition") {
        expect(content).toContain("odrl:prohibition");
      }

      expect(content).toContain("http://www.w3.org/ns/odrl/2/use");

      if (firstAction.policyConstraintType === "temporal") {
        expect(content).toContain("http://www.w3.org/ns/odrl/2/dateTime");
        expect(content).toContain("http://www.w3.org/ns/odrl/2/gteq");
        expect(content).toContain("http://www.w3.org/ns/odrl/2/lteq");
        if (firstAction.temporalRestrictionStart) {
          expect(content).toContain(firstAction.temporalRestrictionStart);
        }
        if (firstAction.temporalRestrictionEnd) {
          expect(content).toContain(firstAction.temporalRestrictionEnd);
        }
      } else if (firstAction.policyConstraintType === "purpose") {
        expect(content).toContain("http://www.w3.org/ns/odrl/2/purpose");
        if (firstAction.policyConstraintValue) {
          const duoCode = firstAction.policyConstraintValue.replace(":", "_");
          expect(content).toContain(duoCode);
        }
      } else if (firstAction.policyConstraintType === "spatial") {
        expect(content).toContain("dct:spatial");
      } else if (firstAction.policyConstraintType === "industry") {
        expect(content).toContain("http://www.w3.org/ns/odrl/2/industry");
      }
    }
    expect(content).toContain(DummyDistribution.access_urls[0]);
    expect(content).toContain(DummyDistribution.download_urls[0]);
    expect(content).toContain(DummyDistribution.compression_format);
    expect(content).toContain(DummyDistribution.distribution_spatial_resolution.toString());
    expect(content).toContain(DummyDistribution.distribution_temporal_resolution);
    expect(content).toContain(DummyDistribution.packaging_format);
    DummyDistribution.documentation.forEach((doc) => {
      expect(content).toContain(doc);
    });
    expect(content).toContain(DummyDistribution.linked_schemas[0]);
    expect(content).toContain(DummyDistribution.media_type);

    expect(content).toContain("<dcat:qualifiedRelation>");
    expect(content).toContain("<dcat:Relationship");
    expect(content).toContain("https://resourcecee.com");
    expect(content).toContain("<dct:relation>");
    expect(content).toContain('<dcat:Resource rdf:about="https://resourcecee.com">');

    expect(content).toContain("http://www.iana.org/assignments/relation/describedby");
    expect(content).toContain("<dcat:hadRole");

    expect(content).toContain("Test external resource description");
  }

  getCatalogueContent() {
    return readFileSync("./catalogue.rdf", { encoding: "utf8" });
  }
}
