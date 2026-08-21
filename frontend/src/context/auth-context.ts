import { createContext } from "react";

import type {
  LoginCredentials,
  RegisterData,
  User,
} from "../api/auth";

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (
    credentials: LoginCredentials
  ) => Promise<void>;
  register: (
    data: RegisterData
  ) => Promise<void>;
  logout: () => void;
}

export const AuthContext =
  createContext<AuthContextType | undefined>(
    undefined
  );