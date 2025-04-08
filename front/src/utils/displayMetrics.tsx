// src/utils/displayMetrics.ts
interface MetricasProps {
  totalProyectos: number;
  proyectosAprobados: number;
  proyectosConDocente: number;
}

export const displayMetrics = (metricas: MetricasProps) => {
  return (
    <div className="metrics-list">
      <p>Total proyectos: {metricas.totalProyectos}</p>
      <p>Proyectos aprobados: {metricas.proyectosAprobados}</p>
      <p>Proyectos con docente: {metricas.proyectosConDocente}</p>
    </div>
  );
};
