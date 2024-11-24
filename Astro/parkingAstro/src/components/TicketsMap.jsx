import React, { useEffect, useState } from "react";

const TicketsMap = ({ apiUrl, selectedParkingId }) => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false); //Handle if it's loading

  useEffect(() => {
    if (!selectedParkingId) {
      return;
    }

    const fetchTickets = async () => {
      setLoading(true); // Start Loading
      try {
        const response = await fetch(`${apiUrl}/get-tickets?parking_id=${selectedParkingId}`);
        if (!response.ok) {
          throw new Error("Error al obtener los tickets");
        }
        const jsonResponse = await response.json();
        //Sort by number
        const sortedData = jsonResponse.data.sort((a, b) => {
          const numA = parseInt(a.ubication.replace('P', ''), 10);
          const numB = parseInt(b.ubication.replace('P', ''), 10);
          return numA - numB;
        });
        setTickets(sortedData || []);
      } catch (err) {
        console.error(err.message);
        setTickets([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTickets();
  }, [apiUrl, selectedParkingId]);

  //No parking ID return
  if (!selectedParkingId) {
    return (
      <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
          Ubicaciones Disponibles
        </h2>
        <p className="text-gray-500">
          Selecciona un aparcamiento para ver las ubicaciones disponibles
        </p>
      </section>
    );
  }

  //Loading return 
  if (loading) {
    return (
      <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
          Ubicaciones Disponibles
        </h2>
        <p className="text-gray-500">Cargando...</p>
      </section>
    );
  }

  //Empty Predictions return
  if (tickets.length === 0) {
    return (
      <section id="ubication_tickets" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
          Ubicaciones Disponibles
        </h2>
        <p className="text-gray-500">
          No hay datos disponibles para las ubicaciones.
        </p>
      </section>
    );
  }

  // Prepare data content for Iframe to render
  const renderIframeContent = () => {
    const grid = tickets
      .map(
        (ticket) => `
        <div style="
          width: 100px; height: 100px; 
          background-color: ${ticket.active ? "red" : "green"}; 
          margin: 5px; 
          display: flex; 
          align-items: center; 
          justify-content: center; 
          color: white; 
          font-size: 14px; 
          border-radius: 4px;
          font-weight: bold;
        ">
          ${ticket.ubication}
        </div>`
      )
      .join("");

    return `
      <div style="
        display: flex; 
        flex-wrap: wrap; 
        justify-content: center; 
        align-items: center; 
        gap: 10px; 
        padding: 20px;
        color: white;
      ">
        ${grid}
      </div>`;
  };

  // return Iframe with the renderIframeContent elements
  return (
    <section id="ubication_tickets" className="mt-12 text-center">
      <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7 ">Ubicaciones Disponibles</h2>
      <iframe
        title="Ubicaciones Disponibles"
        srcDoc={`<!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>
            body { margin: 0; font-family: Arial, sans-serif; height: 100%; }
            #content { 
              width: 100%; 
              height: 100%; 
              overflow: auto; 
              box-sizing: border-box; 
              padding-right: 10px; /* Espacio adicional para la barra de desplazamiento */
            }

            /* Personalización del scrollbar */
            ::-webkit-scrollbar {
              width: 8px;
            }

            ::-webkit-scrollbar-track {
              background-color: #333;
            }

            ::-webkit-scrollbar-thumb {
              background-color: #7c3aed; /* Morado (violet-400 en TailwindCSS) */
              border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb:hover {
              background-color: #6d28d9; /* Morado más oscuro (violet-500 en TailwindCSS) */
            }
          </style>
        </head>
        <body>
          <div
            id="content"
            style="display: flex; justify-content: center; align-items: center; height: 100vh;"
          >
            ${renderIframeContent()}
          </div>
        </body>
        </html>`}
        className="w-full h-[500px] border-2 border-gray-700 rounded-lg"
      />
    </section>
  );
};

export default TicketsMap;
