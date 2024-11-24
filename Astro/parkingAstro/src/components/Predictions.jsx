import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  Filler,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const Predictions = ({ apiUrl, selectedParkingId }) => {
    const [predictions, setPredictions] = useState([]);
    const [isLoading, setIsLoading] = useState(false); // Estado para controlar si está cargando

    useEffect(() => {
      if (!selectedParkingId) {
        return;
      }
    
      const fetchPredictions = async () => {
        setIsLoading(true); // Empieza a cargar
        try {
          const response = await fetch(`${apiUrl}/request-occupation-prediction`, {
            method: "POST", // Use POST request
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ parking_id: selectedParkingId })
            });

          if (!response.ok) {
            throw new Error("Error al obtener las predicciones");
          }
          const predictions_json = await response.json();
          console.log(predictions_json)
          setPredictions(predictions_json || []);
        } catch (err) {
            console.error(err.message);
            setPredictions([]); // Resetea predicciones en caso de error
        } finally {
            setIsLoading(false); // Deja de cargar
        }
      };
  
      fetchPredictions();
    }, [apiUrl, selectedParkingId]);
  
    if (!selectedParkingId) {
      return (
        <section id="prediction" className="mt-12 text-center text-gray-400">
          <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
            Predicción de Plazas Disponibles
          </h2>
          <p className="text-gray-500">
            Selecciona un aparcamiento para ver predicciones
          </p>
        </section>
      );
    }

    if (isLoading) {
        return (
          <section id="prediction" className="mt-12 text-center text-gray-400">
            <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
              Predicción de Plazas Disponibles
            </h2>
            <p className="text-gray-500">
              Cargando datos...
            </p>
          </section>
        );
    }

    if (predictions.length === 0) {
        return (
          <section id="prediction" className="mt-12 text-center text-gray-400">
            <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
              Predicción de Plazas Disponibles
            </h2>
            <p className="text-gray-500">
                No hay histórico suficiente para hacer predicciones.
            </p>
          </section>
        );
    }

    // Prepare data for Chart.js
    const chartData = {
        labels: predictions.map(p => `${p.day} ${p.hour}`), // Combine day and hour
        datasets: [
        {
            label: "Predicción de Ocupación",
            data: predictions.map(p => p.predicted_occupation_probability), // Occupation data
            fill: true,
            backgroundColor: "rgba(138, 43, 226, 0.2)",
            borderColor: "rgba(138, 43, 226, 1)",
            borderWidth:2,
            tension: 0.3
        }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
        legend: {
            display: true,
            position: "top"
        },
        title: {
            display: true,
            text: "Predicción de Ocupación de Aparcamiento"
        }
        },
        scales: {
        x: {
            title: {
            display: true,
            text: "Fecha y Hora"
            }
        },
        y: {
            title: {
            display: true,
            text: "Plazas Ocupadas"
            },
            beginAtZero: true,
            min: 0,
            max: 1
        }
        }
    };

    return (
        <section id="prediction" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold my-4">
            Predicción de Plazas Disponibles
        </h2>
        <div className="chart-container border-2 border-gray-700 rounded-lg p-4" style={{ width: "100%", height: "100%", minWidth: "400px", minHeight: "500px"}}>
            <Line data={chartData} options={chartOptions} />
        </div>
        </section>
    );
};
  
export default Predictions;
