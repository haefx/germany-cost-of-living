import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";

export interface ImportRowResult {
  row_number: number;
  status: "valid" | "duplicate" | "error";
  message: string;
  label: string | null;
  amount: string | null;
  entry_date: string | null;
}

export interface ImportSummary {
  imported: number;
  skipped_duplicates: number;
  errors: ImportRowResult[];
}

type Entity = "income" | "expenses";

export function usePreviewImport() {
  return useMutation({
    mutationFn: async ({ entity, file }: { entity: Entity; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.postForm<ImportRowResult[]>(`/api/import/${entity}/preview`, formData);
    },
  });
}

export function useCommitImport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ entity, file }: { entity: Entity; file: File }) => {
      const formData = new FormData();
      formData.append("file", file);
      return apiClient.postForm<ImportSummary>(`/api/import/${entity}/commit`, formData);
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: [variables.entity] });
    },
  });
}

function downloadBlob(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export async function downloadCsvExport(entity: Entity): Promise<void> {
  const csvText = await apiClient.get<string>(`/api/export/${entity}.csv`);
  downloadBlob(csvText, `${entity}.csv`, "text/csv");
}

export async function downloadAccountExport(): Promise<void> {
  const data = await apiClient.get<Record<string, unknown>>("/api/export/account");
  downloadBlob(JSON.stringify(data, null, 2), "account-export.json", "application/json");
}

export function useDeleteAccount() {
  return useMutation({
    mutationFn: () => apiClient.delete("/api/users/me"),
  });
}
