import React, { useEffect, useState } from "react";
import L from "leaflet"; // map library
import "leaflet/dist/leaflet.css";
import "leaflet-routing-machine"; // route calculator

const Map = ({ apiUrl, selectedParkingId }) => {
  const [parking, setParking] = useState([]);
  const [userLocation, setUserLocation] = useState(null); //get UserLocation

  const FLAG_TEST_ROUTE = false //Enable to TEST the enroute

  useEffect(() => {
    // Ask permission to the user
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
          if (FLAG_TEST_ROUTE) {
            // Test location for non HTTPS websites or others errors with geolocalization
            setUserLocation({
              latitude: 40.416775, // Madrid, Spain
              longitude: -3.703790,
            });
          }
        }
      );
    } else {
      console.error("La geolocalización no está soportada en este navegador.");
    }
  }, []);

  // API Request Data Parking
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

  // API Request MAP
  useEffect(() => {
    if (parking && parking.latitude && parking.longitude) {
      // Initialize Map
      const map = L.map("map-container").setView([parking.latitude, parking.longitude], 15);
      
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);
  
      // Show pointer from the parking selected
      L.marker([parking.latitude, parking.longitude])
        .addTo(map)
        .bindPopup(`<b>${parking.name}</b><br>Latitud: ${parseFloat(parking.latitude).toFixed(6)}<br>Longitud: ${parseFloat(parking.longitude).toFixed(6)}`)
        .openPopup();
  
      // Draw Route if the user has location
      if (userLocation) {
        const routingControl = L.Routing.control({
          waypoints: [
            L.latLng(userLocation.latitude, userLocation.longitude),
            L.latLng(parking.latitude, parking.longitude),
          ],
          routeWhileDragging: true,
          show: false, // Hide all path directions
          createMarker: () => null, // Avoid waypoints being shown as Pointers
          addWaypoints: false, // Unable posibility to add Pointers
        });
  
        // Remove Routes
        routingControl.on("routeselected", () => {
          const container = document.querySelector(".leaflet-routing-container");
          if (container) container.style.display = "none";
        });
  
        routingControl.addTo(map);
      }
  
      return () => {
        map.remove();
      };
    }
  }, [parking, userLocation]);

  //No parking ID return
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
  //Render map return
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
