import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";

async function postFormUrlEncoded(path: string, fields: Record<string, string>): Promise<void> {
  const body = new URLSearchParams(fields);
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  if (!response.ok) {
    let message = "Anmeldung fehlgeschlagen.";
    try {
      const data = await response.json();
      if (data?.detail === "LOGIN_BAD_CREDENTIALS") {
        message = "E-Mail oder Passwort ist falsch.";
      } else if (typeof data?.detail === "string") {
        message = data.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (fields: { email: string; password: string }) =>
      postFormUrlEncoded("/api/auth/login", { username: fields.email, password: fields.password }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.session }),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post("/api/auth/logout"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.session }),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (fields: { email: string; password: string }) =>
      apiClient.post("/api/auth/register", fields),
  });
}

export function useStartDemo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post("/api/demo/start"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.session }),
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email: string) => apiClient.post("/api/auth/forgot-password", { email }),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: (fields: { token: string; password: string }) =>
      apiClient.post("/api/auth/reset-password", fields),
  });
}
