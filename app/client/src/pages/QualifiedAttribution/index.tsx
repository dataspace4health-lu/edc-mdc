import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useAlert } from "@lnds-lu/design-system";
import { loginUrl } from "../../utils/authUrls";
import { useOutletContext, useRevalidator } from "react-router-dom";
import QualifiedAttributionCard from "./QualifiedAttributionCard";
import QualifiedAttributionForm from "./QualifiedAtributionForm";
import { BuildingOfficeIcon } from "@heroicons/react/24/solid";
import { ResourceDatasetType, ResourceQualifiedAttribution } from "../../types";
import { Card } from "@lnds-lu/design-system";
import EmptyScreen from "../../components/EmptyScreen";
import client from "../../zodiosClient/client";
import { usePageTitle } from "../../hooks/usePageTitle";
import { appAlerts } from "../../utils/appAlerts";

export default function QualifiedAttributions() {
  const { isLoading, user } = useAuth();
  const { setAlert } = useAlert();
  const revalidator = useRevalidator();
  const [attributions, setAttributions] = useState<ResourceQualifiedAttribution[]>([]);
  const [current, setCurrent] = useState<ResourceQualifiedAttribution | null>(null);
  const [organisations, setOrganisations] = useState<{ value: string; label: string }[]>([]);

  if (!isLoading && !user) {
    window.location.href = loginUrl();
  }

  const { dataset, triggerActivityLogRefresh } = useOutletContext() as {
    dataset: ResourceDatasetType;
    triggerActivityLogRefresh: () => void;
  };

  usePageTitle(`${dataset?.title || "Dataset"} - Qualified Attributions`);

  useEffect(() => {
    if (dataset?.qualified_attributions) {
      setAttributions(Array.from(dataset.qualified_attributions));
    }
  }, [dataset]);

  useEffect(() => {
    const fetchOrganisations = async () => {
      try {
        const orgs = await client.get_organisations_api_v1_organisations_get({
          withCredentials: true,
        });

        const filteredOrgs = (orgs || []).filter((o) => !o.is_deprecated);

        setOrganisations(
          filteredOrgs.map((o) => ({
            value: String(o.id),
            label: o.name,
          })),
        );
      } catch (error) {
        setAlert(appAlerts.organisationLoadFailed());
      }
    };

    fetchOrganisations();
  }, [setAlert]);

  const handleEdit = (attribution: ResourceQualifiedAttribution) => {
    setCurrent(attribution);
  };

  const handleAttributionUpdated = () => {
    revalidator.revalidate();
  };

  return (
    <div className='flex flex-col w-full'>
      <div className='w-full max-w-3xl self-center'>
        <QualifiedAttributionForm
          datasetId={dataset.id}
          current={current}
          setCurrent={setCurrent}
          organisations={organisations}
          onAttributionUpdated={handleAttributionUpdated}
          triggerActivityLogRefresh={triggerActivityLogRefresh}
        />

        <Card className='mt-4 p-0 flex-grow overflow-y-auto'>
          {attributions.length > 0 ? (
            <div>
              {attributions.map((attribution) => (
                <QualifiedAttributionCard
                  key={attribution.id}
                  datasetId={dataset.id}
                  attribution={attribution}
                  current={current}
                  onEdit={handleEdit}
                />
              ))}
            </div>
          ) : (
            <div className='p-4'>
              <EmptyScreen
                message='No qualified attributions available'
                Icon={BuildingOfficeIcon}
              />
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
