import React, { useEffect, useState } from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

// Componente personalizado para la flecha "siguiente"
const CustomNextArrow = (props) => {
  const { className, style, onClick } = props;
  return (
    <div
      className={`${className} next-arrow`}
      style={{ ...style }}
      onClick={onClick}
    >
      →
    </div>
  );
};

// Componente personalizado para la flecha "anterior"
const CustomPrevArrow = (props) => {
  const { className, style, onClick } = props;
  return (
    <div
      className={`${className} prev-arrow`}
      style={{ ...style }}
      onClick={onClick}
    >
      ←
    </div>
  );
};

const ParkingAviability = ({ apiUrl, onSelectParking }) => {
  const [parkings, setParkings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const responseParkings = await fetch(apiUrl + "get-parkings");
      if (!responseParkings.ok) {
        throw new Error("Error al obtener los datos de los aparcamientos");
      }
      const jsonDataParkings = await responseParkings.json();
      const parkings = jsonDataParkings.data || [];

      const responseTickets = await fetch(apiUrl + "/get-tickets?parking_id=1&active=True");
      if (!responseTickets.ok) {
        throw new Error("Error al obtener los datos de los tickets");
      }
      const jsonDataTickets = await responseTickets.json();
      const tickets = jsonDataTickets.data || [];

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
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      console.log("Refrescando datos...");
      fetchData();
    }, 10000);

    return () => clearInterval(interval);
  }, [apiUrl]);

  if (loading) return <p className="text-center text-gray-500">Cargando aparcamientos...</p>;
  if (error) return <p className="text-center text-red-500">Error: {error}</p>;

  // Configuración de react-slick
  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 3,
    slidesToScroll: 1,
    centerMode: true,
    nextArrow: <CustomNextArrow />,
    prevArrow: <CustomPrevArrow />,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
          arrows: false,
        },
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 1,
          centerPadding: "20px",
          arrows: false,
        },
      },
    ],
    beforeChange: () => {
      // Eliminar el foco antes de cambiar de diapositiva
      if (document.activeElement) {
        document.activeElement.blur();
      }
    },
  };

  return (
    <div>
      <h1 className="text-center text-2xl font-bold mt-4 mb-7">Aparcamientos Disponibles</h1>
      <section id="parkings">
        <Slider className="border-2 border-gray-700 rounded-lg" {...sliderSettings}>
          {parkings.map((parking) => (
            <div
              key={parking.id}
              className="relative"
              onClick={() => onSelectParking(parking.id)}
            >
              <div className="bg-gray-800 rounded-lg shadow-lg p-6 mx-4 m-6 hover:shadow-xl hover:shadow-violet-500 w-120 h-54 card-parking">
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
                        parking.tickets.length < parking.total_capacity
                          ? "bg-green-500"
                          : "bg-red-500"
                      }`}
                    ></div>
                    <span
                      className={`ml-2 ${
                        parking.tickets.length < parking.total_capacity
                          ? "text-green-500"
                          : "text-red-500"
                      }`}
                    >
                      {parking.tickets.length < parking.total_capacity ? "Disponible" : "Completo"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </Slider>
      </section>
    </div>
  );
};

export default ParkingAviability;
