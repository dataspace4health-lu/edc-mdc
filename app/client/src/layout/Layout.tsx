import { Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { LNDSLoader } from "../components/LNDSLoader";
import { usePageTitle } from "../hooks/usePageTitle";

export default function Layout() {
  const { isLoading, user } = useAuth();

  usePageTitle();

  if (isLoading) {
    return (
      <div className='flex items-center justify-center min-h-[500px]'>
        <LNDSLoader />
      </div>
    );
  }

  return (
    <div className='flex flex-col h-screen'>
      <Navbar user={user} />
      <div className='flex-1 pt-16 overflow-x-hidden lg:overflow-x-visible'>
        <Outlet />
      </div>
      <Footer user={user} />
    </div>
  );
}
