import React, { useState } from 'react';
import { 
  FiX, 
  FiPrinter, 
  FiCheckCircle, 
  FiXCircle, 
  FiUser, 
  FiBarChart2,
  FiAward,
  FiInfo,
  FiFileText
} from 'react-icons/fi';
import { IconType } from 'react-icons';

interface ProjectDetailModalProps {
  project: any;
  onClose: () => void;
  password: string;
}

const ProjectDetailModal: React.FC<ProjectDetailModalProps> = ({ project, onClose, password }) => {
  const [isPrinting, setIsPrinting] = useState(false);
  const apiUrl = 'http://127.0.0.1:8000';

  const handlePrint = async () => {
    setIsPrinting(true);
    try {
      // Limpiar la contraseña consistentemente
      const cleanPassword = (pass: string) => 
        pass.replace(/\u00A0/g, " ")
           .replace(/\u200B/g, "")
           .replace(/\uFEFF/g, "")
           .trim();
  
      const passwordLimpia = cleanPassword(password);
      const projectName = encodeURIComponent(project["Nombre del Proyecto"]);
      
      // Usar el mismo formato de autenticación que otros endpoints
      const auth = btoa(`multimediafalab:${passwordLimpia}`);
      const url = `${apiUrl}/reporte-proyecto/${projectName}?auth=${encodeURIComponent(auth)}`;
      
      const win = window.open(url, '_blank');
      if (win) {
        win.focus();
      } else {
        alert('Permite las ventanas emergentes para ver el reporte.');
      }
    } catch (error) {
      console.error('Error al imprimir:', error);
      alert('Error al generar el reporte');
    } finally {
      setIsPrinting(false);
    }
  };

  const renderInfoItem = (label: string, value: string, Icon: IconType) => (
    <div>
      <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
        <Icon size={14} /> {label}
      </p>
      <p className="mt-1 text-gray-900 pl-6">{value}</p>
    </div>
  );

  const renderProgressBar = (label: string, value: number, colorClass: string) => (
    <div>
      <div className="flex justify-between items-center mb-1">
        <p className="text-sm font-medium text-gray-700">{label}</p>
        <span className="text-sm font-medium text-gray-900">{value}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2.5">
        <div 
          className={`${colorClass} h-2.5 rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(100, value)}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0  bg-opacity-30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-gray-200 transition-all duration-300 transform">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6 border-b border-gray-100 pb-4">
            <div>
              <h3 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                <FiFileText className="text-purple-600" />
                {project["Nombre del Proyecto"]}
              </h3>
              <p className="text-sm text-gray-500 mt-1">Detalles completos del proyecto</p>
            </div>
            <button 
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-colors p-1 rounded-full hover:bg-gray-100"
              aria-label="Cerrar modal"
            >
              <FiX size={24} />
            </button>
          </div>
          
          {/* Contenido */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Columna izquierda - Información General */}
            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2 pb-2 border-b border-gray-100">
                <FiInfo className="text-blue-500" />
                Información General
              </h4>
              
              <div className="space-y-4">
                {renderInfoItem('Nombre del Proyecto', project["Nombre del Proyecto"], FiFileText)}
                
                <div>
                  <p className="text-sm font-medium text-gray-500 flex items-center gap-2">
                    <FiAward size={14} /> Estado de Aprobación
                  </p>
                  <span className={`mt-1 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${project.Aprobado === "Sí" ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'} pl-6`}>
                    {project.Aprobado === "Sí" ? (
                      <FiCheckCircle className="mr-1.5" />
                    ) : (
                      <FiXCircle className="mr-1.5" />
                    )}
                    {project.Aprobado}
                  </span>
                </div>
                
                {renderInfoItem('Nivel TRL', project["Nivel TRL"], FiBarChart2)}
                {renderInfoItem('Docente Acompañante', project["Docente Acompañante"] ? 'Sí' : 'No', FiUser)}
              </div>
            </div>
            
            {/* Columna derecha - Puntajes TRL */}
            <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2 pb-2 border-b border-gray-100">
                <FiBarChart2 className="text-purple-500" />
                Progreso TRL
              </h4>
              
              <div className="space-y-5">
                {renderProgressBar('TRL 1-3 (Básico)', project["Puntaje TRL 1-3"], 'bg-blue-500')}
                {renderProgressBar('TRL 4-7 (Intermedio)', project["Puntaje TRL 4-7"], 'bg-green-500')}
                {renderProgressBar('TRL 8-9 (Avanzado)', project["Puntaje TRL 8-9"], 'bg-purple-500')}
                
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-blue-800 flex items-start gap-2">
                    <FiInfo className="text-blue-500 mt-0.5 flex-shrink-0" />
                    <span>Los puntajes TRL representan el nivel de madurez tecnológica del proyecto en cada segmento.</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Footer con botones */}
          <div className="mt-8 pt-4 border-t border-gray-100 flex flex-col sm:flex-row justify-end gap-3">
            <button
              onClick={onClose}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <FiX size={16} />
              Cerrar
            </button>
            <button
              onClick={handlePrint}
              disabled={isPrinting}
              className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:opacity-90 disabled:opacity-70 transition-all flex items-center justify-center gap-2 font-medium shadow-sm hover:shadow-md"
            >
              {isPrinting ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generando reporte...
                </>
              ) : (
                <>
                  <FiPrinter size={16} />
                  Imprimir Reporte
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailModal;