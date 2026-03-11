import { useState, useEffect } from "react";
import { Card, CardHeading, useAlert } from "@lnds-lu/design-system";
import { BuildingOfficeIcon } from "@heroicons/react/24/solid";
import ContactForm from "./ContactForm";
import ContactList from "./ContactList";
import { ResourceContact, ResourceOrganisation } from "../../../types";
import Breadcrumb from "../../../components/Breadcrumb";
import { RightSidebar } from "../../../components/RightSidebar";
import { useLoaderData } from "react-router";
import { useAuth } from "../../../context/AuthContext";
import { usePageTitle } from "../../../hooks/usePageTitle";
import { appAlerts } from "../../../utils/appAlerts";

const OrganizationDetailPage = () => {
  const [contacts, setContacts] = useState<ResourceContact[]>([]);
  const [editableContact, setEditableContact] = useState<ResourceContact | null>(null);
  const [sidebarKey, setSidebarKey] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { setAlert } = useAlert();
  const organisation = (useLoaderData() as Awaited<ResourceOrganisation>) || [];
  const { user } = useAuth();

  usePageTitle(organisation?.name || "Organisation");

  const canEditContacts =
    user?.permissions.includes("contacts:edit") ||
    user?.permissions.includes("contacts:edit:organisation") ||
    user?.permissions.includes("organisations:edit:organisation") ||
    user?.permissions.includes("organisations:edit");

  useEffect(() => {
    setContacts(organisation.contacts || []);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAddContact = (contact: ResourceContact) => {
    setContacts((prev) => [...prev, contact]);
    setSidebarKey((prev) => prev + 1);
  };

  const handleUpdateContact = (contact: ResourceContact) => {
    setContacts((prev) => prev.map((c) => (c.id === contact.id ? contact : c)));
    setEditableContact(null);
    setSidebarKey((prev) => prev + 1);
  };

  const handleDeleteContact = (contactId: number) => {
    setContacts((prev) => prev.filter((c) => c.id !== contactId));
    setSidebarKey((prev) => prev + 1);
  };

  const handleDeprecateContact = (contactId: number) => {
    const contact = contacts.find((c) => c.id === contactId);
    setContacts((prev) =>
      prev.map((c) => (c.id === contactId ? { ...c, is_deprecated: !c.is_deprecated } : c)),
    );

    const alertMsg = contact?.is_deprecated
      ? "Contact successfully restored"
      : "Contact successfully deprecated";
    setAlert(appAlerts.alertMessageAsSuccess(alertMsg));
    setSidebarKey((prev) => prev + 1);
  };

  return (
    <div className='flex relative min-h-screen'>
      <div className='flex-1 flex justify-center transition-all duration-300 ease-in-out'>
        <div className='my-6 mx-6 w-full max-w-2xl lg:max-w-4xl md:mx-auto'>
          <Breadcrumb
            firstLevel='Organisations'
            firstLevelLink='/organisations'
            location={organisation.name}
          />
          <Card className='p-4 md:p-8'>
            <CardHeading label={organisation.name} Icon={BuildingOfficeIcon} className='flex' />
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <div>
                <h3 className='label-lnds-color text-sm'>Type</h3>
                <p className='text-lnds-color'>{organisation.type || "Not specified"}</p>
              </div>
              <div>
                <h3 className='label-lnds-color text-sm'>Email</h3>
                <p className='text-lnds-color'>{organisation.email || "Not specified"}</p>
              </div>
              {user?.feature_options?.enable_multi_tenants && (
                <>
                  <div>
                    <h3 className='label-lnds-color text-sm'>Category</h3>
                    <p className='text-lnds-color'>
                      {organisation.category === "EP"
                        ? "EP (Entité publique / Public entity)"
                        : organisation.category === "OSP"
                          ? "OSP (Organisme du secteur public / Public sector body)"
                          : "Not specified"}
                    </p>
                  </div>
                  <div>
                    <h3 className='label-lnds-color text-sm'>Accessible within CTIE</h3>
                    <p className='text-lnds-color'>
                      {organisation.accessible_within_ctie === true
                        ? "Yes"
                        : organisation.accessible_within_ctie === false
                          ? "No"
                          : "Not specified"}
                    </p>
                  </div>
                </>
              )}
            </div>
          </Card>
          <Card className='mt-4 p-4 md:p-8'>
            <div className='heading-lnds-color text-lg my-4'>Contacts</div>
            {canEditContacts && !organisation.is_deprecated && (
              <ContactForm
                organisationId={organisation.id}
                onAddContact={handleAddContact}
                onUpdateContact={handleUpdateContact}
                clearContact={() => setEditableContact(null)}
                contact={editableContact}
              />
            )}
            <ContactList
              organisationId={organisation.id}
              contacts={contacts}
              setEditableContact={setEditableContact}
              canEditContacts={canEditContacts || false}
              onDeleteContact={handleDeleteContact}
              onDeprecateContact={handleDeprecateContact}
            />
          </Card>
        </div>
      </div>
      <div
        className={`transition-all duration-300 ease-in-out ${
          isSidebarOpen ? "w-[20rem]" : "w-0"
        } overflow-hidden`}
      >
        {organisation && (
          <RightSidebar
            refreshTrigger={sidebarKey}
            entityId={organisation.id}
            entityType='organisation'
            className='border-l border-lnds-color'
            defaultIsOpen={false}
            onSidebarToggle={(isOpen: boolean) => setIsSidebarOpen(isOpen)}
          />
        )}
      </div>
    </div>
  );
};

export default OrganizationDetailPage;
