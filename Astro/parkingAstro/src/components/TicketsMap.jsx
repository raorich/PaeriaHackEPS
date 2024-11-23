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
          const jsonReponse = await response.json();
          console.log(jsonReponse)
          setTickets(jsonReponse.data || []);
        } catch (err) {
          console.error(err.message);
        }
      };
  
      fetchTickets();
    }, [apiUrl, selectedParkingId]);

    console.log(tickets.length)
  
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

    if (!tickets) {
      return (
        <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
            <h2 className="text-white text-center text-2xl font-bold my-4">
                Ubicaciones Disponibles
            </h2>
            <hr />
          </section>
      );
    }
  
    return (
      <section id="ubication_tickets" className="mt-12 text-center">
        <h2 className="text-white text-center text-2xl font-bold my-4">
          Ubicaciones Disponibles
        </h2>
        <div className="grid grid-cols-3 gap-4 justify-center">
          {tickets.map((ticket) => (
            <div
              key={ticket.id}
              className={`p-4 rounded-lg shadow-md text-white font-bold text-lg flex items-center justify-center ${
                ticket.active ? "bg-green-500" : "bg-red-500"
              }`}
              style={{ height: "100px", cursor: "pointer" }}
            >
              {ticket.ubication}
            </div>
          ))}
        </div>
      </section>
    );
  
  };
  
  export default TicketsMap;

