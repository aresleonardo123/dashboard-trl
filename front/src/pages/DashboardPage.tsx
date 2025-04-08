import React, { useState } from "react";
import { motion } from "framer-motion";
import GeneralInsights from "../components/GeneralInsights";
import {
  FiBarChart2,
  FiList,
  FiLock,
  FiRefreshCw,
  FiChevronUp,
  FiChevronDown,
  FiCheckCircle,
  FiUser,
  FiZap,
} from "react-icons/fi";
import { FaRocket } from "react-icons/fa";
import Navbar from "../components/Navbar";
import MetricCard from "../components/MetricaCard";
import ProjectSearch from "../components/ProjectSearch";
import ChartSection from "../components/ChartSection";
import DataStatus from "../components/DataStatus";
import Top10ProjectsView from "../components/Top10ProjectsView";
import ProjectsTable from "../components/ProjectsTable";
import {
  obtenerProyectos,
  getMetricasPrincipales,
  getGraficosData,
  getInsightsGenerales,
} from "../services/api";

const DashboardPage: React.FC = () => {
  const [password, setPassword] = useState<string>("");
  const [isControlExpanded, setIsControlExpanded] = useState(true);
  const [status, setStatus] = useState<{
    type: "idle" | "loading" | "success" | "error";
    message: string;
  }>({
    type: "idle",
    message: "",
  });

  const [metricas, setMetricas] = useState<any>(null);
  const [graficos, setGraficos] = useState<any>(null);
  const [insigths, setInsigths] = useState<any>(null);
  const [proyectos, setProyectos] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<
    "metrics" | "charts" | "search" | "projects-table" | "insigths"
  >("metrics");

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const handleActualizarDatos = async () => {
    const passwordLimpia = limpiarContraseña(password);
  
    if (!passwordLimpia) {
      setStatus({ type: "error", message: "Por favor ingrese la contraseña" });
      return;
    }
  
    setStatus({ type: "loading", message: "Actualizando datos..." });
  
    try {
      const [proyectosRes, metricasRes, graficosRes, insigthsRes] = await Promise.all([
        obtenerProyectos(passwordLimpia),
        getMetricasPrincipales(passwordLimpia),
        getGraficosData(passwordLimpia),
        getInsightsGenerales(passwordLimpia),
      ]);
  
      setProyectos(Array.isArray(proyectosRes) ? proyectosRes : []);
      setMetricas(metricasRes);
      setInsigths(insigthsRes);
      setGraficos(graficosRes.graficos);
      setStatus({
        type: "success",
        message: "Datos actualizados correctamente",
      });
    } catch (error) {
      console.error(error);
      setStatus({
        type: "error",
        message: "Error al actualizar datos. Verifique la contraseña.",
      });
    }
  };
  
  const limpiarContraseña = (password: string) => {
    return password
      .replace(/\u00A0/g, " ")
      .replace(/\u200B/g, "")
      .replace(/\uFEFF/g, "")
      .trim();
  };  
  

  return (
    <div className="min-h-screen ">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <motion.main
        className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 pb-12 pt-[100px]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="text-3xl font-bold text-purple-600 mb-6"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Dashboard TRL
        </motion.h1>

        {/* Sección de Control */}
        <motion.section
          className="bg-white rounded-xl shadow-sm overflow-hidden mb-6 border border-gray-200"
          initial={false}
          animate={{
            height: isControlExpanded ? "auto" : "64px",
            overflow: "hidden",
          }}
          transition={{ type: "spring", damping: 20 }}
        >
          <div className="p-6 border-b border-gray-100 bg-white">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-800 flex items-center gap-2">
                <FiLock className="text-purple-600" />
                Control de Datos
              </h2>
              <button
                onClick={() => setIsControlExpanded(!isControlExpanded)}
                className="text-purple-600 hover:text-purple-800  flex items-center gap-1 text-lg"
              >
                {isControlExpanded ? (
                  <>
                    <FiChevronUp /> Ocultar
                  </>
                ) : (
                  <>
                    <FiChevronDown /> Mostrar
                  </>
                )}
              </button>
            </div>

            {isControlExpanded && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <div className="mt-4">
                  <div className="flex flex-col sm:flex-row gap-4 items-end">
                    <div className="flex-grow">
                      <label
                        htmlFor="password"
                        className="block  text-lg font-medium text-gray-700 mb-1"
                      >
                        Contraseña de Acceso
                      </label>
                      <div className="relative rounded-md shadow-sm">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <FiLock className="text-gray-400" />
                        </div>
                        <input
                          type="password"
                          id="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              e.preventDefault();
                              handleActualizarDatos();
                            }
                          }}
                          className="block w-full pl-10 pr-4 py-2 border text-lg border-gray-300 focus:outline-0 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition"
                          placeholder="Ingrese su contraseña"
                        />
                      </div>
                    </div>

                    <button
                      onClick={handleActualizarDatos}
                      disabled={status.type === "loading"}
                      className={`px-6 py-2.5 rounded-md font-semibold text-white text-base transition-colors flex items-center gap-2 ${
                        status.type === "loading"
                          ? "bg-purple-400 cursor-not-allowed"
                          : "bg-purple-600 hover:bg-purple-700"
                      }`}
                    >
                      {status.type === "loading" ? (
                        <>
                          <FiRefreshCw className="animate-spin h-5 w-5" />
                          Cargando...
                        </>
                      ) : (
                        <>
                          <FiRefreshCw />
                          Actualizar Datos
                        </>
                      )}
                    </button>
                  </div>
                  <DataStatus status={status} />
                </div>
              </motion.div>
            )}
          </div>
        </motion.section>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          {/* Navegación de tabs ya está en Navbar */}

          <div className="p-6">
            {activeTab === "metrics" && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
                  <FiBarChart2 className="text-purple-600" />
                  Métricas Clave
                </h3>
                {metricas ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
                    <MetricCard
                      title="Total Proyectos"
                      value={metricas.formularios}
                      icon={<FiList className="text-blue-500" />}
                      trend="neutral"
                    />
                    <MetricCard
                      title="Nivel Inglés + Común"
                      value={metricas.nivel_ingles_mas_comun}
                      icon={<FiUser className="text-cyan-500" />}
                      trend="neutral"
                    />
                    <MetricCard
                      title="TRL Máximo"
                      value={metricas.trl_max}
                      icon={<FaRocket className="text-purple-500" />}
                      trend="neutral"
                    />
                    <MetricCard
                      title="Aprobados"
                      value={metricas.aprobados}
                      icon={<FiCheckCircle className="text-green-500" />}
                      trend="up"
                    />
                    <MetricCard
                      title="Con Docente"
                      value={metricas.docente_si}
                      icon={<FiUser className="text-amber-500" />}
                      trend="up"
                    />
                    <MetricCard
                      title="Sin Docente"
                      value={metricas.docente_no}
                      icon={<FiUser className="text-amber-500" />}
                      trend="up"
                    />
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                    {status.type === "idle"
                      ? "Actualice los datos para ver las métricas"
                      : "No hay datos disponibles"}
                  </div>
                )}
                {proyectos.length > 0 && (
                  <Top10ProjectsView
                    proyectos={proyectos}
                    password={password}
                  />
                )}
              </motion.section>
            )}

            {activeTab === "charts" && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <ChartSection graficos={graficos} />
              </motion.section>
            )}

            {activeTab === "search" && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <ProjectSearch password={password} />
              </motion.section>
            )}

            {activeTab === "projects-table" && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                {proyectos.length > 0 ? (
                  <ProjectsTable
                    proyectos={proyectos}
                    currentPage={currentPage}
                    itemsPerPage={itemsPerPage}
                    password={password}
                    setCurrentPage={setCurrentPage}
                  />
                ) : (
                  <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                    {status.type === "idle"
                      ? "Actualice los datos para ver los proyectos"
                      : "No hay datos disponibles"}
                  </div>
                )}
              </motion.section>
            )}

            {activeTab === "insigths" && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <h3 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
                  <FiZap className="text-purple-600" />
                  Insights Generales
                </h3>
                {insigths ? (
                  <GeneralInsights data={insigths} />
                ) : (
                  <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg">
                    {status.type === "idle"
                      ? "Actualice los datos para ver los insights"
                      : "No hay insights disponibles"}
                  </div>
                )}
              </motion.section>
            )}
          </div>
        </div>
      </motion.main>
    </div>
  );
};

export default DashboardPage;
