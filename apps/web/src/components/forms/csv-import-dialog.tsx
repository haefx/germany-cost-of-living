"use client";

import { Upload } from "lucide-react";
import { useTranslations } from "next-intl";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  useCommitImport,
  usePreviewImport,
  type ImportRowResult,
  type ImportSummary,
} from "@/hooks/use-export";
import { cn } from "@/lib/utils";

const ROW_STATUS_STYLES: Record<ImportRowResult["status"], string> = {
  valid: "text-[var(--color-good-text)]",
  duplicate: "text-[#7a5200]",
  error: "text-[var(--color-critical)]",
};

export function CsvImportDialog({ entity }: { entity: "income" | "expenses" }) {
  const t = useTranslations("expenses");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [previewRows, setPreviewRows] = useState<ImportRowResult[] | null>(null);
  const [summary, setSummary] = useState<ImportSummary | null>(null);

  const preview = usePreviewImport();
  const commit = useCommitImport();

  function reset() {
    setFile(null);
    setPreviewRows(null);
    setSummary(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function handlePreview() {
    if (!file) return;
    const rows = await preview.mutateAsync({ entity, file });
    setPreviewRows(rows);
    setSummary(null);
  }

  async function handleCommit() {
    if (!file) return;
    const result = await commit.mutateAsync({ entity, file });
    setSummary(result);
    setPreviewRows(null);
  }

  const validCount = previewRows?.filter((row) => row.status === "valid").length ?? 0;

  return (
    <Dialog
      open={open}
      onOpenChange={(nextOpen) => {
        setOpen(nextOpen);
        if (!nextOpen) reset();
      }}
    >
      <DialogTrigger asChild>
        <Button variant="secondary">
          <Upload className="h-4 w-4" aria-hidden="true" />
          {t("importTitle")}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("importTitle")}</DialogTitle>
          <DialogDescription>{t("importDescription")}</DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          <div>
            <label
              htmlFor={`csv-file-${entity}`}
              className="mb-1.5 block text-sm font-medium text-[var(--color-ink)]"
            >
              {t("importSelectFile")}
            </label>
            <input
              ref={fileInputRef}
              id={`csv-file-${entity}`}
              type="file"
              accept=".csv,text/csv"
              className="block w-full text-sm text-[var(--color-ink-secondary)] file:mr-3 file:rounded-md file:border-0 file:bg-[var(--color-page)] file:px-3 file:py-2 file:text-sm file:font-medium"
              onChange={(event) => {
                setFile(event.target.files?.[0] ?? null);
                setPreviewRows(null);
                setSummary(null);
              }}
            />
          </div>

          {previewRows ? (
            <div className="max-h-56 overflow-y-auto rounded-md border border-[var(--color-border)]">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-[var(--color-page)]">
                  <tr className="text-left text-[var(--color-ink-muted)]">
                    <th scope="col" className="px-3 py-2 font-medium">Zeile</th>
                    <th scope="col" className="px-3 py-2 font-medium">Status</th>
                    <th scope="col" className="px-3 py-2 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {previewRows.map((row) => (
                    <tr key={row.row_number} className="border-t border-[var(--color-gridline)]">
                      <td className="px-3 py-1.5 tabular-nums">{row.row_number}</td>
                      <td className={cn("px-3 py-1.5 font-medium", ROW_STATUS_STYLES[row.status])}>
                        {row.status}
                      </td>
                      <td className="px-3 py-1.5 text-[var(--color-ink-secondary)]">
                        {row.label ?? ""} {row.status !== "valid" ? `– ${row.message}` : ""}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}

          {summary ? (
            <div role="status" className="rounded-md bg-[var(--color-page)] p-3 text-sm">
              <p className="font-medium text-[var(--color-good-text)]">
                {summary.imported} Einträge importiert
              </p>
              {summary.skipped_duplicates > 0 ? (
                <p className="text-[var(--color-ink-secondary)]">
                  {summary.skipped_duplicates} Duplikate übersprungen
                </p>
              ) : null}
              {summary.errors.length > 0 ? (
                <p className="text-[var(--color-critical)]">
                  {summary.errors.length} fehlerhafte Zeilen ignoriert
                </p>
              ) : null}
            </div>
          ) : null}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="secondary"
            onClick={handlePreview}
            disabled={!file || preview.isPending}
          >
            {t("importPreview")}
          </Button>
          <Button
            type="button"
            onClick={handleCommit}
            disabled={!file || commit.isPending || (previewRows !== null && validCount === 0)}
          >
            {t("importCommit")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
