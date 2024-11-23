import React, { useEffect, useState } from "react";

const Predictions = ({ apiUrl, selectedParkingId }) => {
    const [predictions, setPredictions] = useState([]);
  
    useEffect(() => {
      if (!selectedParkingId) {
        return
      }
    
      const fetchPredictions = async () => {
        try {
          console.log(selectedParkingId)
          const response = await fetch(apiUrl + `/get-predictions?parking_id=${selectedParkingId}`);
          if (!response.ok) {
            throw new Error("Error al obtener las predicciones");
          }
          const data = await response.json();
          setPredictions(data.predictions || []);
        } catch (err) {
          console.error(err.message);
        }
      };
  
      fetchPredictions();
    }, [apiUrl, selectedParkingId]);
  
    if (!selectedParkingId) {
      return (
        <section id="prediction" className="mt-12 text-center text-gray-400">
          <h2 className="text-white text-center text-2xl font-bold my-4">
            Predicción de Plazas Disponibles
          </h2>
          <p className="text-gray-500">
            Selecciona un aparcamiento para ver predicciones
          </p>
        </section>
    );
    }
  
    return (
        <section id="prediction" className="mt-12 text-center text-gray-400">
          <h2 className="text-white text-center text-2xl font-bold my-4">
            Predicción de Plazas Disponibles
          </h2>
          <p className="text-gray-400">
            Según las tendencias actuales, se espera que en las próximas horas los aparcamientos más
            cercanos estén:
          </p>
          <ul className="mt-4 space-y-4">
            {predictions.map((prediction, index) => (
              <li
                key={index}
                className="bg-gray-700 p-4 rounded-lg shadow-lg hover:shadow-xl hover:shadow-violet-500"
              >
                <h3 className="text-xl font-semibold text-violet-400">{prediction.title}</h3>
                <p className="text-gray-300">{prediction.description}</p>
              </li>
            ))}
          </ul>
        </section>
    );
  };
  
  export default Predictions;

