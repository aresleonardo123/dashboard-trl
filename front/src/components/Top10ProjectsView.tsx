import React, { useState } from "react";
import ProjectsTable from "./ProjectsTable";
import { descargarReporteTop10 } from "../services/api";

interface Top10ProjectsViewProps {
  proyectos: any[];
  password: string;
}

const Top10ProjectsView: React.FC<Top10ProjectsViewProps> = ({
  proyectos,
  password,
}) => {
  const top10 = [...proyectos]
    .sort((a, b) => b["Puntaje Total"] - a["Puntaje Total"])
    .slice(0, 10);

  const [currentPage, setCurrentPage] = useState(1);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-xl font-bold py-6 text-gray-800">
          Top 10 Proyectos con Mayor Puntaje
        </h3>
        <button
          onClick={() => descargarReporteTop10(password)}
          className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition"
        >
          Descargar PDF
        </button>
      </div>
      <ProjectsTable
        proyectos={top10}
        currentPage={currentPage}
        itemsPerPage={10}
        setCurrentPage={setCurrentPage}
        password={password}
        hidePagination 
      />
    </div>
  );
};

export default Top10ProjectsView;
