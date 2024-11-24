import React, { useEffect, useState } from "react";

const Map = ({ apiUrl, selectedParkingId }) => {
    const [parking, setParking] = useState([]);
  
    useEffect(() => {
      if (!selectedParkingId) {
        return
      }
    
      const fetchTickets = async () => {
        try {
          const response = await fetch(apiUrl + `/get-parking?parking_id=${selectedParkingId}`);
          if (!response.ok) {
            throw new Error("Error al obtener el parking");
          }
          const jsonResponse = await response.json();
          setParking(jsonResponse.data || []);
        } catch (err) {
          console.error(err.message);
        }
      };
  
      fetchTickets();
    }, [apiUrl, selectedParkingId]);
  
    if (!selectedParkingId) {
      return (
        <section id="map" className="mt-12 text-center text-gray-400">
          <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
              Mapa
          </h2>
          <p className="text-gray-500">
            Selecciona un aparcamiento para saber como llegar
          </p>
        </section>
    );
    }
  
    return (
        <section id="map" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
            Mapa
        </h2>
        <p className="text-gray-400">
            Se tiene que hacer
        </p>
      </section>
    );
  };
  
  export default Map;

