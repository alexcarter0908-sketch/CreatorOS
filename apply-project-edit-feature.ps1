$enc = New-Object System.Text.UTF8Encoding($false)

$content = @'
export type ProjectStatus = "draft" | "active" | "completed";

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  brand_voice: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectPayload {
  name: string;
  description?: string;
  brand_voice?: string;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  brand_voice?: string;
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/types/project.ts", $content, $enc)

$content = @'
import apiClient from "@/lib/api/client";
import type { CreateProjectPayload, Project, UpdateProjectPayload } from "../types/project";

export async function listProjects(): Promise<Project[]> {
  const { data } = await apiClient.get<Project[]>("/api/v1/projects");
  return data;
}

export async function getProject(id: string): Promise<Project> {
  const { data } = await apiClient.get<Project>(`/api/v1/projects/${id}`);
  return data;
}

export async function createProject(
  payload: CreateProjectPayload
): Promise<Project> {
  const { data } = await apiClient.post<Project>("/api/v1/projects", payload);
  return data;
}

export async function updateProject(
  id: string,
  payload: UpdateProjectPayload
): Promise<Project> {
  const { data } = await apiClient.patch<Project>(`/api/v1/projects/${id}`, payload);
  return data;
}

export async function deleteProject(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/projects/${id}`);
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/services/project.service.ts", $content, $enc)

$content = @'
"use client";

import { create } from "zustand";

import type {
  CreateProjectPayload,
  Project,
  UpdateProjectPayload,
} from "../types/project";
import {
  createProject as createProjectService,
  deleteProject as deleteProjectService,
  getProject,
  listProjects,
  updateProject as updateProjectService,
} from "../services/project.service";

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  isLoading: boolean;
  isLoadingCurrent: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  fetchProjectById: (id: string) => Promise<void>;
  addProject: (payload: CreateProjectPayload) => Promise<void>;
  updateProject: (id: string, payload: UpdateProjectPayload) => Promise<Project>;
  removeProject: (id: string) => Promise<void>;
  clearCurrentProject: () => void;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  isLoading: false,
  isLoadingCurrent: false,
  isUpdating: false,
  isDeleting: false,
  error: null,

  async fetchProjects() {
    set({ isLoading: true, error: null });

    try {
      const projects = await listProjects();
      set({ projects, isLoading: false });
    } catch {
      set({ isLoading: false, error: "Failed to load projects." });
    }
  },

  async fetchProjectById(id) {
    set({ isLoadingCurrent: true, error: null });

    try {
      const project = await getProject(id);
      set({ currentProject: project, isLoadingCurrent: false });
    } catch {
      set({ isLoadingCurrent: false, error: "Failed to load project." });
    }
  },

  async addProject(payload) {
    const project = await createProjectService(payload);
    set({ projects: [project, ...get().projects] });
  },

  async updateProject(id, payload) {
    set({ isUpdating: true, error: null });

    try {
      const updated = await updateProjectService(id, payload);

      set((state) => ({
        isUpdating: false,
        projects: state.projects.map((project) =>
          project.id === id ? updated : project
        ),
        currentProject:
          state.currentProject?.id === id ? updated : state.currentProject,
      }));

      return updated;
    } catch (err) {
      set({ isUpdating: false, error: "Failed to update project." });
      throw err;
    }
  },

  async removeProject(id) {
    set({ isDeleting: true, error: null });

    try {
      await deleteProjectService(id);

      set((state) => ({
        isDeleting: false,
        projects: state.projects.filter((project) => project.id !== id),
        currentProject:
          state.currentProject?.id === id ? null : state.currentProject,
      }));
    } catch (err) {
      set({ isDeleting: false, error: "Failed to delete project." });
      throw err;
    }
  },

  clearCurrentProject() {
    set({ currentProject: null, error: null });
  },
}));
'@
[System.IO.File]::WriteAllText("frontend/features/projects/store/project.store.ts", $content, $enc)

$content = @'
"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

import { useProjectStore } from "../store/project.store";
import type { Project, ProjectStatus } from "../types/project";

interface Props {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const STATUS_OPTIONS: { value: ProjectStatus; label: string }[] = [
  { value: "draft", label: "Draft" },
  { value: "active", label: "Active" },
  { value: "completed", label: "Completed" },
];

export default function EditProjectDialog({ project, open, onOpenChange }: Props) {
  const updateProject = useProjectStore((state) => state.updateProject);
  const isUpdating = useProjectStore((state) => state.isUpdating);

  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description ?? "");
  const [brandVoice, setBrandVoice] = useState(project.brand_voice ?? "");
  const [status, setStatus] = useState<ProjectStatus>(project.status);

  // Re-sync form fields whenever a different project is opened for editing.
  useEffect(() => {
    if (open) {
      setName(project.name);
      setDescription(project.description ?? "");
      setBrandVoice(project.brand_voice ?? "");
      setStatus(project.status);
    }
  }, [open, project]);

  async function handleSave() {
    if (!name.trim()) {
      toast.error("Project name is required.");
      return;
    }

    try {
      await updateProject(project.id, {
        name: name.trim(),
        description: description.trim(),
        brand_voice: brandVoice.trim(),
        status,
      });

      toast.success("Project updated.");
      onOpenChange(false);
    } catch {
      toast.error("Failed to update project.");
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Project</DialogTitle>
        </DialogHeader>

        <div className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="edit-project-name">Project Name</Label>
            <Input
              id="edit-project-name"
              placeholder="Project Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-project-description">Description</Label>
            <Textarea
              id="edit-project-description"
              placeholder="Project Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-project-brand-voice">Brand Voice</Label>
            <Textarea
              id="edit-project-brand-voice"
              placeholder="Brand Voice (optional) - e.g. casual and friendly, always use emojis, no formal language"
              value={brandVoice}
              onChange={(e) => setBrandVoice(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-project-status">Status</Label>
            <select
              id="edit-project-status"
              value={status}
              onChange={(e) => setStatus(e.target.value as ProjectStatus)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <Button className="w-full" onClick={handleSave} disabled={isUpdating}>
            {isUpdating ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/components/EditProjectDialog.tsx", $content, $enc)

$content = @'
"use client";

import { useState } from "react";
import { toast } from "sonner";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

import { useProjectStore } from "../store/project.store";
import type { Project } from "../types/project";

interface Props {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  // Called after the project has been deleted successfully.
  // Useful for e.g. redirecting away from a project detail page.
  onDeleted?: () => void;
}

export default function DeleteProjectDialog({
  project,
  open,
  onOpenChange,
  onDeleted,
}: Props) {
  const removeProject = useProjectStore((state) => state.removeProject);
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    setIsDeleting(true);

    try {
      await removeProject(project.id);
      toast.success("Project deleted.");
      onOpenChange(false);
      onDeleted?.();
    } catch {
      toast.error("Failed to delete project.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete Project</DialogTitle>
        </DialogHeader>

        <p className="text-sm text-muted-foreground">
          Are you sure you want to delete <span className="font-semibold text-foreground">{project.name}</span>?
          This action cannot be undone.
        </p>

        <div className="flex justify-end gap-3 pt-2">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/components/DeleteProjectDialog.tsx", $content, $enc)

$content = @'
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, FolderKanban, Pencil, Trash2 } from "lucide-react";

import type { ProjectStatus } from "../types/project";
import { useProjectStore } from "../store/project.store";
import EditProjectDialog from "./EditProjectDialog";
import DeleteProjectDialog from "./DeleteProjectDialog";
import { Button } from "@/components/ui/button";

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

interface ProjectDetailProps {
  id: string;
}

export default function ProjectDetail({ id }: ProjectDetailProps) {
  const router = useRouter();

  const project = useProjectStore((state) => state.currentProject);
  const isLoading = useProjectStore((state) => state.isLoadingCurrent);
  const error = useProjectStore((state) => state.error);
  const fetchProjectById = useProjectStore((state) => state.fetchProjectById);
  const clearCurrentProject = useProjectStore((state) => state.clearCurrentProject);

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  useEffect(() => {
    fetchProjectById(id);

    // Avoid showing a stale project from a previous visit while this one loads.
    return () => clearCurrentProject();
  }, [id, fetchProjectById, clearCurrentProject]);

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

      {!isLoading && !error && project && (
        <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent">
                <FolderKanban className="h-6 w-6 text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold text-foreground">{project.name}</h1>
            </div>

            <div className="flex items-center gap-2">
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[project.status]}`}>
                {STATUS_LABELS[project.status]}
              </span>

              <Button
                variant="outline"
                size="icon"
                aria-label="Edit project"
                onClick={() => setIsEditOpen(true)}
              >
                <Pencil className="h-4 w-4" />
              </Button>

              <Button
                variant="destructive"
                size="icon"
                aria-label="Delete project"
                onClick={() => setIsDeleteOpen(true)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <p className="mt-4 text-muted-foreground">
            {project.description || "No description provided."}
          </p>

          {project.brand_voice && (
            <div className="mt-6">
              <h2 className="text-sm font-semibold text-foreground">Brand Voice</h2>
              <p className="mt-1 text-sm text-muted-foreground">{project.brand_voice}</p>
            </div>
          )}

          <div className="mt-6 flex gap-6 text-xs text-muted-foreground">
            <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(project.updated_at).toLocaleDateString()}</span>
          </div>

          <EditProjectDialog
            project={project}
            open={isEditOpen}
            onOpenChange={setIsEditOpen}
          />

          <DeleteProjectDialog
            project={project}
            open={isDeleteOpen}
            onOpenChange={setIsDeleteOpen}
            onDeleted={() => router.push("/projects")}
          />
        </div>
      )}
    </main>
  );
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/components/ProjectDetail.tsx", $content, $enc)

$content = @'
"use client";

import { useState } from "react";
import Link from "next/link";
import { FolderKanban, Pencil, Trash2 } from "lucide-react";

import type { Project, ProjectStatus } from "../types/project";
import { Button } from "@/components/ui/button";
import EditProjectDialog from "./EditProjectDialog";
import DeleteProjectDialog from "./DeleteProjectDialog";

interface ProjectCardProps {
  project: Project;
}

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

export default function ProjectCard({ project }: ProjectCardProps) {
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  // Card actions sit inside a <Link>, so clicks on them must not trigger navigation.
  function stopNavigation(e: React.MouseEvent, action: () => void) {
    e.preventDefault();
    e.stopPropagation();
    action();
  }

  return (
    <div className="group relative rounded-2xl border border-border bg-card shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg">
      <Link href={`/projects/${project.id}`} className="block p-6">
        <div className="flex items-center justify-between">
          <FolderKanban className="h-8 w-8 text-blue-600" />
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${STATUS_STYLES[project.status]}`}>
            {STATUS_LABELS[project.status]}
          </span>
        </div>

        <h3 className="mt-5 text-xl font-semibold text-foreground">{project.name}</h3>
        <p className="mt-2 text-sm text-muted-foreground">{project.description}</p>
      </Link>

      <div className="flex items-center justify-end gap-1 border-t border-border/60 px-3 py-2 opacity-0 transition-opacity group-hover:opacity-100">
        <Button
          variant="outline"
          size="icon-sm"
          aria-label="Edit project"
          onClick={(e) => stopNavigation(e, () => setIsEditOpen(true))}
        >
          <Pencil className="h-3.5 w-3.5" />
        </Button>

        <Button
          variant="destructive"
          size="icon-sm"
          aria-label="Delete project"
          onClick={(e) => stopNavigation(e, () => setIsDeleteOpen(true))}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
      </div>

      <EditProjectDialog
        project={project}
        open={isEditOpen}
        onOpenChange={setIsEditOpen}
      />

      <DeleteProjectDialog
        project={project}
        open={isDeleteOpen}
        onOpenChange={setIsDeleteOpen}
      />
    </div>
  );
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/components/ProjectCard.tsx", $content, $enc)

$content = @'
"use client";

import { useEffect } from "react";

import CreateProjectButton from "./CreateProjectButton";
import ProjectCard from "./ProjectCard";
import { useProjectStore } from "../store/project.store";

export default function ProjectsPage() {
  const projects = useProjectStore((state) => state.projects);
  const isLoading = useProjectStore((state) => state.isLoading);
  const error = useProjectStore((state) => state.error);
  const fetchProjects = useProjectStore((state) => state.fetchProjects);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return (
    <main className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Projects</h1>
          <p className="mt-2 text-muted-foreground">Manage all your AI content projects.</p>
        </div>

        <CreateProjectButton />
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading projects...</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {!isLoading && !error && projects.length === 0 && (
        <div className="rounded-xl border border-dashed p-10 text-center text-sm text-muted-foreground">
          No projects yet. Create your first one.
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </main>
  );
}
'@
[System.IO.File]::WriteAllText("frontend/features/projects/components/ProjectsPage.tsx", $content, $enc)

$content = @'
export { default as ProjectsPage } from "./components/ProjectsPage";
export { default as ProjectDetail } from "./components/ProjectDetail";
export { default as ProjectCard } from "./components/ProjectCard";
export { default as CreateProjectButton } from "./components/CreateProjectButton";
export { default as CreateProjectDialog } from "./components/CreateProjectDialog";
export { default as EditProjectDialog } from "./components/EditProjectDialog";
export { default as DeleteProjectDialog } from "./components/DeleteProjectDialog";
export * from "./types/project";
export * from "./store/project.store";
export * from "./services/project.service";
'@
[System.IO.File]::WriteAllText("frontend/features/projects/index.ts", $content, $enc)
