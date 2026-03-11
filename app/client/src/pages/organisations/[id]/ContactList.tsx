import { useState } from "react";
import { ResourceContact } from "../../../types";
import { UsersIcon, PencilIcon } from "@heroicons/react/24/solid";
import { useAlert } from "@lnds-lu/design-system";
import EmptyScreen from "../../../components/EmptyScreen";
import client from "../../../zodiosClient/client";
import { isAxiosError } from "axios";
import SearchBar from "../../../components/SearchBar";
import ConfirmableActionButton from "../../../components/ConfirmableActionButton";
import { Button } from "@lnds-lu/design-system";
import Tooltip from "../../../components/Tooltip";
import { DeprecatedTag, deprecatedBgClasses } from "../../../components/DeprecatedTag";
import { appAlerts } from "../../../utils/appAlerts";

const ContactList = ({
  organisationId,
  contacts,
  setEditableContact,
  canEditContacts,
  onDeleteContact,
  onDeprecateContact,
}: {
  organisationId: number;
  contacts: ResourceContact[];
  setEditableContact: (contact: ResourceContact) => void;
  canEditContacts: boolean;
  onDeleteContact: (contactId: number) => void;
  onDeprecateContact: (contactId: number) => void;
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const filteredContacts = contacts.filter(
    (contact) =>
      contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.role?.toLowerCase().includes(searchTerm.toLowerCase()),
  );
  const { setAlert } = useAlert();

  const handleDelete = async (contactId: number) => {
    try {
      await client.delete_contact_api_v1_organisations__organisation_id__contacts__contact_id__delete(
        undefined,
        {
          params: { organisation_id: organisationId, contact_id: contactId },
          withCredentials: true,
        },
      );

      setAlert(appAlerts.contactDeleted());
      onDeleteContact(contactId);
    } catch (error: unknown) {
      console.log("Error deleting contact:", error);
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.serverErrorTryLater().message,
          ),
        );
      } else {
        setAlert(appAlerts.unknownError());
      }
    }
  };

  const handleDeprecate = async (contactId: number) => {
    try {
      await client.change_deprecation_status_api_v1_organisations__organisation_id__contacts__contact_id__toggle_deprecation_patch(
        undefined,
        {
          params: { organisation_id: organisationId, contact_id: contactId },
          withCredentials: true,
        },
      );
      onDeprecateContact(contactId);
    } catch (error: unknown) {
      console.error("Error deprecating contact:", error);
      if (isAxiosError(error)) {
        setAlert(
          appAlerts.genericValidationError(
            error.response?.data?.detail || appAlerts.serverErrorTryLater().message,
          ),
        );
      } else {
        setAlert(appAlerts.unknownError());
      }
    }
  };

  return (
    <div className='overflow-x-auto mt-4'>
      <SearchBar
        searchTerm={searchTerm}
        onSearch={setSearchTerm}
        placeholder='Search Contacts...'
      />
      <div className='flex-grow overflow-y-auto' style={{ height: "calc(40vh)" }}>
        <table className={`min-w-full divide-y divide-gray-200 dark:divide-gray-700`}>
          <thead className='bg-gray-100 dark:bg-gray-700'>
            <tr>
              <th className='px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-200 uppercase tracking-wider'>
                Name
              </th>
              <th className='px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-200 uppercase tracking-wider'>
                Email
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-200 uppercase tracking-wider'>
                Role
              </th>
              <th className='px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-200 uppercase tracking-wider'>
                Actions
              </th>
            </tr>
          </thead>
          <tbody className='bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700'>
            {contacts.length > 0 ? (
              filteredContacts.map((contact) => (
                <tr key={contact.id} className={contact.is_deprecated ? deprecatedBgClasses : ""}>
                  <td className='px-3 py-4 whitespace-nowrap'>
                    <span className='text-gray-700 dark:text-gray-200'>{contact.name}</span>
                    {contact.is_deprecated && <DeprecatedTag />}
                  </td>
                  <td className='px-3 py-4 whitespace-nowrap'>
                    <span className='text-gray-700 dark:text-gray-200'>{contact.email}</span>
                  </td>
                  <td className='px-3 py-4 whitespace-nowrap'>
                    <span className='text-gray-700 dark:text-gray-200'>{contact.role}</span>
                  </td>
                  <td className='px-3 py-4 whitespace-nowrap'>
                    {canEditContacts && !contact.is_deprecated ? (
                      <div className='flex gap-2 items-center'>
                        <Tooltip text='Edit Contact'>
                          <Button
                            btnType='transparent'
                            onClick={() => setEditableContact(contact)}
                            className='p-2 w-10 h-10 rounded-md flex items-center justify-center icon-lnds-color cursor-pointer'
                            Icon={PencilIcon}
                          />
                        </Tooltip>
                        <ConfirmableActionButton
                          action='delete'
                          onConfirm={() => handleDelete(contact.id)}
                        />
                        <ConfirmableActionButton
                          action='deprecate'
                          onConfirm={() => handleDeprecate(contact.id)}
                        />
                      </div>
                    ) : (
                      contact.is_deprecated &&
                      canEditContacts && (
                        <div className='flex gap-2 items-center text-lnds-light-gray'>
                          <ConfirmableActionButton
                            action='restore'
                            onConfirm={() => handleDeprecate(contact.id)}
                          />
                        </div>
                      )
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className='p-4'>
                  <EmptyScreen message='No Contacts added' Icon={UsersIcon} />
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ContactList;
