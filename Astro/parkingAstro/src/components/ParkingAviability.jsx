import React, { useEffect, useState } from "react";

const ApiData = ({ apiUrl }) => {
  const [parkings, setParkings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      // Obtener los datos de los aparcamientos
      const responseParkings = await fetch(apiUrl + "get-parkings");
      if (!responseParkings.ok) {
        throw new Error("Error al obtener los datos de los aparcamientos");
      }
      const jsonDataParkings = await responseParkings.json();
      const parkings = jsonDataParkings.data || [];

      // Obtener los datos de las plazas ocupadas
      const responseTickets = await fetch(apiUrl + "/get-tickets?parking_id=1&active=True");
      if (!responseTickets.ok) {
        throw new Error("Error al obtener los datos de los tickets");
      }
      const jsonDataTickets = await responseTickets.json();
      const tickets = jsonDataTickets.data || [];

      // Combinamos los datos
      const combinedParkings = parkings.map((parking) => {
        const ticketsForParking = tickets.filter(
          (ticket) => ticket.parking_id === parking.id
        );
        return {
          ...parking,
          tickets: ticketsForParking,
        };
      });

      setParkings(combinedParkings);
      setError(null); // Limpiar errores previos si los datos se obtienen con éxito
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Llamar fetchData inicialmente
    fetchData();

    // Configurar el intervalo para refrescar los datos
    const interval = setInterval(() => {
      console.log("Refrescando datos...");
      fetchData();
    }, 10000); // Cambiar el tiempo de refresco en milisegundos (10 segundos)

    // Limpiar el intervalo al desmontar el componente
    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) return <p className="text-center text-gray-500">Cargando aparcamientos...</p>;
  if (error) return <p className="text-center text-red-500">Error: {error}</p>;

  return (
    <div>
      <h1 className="text-center text-2xl font-bold my-4">Aparcamientos Disponibles</h1>
      <section id="parkings" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {parkings.map((parking) => (
          <div
            key={parking.id}
            className="relative bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl hover:shadow-violet-500"
          >
            <div className="relative z-10">
              <h2 className="text-xl font-bold text-violet-400">{parking.name}</h2>
              <p className="text-gray-400 mt-2">
                <strong>Ubicación:</strong> {parking.location}
              </p>
              <p className="text-gray-400 mt-1">
                <strong>Ocupación:</strong> {parking.tickets.length}/{parking.total_capacity} plazas
              </p>
              <div className="mt-4 flex items-center">
                <div
                  className={`w-4 h-4 rounded-full ${
                    parking.tickets.length < parking.total_capacity ? "bg-green-500" : "bg-red-500"
                  }`}
                ></div>
                <span
                  className={`ml-2 ${
                    parking.tickets.length < parking.total_capacity ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {parking.tickets.length < parking.total_capacity ? "Disponible" : "Completo"}
                </span>
              </div>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
};

export default ApiData;
