import React, { useEffect, useState } from "react";

const TicketsMap = ({ apiUrl, selectedParkingId }) => {
    const [tickets, setTickets] = useState([]);
  
    useEffect(() => {
      if (!selectedParkingId) {
        return
      }
    
      const fetchTickets = async () => {
        try {
          const response = await fetch(apiUrl + `/get-tickets?parking_id=${selectedParkingId}`);
          if (!response.ok) {
            throw new Error("Error al obtener los tickets");
          }
          const data = await response.json();
          console.log(data)
          setTickets(data.tickets || []);
        } catch (err) {
          console.error(err.message);
        }
      };
  
      fetchTickets();
    }, [apiUrl, selectedParkingId]);
  
    if (!selectedParkingId) {
      return (
        <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
          <h2 className="text-white text-center text-2xl font-bold my-4">
              Ubicaciones Disponibles
          </h2>
          <p className="text-gray-500">
            Selecciona un aparcamiento para ver las ubicaciones disponibles
          </p>
        </section>
    );
    }
  
    return (
        <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold my-4">
            Ubicaciones Disponibles
        </h2>
        <p className="text-gray-400">
            Se tiene que hacer
        </p>
      </section>
    );
  };
  
  export default TicketsMap;

