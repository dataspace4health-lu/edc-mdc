import { useRouteError, isRouteErrorResponse } from "react-router-dom";
import { AxiosError } from "axios";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { useAuth } from "../context/AuthContext";

function checkStatus(status?: number) {
  let message = "";
  switch (status) {
    case 404:
      message = "This page doesn't exist!";
      break;
    case 401:
      message = "You aren't logged-in";
      break;
    case 503:
      message = "Looks like our API is down";
      break;
    case 403:
      message = "You don't have permission to access this page";
      break;
    case 409:
      message =
        "The requested action cannot be completed due to the current state of the resource.";
      break;
    default:
      console.log("Unknown error");
  }
  return message;
}

interface ReactRouterError extends Error {
  response?: {
    status?: number;
  };
  status?: number;
}

export default function ErrorBoundary() {
  const { user } = useAuth();
  const error = useRouteError() as ReactRouterError | AxiosError;

  let message = "Something went wrong";

  if (isRouteErrorResponse(error) || error.response) {
    const status = error.response ? error.response.status : error.status;
    message = checkStatus(status);
  }

  console.error(error);

  return (
    <div className='flex flex-col h-screen'>
      <Navbar user={user} />
      <div className='flex-1 flex items-center justify-center p-3 flex-col'>
        {import.meta.env.VITE_ENV === "development" && error && error.message && (
          <div className='bg-warning p-4 text-white mb-3'>
            <p className='font-medium'>{error.message}</p>
            {error.stack && <pre className='mt-4 overflow-x-auto'>{error.stack}</pre>}
          </div>
        )}
        <div className='text-center w-full max-w-md text-lnds-color'>
          <h1 className='text-2xl md:text-3xl lg:text-4xl font-bold mb-4'>{message}</h1>
          <p>If you think this is a mistake, please contact support or try refreshing the page.</p>
        </div>
      </div>
      <Footer user={user} />
    </div>
  );
}
