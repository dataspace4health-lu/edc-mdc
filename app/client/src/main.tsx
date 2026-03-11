import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import "@lnds-lu/design-system/tailwind.css";
import Layout from "./layout/Layout";
import { AuthProvider } from "./context/AuthContext";
import { AuthenticSourceLabelsProvider } from "./context/AuthenticSourceLabelsContext";
import { LeftSidebarProvider } from "./context/LeftSidebarContext";
import { DatasetsProvider } from "./context/DatasetsContext";
import { UIConfigProvider } from "./context/UIConfigContext";
import { AlertToastProvider } from "@lnds-lu/design-system";
import { RouterProvider, createBrowserRouter, LoaderFunctionArgs } from "react-router-dom";
import DatasetForm from "./pages/DatasetForm/DatasetForm";
import Relations from "./pages/Relations";
import QualifiedAttributions from "./pages/QualifiedAttribution";
import { datasetLoader } from "./pages/datasets/[id]/loader";
import DatasetLayout from "./pages/datasets/[id]/layout";
import { datasetFormLoader } from "./pages/DatasetForm/loader";
import { datasetFormAction } from "./pages/DatasetForm/actions";
import { relationsFormAction } from "./pages/Relations/actions";
import DatasetList from "./pages/DatasetList/DatasetList";
import { datasetListLoader } from "./pages/DatasetList/loader";
import ErrorBoundary from "./components/ErrorBoundary";
import { DataDictionaryPage } from "./pages/DataDictionary";
import { DistributionsPage } from "./pages/distributions";
import { OrganisationList } from "./pages/OrganisationList";
import { organisationListLoader } from "./pages/OrganisationList/loader";
import OrganizationDetailPage from "./pages/organisations/[id]";
import { organisationLoader } from "./pages/organisations/[id]/loader";
import FormFields from "./pages/form_fields";
import DataServiceManagement from "./pages/data_services";
import DataServiceLoader from "./pages/data_services/loader";
import AuthenticSourceManagement from "./pages/authentic_sources";
import Unauthorised from "./pages/unauthorised";
import FirstTimeLogin from "./pages/first_time_login";
import CtieOnlyAccess from "./pages/ctie_only_access";
import UserList from "./pages/users";
import { usersLoader } from "./pages/users/loader";
import RolesInformation from "./pages/roles";
import { rolesLoader } from "./pages/roles/loader";
import ValidatorPage from "./pages/excel_validator";
import BulkUploadPage from "./pages/bulk_upload";
import FrontOfficeDirectory from "./pages/front_office_directory";
import RequirePermission from "./components/RequirePermission";
import { UnsavedProvider } from "./context/UnSavedChangesContext";
import RdfImportPage from "./pages/rdf_import";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    errorElement: <ErrorBoundary />,
    children: [
      {
        path: "/",
        loader: datasetListLoader,
        element: (
          <DatasetsProvider>
            <DatasetList />
          </DatasetsProvider>
        ),
      },
      {
        path: "datasets/:datasetId",
        element: <DatasetLayout />,
        loader: async ({ params }: LoaderFunctionArgs) => {
          const datasetId = params["datasetId"];
          if (typeof datasetId === "string") {
            return datasetLoader(parseInt(datasetId));
          }
          throw new Error("Dataset ID is required and must be a string.");
        },
        children: [
          {
            path: "relations",
            action: relationsFormAction,
            shouldRevalidate: () => false,
            element: <Relations />,
          },
          {
            path: "qualified-attributions",
            shouldRevalidate: () => false,
            element: <QualifiedAttributions />,
          },
          {
            path: "edit",
            action: datasetFormAction,
            loader: datasetFormLoader,
            shouldRevalidate: () => false,
            element: <DatasetForm />,
          },
          {
            path: "dictionaries",
            element: <DataDictionaryPage />,
            loader: ({ params }: LoaderFunctionArgs) => {
              const datasetId = params["datasetId"];
              if (typeof datasetId === "string") {
                return { datasetId: parseInt(datasetId) };
              }
              throw new Error("Dataset ID is required and must be a string.");
            },
          },
          {
            path: "distributions",
            element: <DistributionsPage />,
            loader: async ({ params }: LoaderFunctionArgs) => {
              const datasetId = params["datasetId"];
              if (typeof datasetId === "string") {
                const formFields = await datasetFormLoader();
                return {
                  datasetId: parseInt(datasetId),
                  formFields,
                };
              }
              throw new Error("Dataset ID is required and must be a string.");
            },
          },
        ],
      },
      {
        path: "datasetform",
        action: datasetFormAction,
        loader: async () => datasetFormLoader(),
        shouldRevalidate: () => false,
        element: <DatasetForm />,
      },
      {
        path: "organisations",
        loader: organisationListLoader,
        element: (
          <RequirePermission
            permissions={[
              "organisations:edit",
              "organisations:edit:organisation",
              "contacts:edit",
              "contacts:edit:organisation",
            ]}
          >
            <OrganisationList />
          </RequirePermission>
        ),
      },
      {
        path: "organisations/:id",
        element: <OrganizationDetailPage />,
        loader: async ({ params }: LoaderFunctionArgs) => {
          const id = params["id"];
          if (typeof id === "string") {
            return organisationLoader(parseInt(id));
          }
        },
      },
      {
        path: "keywords",
        element: <FormFields />,
      },
      {
        path: "applicable_legislations",
        element: <FormFields />,
      },
      {
        path: "data_services",
        loader: DataServiceLoader,
        element: <DataServiceManagement />,
      },
      {
        path: "users",
        loader: usersLoader,
        element: (
          <RequirePermission
            permissions={["roles:manage", "roles:manage:organisation"]}
            feature='enable_multi_tenants'
          >
            <UserList />
          </RequirePermission>
        ),
      },
      {
        path: "roles",
        loader: rolesLoader,
        element: <RolesInformation />,
      },
      {
        path: "/datasets/bulk-upload",
        element: <BulkUploadPage />,
      },
      {
        path: "/datasets/import-rdf",
        element: (
          <RequirePermission permissions={["datasets:edit:draft"]}>
            <RdfImportPage />
          </RequirePermission>
        ),
      },
      {
        path: "authentic_sources",
        element: <AuthenticSourceManagement />,
      },
      {
        path: "admin/front-office-directory",
        element: (
          <RequirePermission permissions={["datasets:status-change:publish"]}>
            <FrontOfficeDirectory />
          </RequirePermission>
        ),
      },
    ],
  },
  {
    path: "/excel-validator",
    element: <ValidatorPage />,
  },
  {
    path: "/first-time-login",
    element: <FirstTimeLogin />,
  },
  {
    path: "/unauthorised",
    element: <Unauthorised />,
  },
  {
    path: "/ctie-only-access",
    element: <CtieOnlyAccess />,
  },
], { basename: import.meta.env.VITE_BASE_URL || "/" });

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <UIConfigProvider>
      <AuthProvider>
        <AuthenticSourceLabelsProvider>
          <AlertToastProvider>
            <LeftSidebarProvider>
              <UnsavedProvider>
                <RouterProvider router={router} />
              </UnsavedProvider>
            </LeftSidebarProvider>
          </AlertToastProvider>
        </AuthenticSourceLabelsProvider>
      </AuthProvider>
    </UIConfigProvider>
  </React.StrictMode>,
);
