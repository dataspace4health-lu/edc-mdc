import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type RequirePermissionProps = {
  children: ReactNode;
  permission?: string;
  permissions?: string[];
  feature?: string;
};

export default function RequirePermission(props: Readonly<RequirePermissionProps>) {
  const { children, permission, permissions, feature } = props;
  const { user } = useAuth();
  const userPermissions = user?.permissions || [];
  const featureEnabled = feature ? user?.feature_options?.[feature] === true : true;

  const hasPermission =
    permission !== undefined
      ? userPermissions.includes(permission)
      : permissions?.some((p) => userPermissions.includes(p));

  if (!hasPermission || !featureEnabled) {
    return <Navigate to='/unauthorised' replace />;
  }

  return <>{children}</>;
}
