import {
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  login as loginApi,
  register as registerApi,
  type LoginCredentials,
  type RegisterData,
} from "../api/auth";

import { AuthContext } from "./auth-context";

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<
    import("../api/auth").User | null
  >(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function restoreSession() {
      const token =
        localStorage.getItem("access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        setUser(currentUser);
      } catch {
        localStorage.removeItem(
          "access_token"
        );

        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  async function login(
    credentials: LoginCredentials
  ) {
    const tokenResponse =
      await loginApi(credentials);

    localStorage.setItem(
      "access_token",
      tokenResponse.access_token
    );

    try {
      const currentUser =
        await getCurrentUser();

      setUser(currentUser);
    } catch (error) {
      localStorage.removeItem(
        "access_token"
      );

      throw error;
    }
  }

  async function register(
    data: RegisterData
  ) {
    await registerApi(data);

    await login({
      email: data.email,
      password: data.password,
    });
  }

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated:
          user !== null,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}