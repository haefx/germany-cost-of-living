import { useQuery } from "@tanstack/react-query";

import { ApiError, apiClient } from "@/lib/api-client";
import type { User } from "@/lib/api-types";
import { queryKeys } from "@/lib/query-keys";

export function useSession() {
  return useQuery<User | null>({
    queryKey: queryKeys.session,
    queryFn: async () => {
      try {
        return await apiClient.get<User>("/api/users/me");
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) {
          return null;
        }
        throw error;
      }
    },
    retry: false,
  });
}
