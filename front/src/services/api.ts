import axios from "axios";

// Usamos ruta relativa vacía para compatibilidad con backend integrado
const apiUrl = "";

const limpiarContraseña = (password: string): string =>
  password
    .replace(/\u00A0/g, " ") // Espacio no separable
    .replace(/\u200B/g, "")  // Zero-width space
    .replace(/\uFEFF/g, "")  // BOM
    .trim();

export const getGraficosData = async (password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const response = await axios.get(`${apiUrl}/datos-graficos`, {
      headers: {
        Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error obteniendo gráficos:", error);
    throw error;
  }
};

export const getMetricasPrincipales = async (password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const response = await axios.get(`${apiUrl}/metricas-principales`, {
      headers: {
        Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error obteniendo métricas:", error);
    throw error;
  }
};

export const getInsightsGenerales = async (password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const response = await axios.get(`${apiUrl}/insights-generales`, {
      headers: {
        Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error obteniendo insights generales:", error);
    throw error;
  }
};

export const actualizarDatos = async (password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const headers = {
      Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
    };

    const response = await axios.post(`${apiUrl}/actualizar-datos`, {}, { headers });
    return response.data;
  } catch (error) {
    console.error("Error al actualizar los datos:", error);
    throw error;
  }
};

export const obtenerProyectos = async (password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const response = await axios.get(`${apiUrl}/proyectos`, {
      headers: {
        Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
      },
    });
    return response.data.proyectos;
  } catch (error) {
    console.error("Error obteniendo proyectos:", error);
    throw error;
  }
};

export const buscarProyecto = async (nombre: string, password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const response = await axios.post(`${apiUrl}/buscar-proyecto`,
      { nombre },
      {
        headers: {
          Authorization: `Basic ${btoa(`multimediafalab:${limpia}`)}`
        },
      }
    );
    return response.data.proyectos;
  } catch (error) {
    console.error("Error al buscar el proyecto:", error);
    return [];
  }
};

export const generarReporteProyecto = async (nombre: string, password: string) => {
  try {
    const limpia = limpiarContraseña(password);
    const auth = btoa(`multimediafalab:${limpia}`);
    const url = `/reporte-proyecto/${encodeURIComponent(nombre)}?auth=${auth}`;

    const win = window.open(url, "_blank");
    if (win) {
      win.focus();
    } else {
      alert("Permite las ventanas emergentes para ver el reporte.");
    }
  } catch (error) {
    console.error("Error generando reporte del proyecto:", error);
    alert("No se pudo generar el reporte del proyecto.");
  }
};

export const descargarReporteAprobados = async (password: string): Promise<void> => {
  try {
    const limpia = limpiarContraseña(password);
    const auth = btoa(`multimediafalab:${limpia}`);
    const url = `/reporte-aprobados?auth=${auth}`;

    const win = window.open(url, "_blank");
    if (win) {
      const checkWindow = setInterval(() => {
        if (win.closed) clearInterval(checkWindow);
      }, 100);
    } else {
      alert("Permite las ventanas emergentes para ver el reporte.");
    }
  } catch (error) {
    console.error("Error generando reporte de aprobados:", error);
    alert("No se pudo generar el reporte de aprobados.");
  }
};

export const descargarReporteTop10 = async (password: string): Promise<void> => {
  try {
    const limpia = limpiarContraseña(password);
    const auth = btoa(`multimediafalab:${limpia}`);
    const url = `/reporte-top10?auth=${auth}`;

    const win = window.open(url, "_blank");
    if (win) {
      const checkWindow = setInterval(() => {
        if (win.closed) clearInterval(checkWindow);
      }, 100);
    } else {
      alert("Permite las ventanas emergentes para ver el reporte.");
    }
  } catch (error) {
    console.error("Error generando reporte Top10:", error);
    alert("No se pudo generar el reporte Top10.");
  }
};
