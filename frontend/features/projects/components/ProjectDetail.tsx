"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FolderKanban, Pencil, Trash2, X, Check } from "lucide-react";

import type { ProjectStatus } from "../types/project";
import { useProjectStore } from "../store/project.store";

const STATUS_STYLES: Record<ProjectStatus, string> = {
  active: "bg-green-100 text-green-700",
  draft: "bg-yellow-100 text-yellow-700",
  completed: "bg-blue-100 text-blue-700",
};

const STATUS_LABELS: Record<ProjectStatus, string> = {
  active: "Active",
  draft: "Draft",
  completed: "Completed",
};

const STATUS_OPTIONS: ProjectStatus[] = ["draft", "active", "completed"];

interface ProjectDetailProps {
  id: string;
}

export default function ProjectDetail({ id }: ProjectDetailProps) {
  const router = useRouter();

  const project = useProjectStore((state) => state.currentProject);
  const assets = useProjectStore((state) => state.currentProjectAssets);
  const isLoading = useProjectStore((state) => state.isLoadingCurrent);
  const isLoadingAssets = useProjectStore((state) => state.isLoadingAssets);
  const isSaving = useProjectStore((state) => state.isSaving);
  const isDeleting = useProjectStore((state) => state.isDeleting);
  const error = useProjectStore((state) => state.error);
  const fetchProjectById = useProjectStore((state) => state.fetchProjectById);
  const fetchProjectAssets = useProjectStore((state) => state.fetchProjectAssets);
  const editProject = useProjectStore((state) => state.editProject);
  const removeProject = useProjectStore((state) => state.removeProject);

  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    brand_voice: "",
    status: "draft" as ProjectStatus,
    status_auto: true,
  });

  useEffect(() => {
    fetchProjectById(id);
    fetchProjectAssets(id);
  }, [id, fetchProjectById, fetchProjectAssets]);

  function startEditing() {
    if (!project) return;
    setForm({
      name: project.name,
      description: project.description ?? "",
      brand_voice: project.brand_voice ?? "",
      status: project.status,
      status_auto: project.status_auto,
    });
    setIsEditing(true);
  }

  async function handleSave() {
    const ok = await editProject(id, {
      name: form.name,
      description: form.description || null,
      brand_voice: form.brand_voice || null,
      ...(form.status_auto ? { status_auto: true } : { status: form.status, status_auto: false }),
    });
    if (ok) setIsEditing(false);
  }

  async function handleDelete() {
    const ok = await removeProject(id);
    if (ok) router.push("/projects");
  }

  return (
    <main className="space-y-6">
      <Link
        href="/projects"
        className="flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Projects
      </Link>

      {isLoading && <p className="text-sm text-muted-foreground">Loading project...</p>}
      {error && !isLoading && <p className="text-sm text-red-500">{error}</p>}

      {!isLoading && project && (
        <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-accent">
                <FolderKanban className="h-6 w-6 text-blue-600" />
              </div>
              {!isEditing ? (
                <h1 className="text-2xl font-bold text-foreground">{project.name}</h1>
              ) : (
                <input
                  className="w-full max-w-sm rounded-lg border border-border bg-background px-3 py-2 text-xl font-bold text-foreground"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              )}
            </div>

            <div className="flex shrink-0 items-center gap-2">
              {!isEditing ? (
                <>
                  <span className={`flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[project.status]}`}>
                    {STATUS_LABELS[project.status]}
                    {project.status_auto && <span className="opacity-70">· Auto</span>}
                  </span>
                  <button
                    onClick={startEditing}
                    className="flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent"
                  >
                    <Pencil className="h-3.5 w-3.5" />
                    Edit
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="flex items-center gap-1 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Delete
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex items-center gap-1 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:opacity-90 disabled:opacity-50"
                  >
                    <Check className="h-3.5 w-3.5" />
                    {isSaving ? "Saving..." : "Save"}
                  </button>
                  <button
                    onClick={() => setIsEditing(false)}
                    disabled={isSaving}
                    className="flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-accent"
                  >
                    <X className="h-3.5 w-3.5" />
                    Cancel
                  </button>
                </>
              )}
            </div>
          </div>

          {!isEditing ? (
            <>
              <p className="mt-4 text-muted-foreground">
                {project.description || "No description provided."}
              </p>

              {project.brand_voice && (
                <div className="mt-6">
                  <h2 className="text-sm font-semibold text-foreground">Brand Voice</h2>
                  <p className="mt-1 text-sm text-muted-foreground">{project.brand_voice}</p>
                </div>
              )}
            </>
          ) : (
            <div className="mt-4 space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-semibold text-foreground">Status</label>
                  <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <input
                      type="checkbox"
                      checked={form.status_auto}
                      onChange={(e) => setForm({ ...form, status_auto: e.target.checked })}
                      className="h-3.5 w-3.5"
                    />
                    Auto (recommended)
                  </label>
                </div>
                <div className="mt-1 flex gap-2">
                  {STATUS_OPTIONS.map((s) => (
                    <button
                      key={s}
                      disabled={form.status_auto}
                      onClick={() => setForm({ ...form, status: s })}
                      className={`rounded-full px-3 py-1 text-xs font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${
                        form.status === s ? STATUS_STYLES[s] : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {STATUS_LABELS[s]}
                    </button>
                  ))}
                </div>
                {form.status_auto && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    System will move this from Draft to Active once you generate content in it.
                  </p>
                )}
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground">Description</label>
                <textarea
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                  rows={3}
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground">Brand Voice</label>
                <textarea
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                  rows={2}
                  value={form.brand_voice}
                  onChange={(e) => setForm({ ...form, brand_voice: e.target.value })}
                />
              </div>
            </div>
          )}

          <div className="mt-6 flex gap-6 text-xs text-muted-foreground">
            <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(project.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      )}

      {!isLoading && project && (
        <div>
          <h2 className="text-lg font-semibold text-foreground">Scripts & Videos in this Project</h2>

          {isLoadingAssets && <p className="mt-3 text-sm text-muted-foreground">Loading assets...</p>}

          {!isLoadingAssets && assets.length === 0 && (
            <div className="mt-3 rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground">
              Nothing generated in this project yet.
            </div>
          )}

          <div className="mt-3 space-y-3">
            {assets.map((asset) => (
              <div key={asset.id} className="rounded-xl border border-border bg-card p-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {asset.asset_type}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(asset.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="mt-1 text-sm text-foreground">{asset.prompt ?? "(no prompt)"}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-card p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-foreground">Delete this project?</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              This will permanently delete the project and everything inside it (scripts, videos,
              automations). This cannot be undone.
            </p>
            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
