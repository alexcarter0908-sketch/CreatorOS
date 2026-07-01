import {
  fetchProjects,
  createProject,
  updateProject,
  deleteProject,
} from "../api/project.api";

export async function getProjects() {
  return await fetchProjects();
}

export async function addProject(
  name: string,
  description: string
) {
  return await createProject({
    name,
    description,
  });
}

export async function editProject(
  id: number,
  name: string,
  description: string
) {
  return await updateProject(id, {
    name,
    description,
  });
}

export async function removeProject(id: number) {
  return await deleteProject(id);
}