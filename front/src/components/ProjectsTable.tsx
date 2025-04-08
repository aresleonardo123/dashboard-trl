import React, { useState } from "react";
import { ChevronUpIcon, ChevronDownIcon } from "@heroicons/react/24/solid";
import ProjectDetailModal from "./ProjectDetailModal";

interface ProjectData {
  "Nombre del Proyecto": string;
  Aprobado: "Sí" | "No";
  "Puntaje TRL 1-3": number;
  "Puntaje TRL 4-7": number;
  "Puntaje TRL 8-9": number;
  "Puntaje Total": number;
  "Segmento TRL"?: string;
  "Docente Acompañante"?: boolean;
  "Nivel de Inglés"?: string;
  "Industria"?: string;
  "Ubicación"?: string;
  Insights?: string[] | string;
  
  // Añade esta línea para permitir acceso por string index
  [key: string]: any;
}
interface ProjectsTableProps {
  proyectos: ProjectData[];
  currentPage: number;
  itemsPerPage: number;
  setCurrentPage: (page: number) => void;
  hidePagination?: boolean;
  password: string;
}

const ProjectsTable: React.FC<ProjectsTableProps> = ({
  proyectos,
  currentPage,
  itemsPerPage,
  setCurrentPage,
  hidePagination,
  password,
}) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: "ascending" | "descending";
  }>({
    key: "Puntaje Total",
    direction: "descending",
  });

  const [selectedProject, setSelectedProject] = useState<ProjectData | null>(
    null
  );
  const [isModalOpen, setIsModalOpen] = useState(false);
  const handleViewDetails = (project: ProjectData) => {
    setSelectedProject(project);
    setIsModalOpen(true);
  };

  const sortedProjects = [...proyectos].sort((a, b) => {
    if (a.Aprobado !== b.Aprobado) return a.Aprobado === "Sí" ? -1 : 1;
    if (a[sortConfig.key] < b[sortConfig.key])
      return sortConfig.direction === "ascending" ? -1 : 1;
    if (a[sortConfig.key] > b[sortConfig.key])
      return sortConfig.direction === "ascending" ? 1 : -1;
    return 0;
  });

  const paginatedProjects = sortedProjects.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const requestSort = (key: string) => {
    const direction =
      sortConfig.key === key && sortConfig.direction === "ascending"
        ? "descending"
        : "ascending";
    setSortConfig({ key, direction });
  };

  return (
    <div className="overflow-x-auto bg-white shadow-lg rounded-xl border border-gray-200">
      <table className="min-w-full text-lg text-left text-gray-800">
        <thead className="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th className="px-6 py-4 font-semibold">Proyecto</th>
            <th className="px-6 py-4 font-semibold">Aprobado</th>
            {[
              "Puntaje TRL 1-3",
              "Puntaje TRL 4-7",
              "Puntaje TRL 8-9",
              "Puntaje Total",
            ].map((key) => (
              <th
                key={key}
                className="px-6 py-4 font-semibold cursor-pointer select-none hover:text-purple-600 transition-colors"
                onClick={() => requestSort(key)}
              >
                {key}
                {sortConfig.key === key &&
                  (sortConfig.direction === "ascending" ? (
                    <ChevronUpIcon className="inline w-4 h-4 ml-1" />
                  ) : (
                    <ChevronDownIcon className="inline w-4 h-4 ml-1" />
                  ))}
              </th>
            ))}
            <th className="px-6 py-4 font-semibold">Acciones</th>
          </tr>
        </thead>
        <tbody className="text-base">
          {paginatedProjects.map((proyecto, idx) => (
            <tr
              key={idx}
              className="hover:bg-purple-50 transition-all duration-200 border-t"
            >
              <td className="px-6 py-4 font-medium">
                {proyecto["Nombre del Proyecto"]}
              </td>
              <td className="px-6 py-4">
                <span
                  className={`px-3 py-1 text-sm font-medium rounded-full ${
                    proyecto.Aprobado === "Sí"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {proyecto.Aprobado}
                </span>
              </td>
              {[
                "Puntaje TRL 1-3",
                "Puntaje TRL 4-7",
                "Puntaje TRL 8-9",
                "Puntaje Total",
              ].map((key) => (
                <td key={key} className="px-6 py-4">
                  {proyecto[key]}
                </td>
              ))}
              <td className="px-6 py-4">
                <button
                  onClick={() => handleViewDetails(proyecto)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition"
                >
                  Ver Detalles
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {!hidePagination && (
        <div className="flex flex-col md:flex-row justify-between items-center px-6 py-4 bg-gray-50 border-t gap-4">
          <span className="text-base text-gray-700">
            Página <strong>{currentPage}</strong> de{" "}
            <strong>{Math.ceil(proyectos.length / itemsPerPage)}</strong>
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded-md bg-purple-600 text-white font-medium hover:bg-purple-700 disabled:opacity-50 transition"
            >
              Anterior
            </button>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={
                currentPage >= Math.ceil(proyectos.length / itemsPerPage)
              }
              className="px-4 py-2 rounded-md bg-purple-600 text-white font-medium hover:bg-purple-700 disabled:opacity-50 transition"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {isModalOpen && selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          onClose={() => setIsModalOpen(false)}
          password={password
            .replace(/\u00A0/g, " ")
            .replace(/\u200B/g, "")
            .replace(/\uFEFF/g, "")
            .trim()}
        />
      )}
    </div>
  );
};

export default ProjectsTable;
