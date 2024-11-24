import React, { useEffect, useState } from "react";
import L from "leaflet"; // Importa la biblioteca Leaflet
import "leaflet/dist/leaflet.css"; // Importa los estilos de Leaflet
import "leaflet-routing-machine"; // Importa la biblioteca para el enrutamiento

const Map = ({ apiUrl, selectedParkingId }) => {
  const [parking, setParking] = useState([]);
  const [userLocation, setUserLocation] = useState(null);

  const FLAG_TEST_ROUTE = false

  useEffect(() => {
    // Solicitar la ubicación actual del usuario directamente
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.log("Not able to get ubication")
          //console.error("Error al obtener la ubicación: ", error);
          if (FLAG_TEST_ROUTE) {
            // Coordenadas de prueba para entornos no HTTPS o errores en la geolocalización
            setUserLocation({
              latitude: 40.416775, // Madrid, España
              longitude: -3.703790,
            });
          }
        }
      );
    } else {
      console.error("La geolocalización no está soportada en este navegador.");
    }
  }, []);

  useEffect(() => {
    if (!selectedParkingId) {
      return;
    }

    const fetchParking = async () => {
      try {
        const response = await fetch(`${apiUrl}/get-parking?parking_id=${selectedParkingId}`);
        if (!response.ok) {
          throw new Error("Error al obtener el parking");
        }
        const jsonResponse = await response.json();
        setParking(jsonResponse.data || []);
      } catch (err) {
        console.error(err.message);
      }
    };

    fetchParking();
  }, [apiUrl, selectedParkingId]);

  useEffect(() => {
    if (parking && parking.latitude && parking.longitude) {
      // Inicializar el mapa
      const map = L.map("map-container").setView([parking.latitude, parking.longitude], 15);
  
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);
  
      // Mostrar un marcador en el parking seleccionado
      L.marker([parking.latitude, parking.longitude])
        .addTo(map)
        .bindPopup(`<b>${parking.name}</b><br>Latitud: ${parseFloat(parking.latitude).toFixed(6)}<br>Longitud: ${parseFloat(parking.longitude).toFixed(6)}`)
        .openPopup();
  
      // Dibujar una ruta si se tiene la ubicación del usuario
      if (userLocation) {
        const routingControl = L.Routing.control({
          waypoints: [
            L.latLng(userLocation.latitude, userLocation.longitude),
            L.latLng(parking.latitude, parking.longitude),
          ],
          routeWhileDragging: true,
          show: false, // Oculta el cuadro de direcciones
          createMarker: () => null, // Evita que los waypoints se muestren como marcadores
          addWaypoints: false, // Desactiva la posibilidad de añadir waypoints
        });
  
        // Eliminar el contenedor del panel de direcciones
        routingControl.on("routeselected", () => {
          const container = document.querySelector(".leaflet-routing-container");
          if (container) container.style.display = "none";
        });
  
        routingControl.addTo(map);
      }
  
      return () => {
        map.remove(); // Limpiar el mapa al desmontar
      };
    }
  }, [parking, userLocation]);

  if (!parking || !parking.latitude || !parking.longitude) {
    return (
      <section id="map" className="mt-12 text-center text-gray-400">
        <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
          Mapa
        </h2>
        <p className="text-gray-500">
          No hay información de latitud y longitud para este aparcamiento.
        </p>
      </section>
    );
  }

  return (
    <section id="map" className="mt-12">
      <h2 className="text-white text-center text-2xl font-bold mt-4 mb-7">
        Mapa
      </h2>
      <div className="border-2 border-gray-700 rounded-lg">
        <div className="p-4">
          <div id="map-container" style={{ height: "500px", borderRadius: "10px" }}></div>
        </div>
      </div>
    </section>
  );
};

export default Map;
