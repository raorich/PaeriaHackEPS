import React, { useState } from 'react';
import ParkingAviability from '../components/ParkingAviability.jsx';
import Predictions from '../components/Predictions.jsx';
import TicketsMap from '../components/TicketsMap.jsx';
import Map from '../components/Map.jsx';

const ParkingManager = ({ apiUrl }) => {
  const [selectedParkingId, setSelectedParkingId] = useState(null);

  return (
    <main>
      {/* Pasar la función para seleccionar parking */}
      <ParkingAviability apiUrl={apiUrl} onSelectParking={setSelectedParkingId} />
      {/* Pasar el ID seleccionado al componente Tickets */}
      <TicketsMap apiUrl={apiUrl} selectedParkingId={selectedParkingId} />
      {/* Pasar el ID seleccionado al componente Predictions */}
      <Predictions apiUrl={apiUrl} selectedParkingId={selectedParkingId} />
      {/* Pasar el ID seleccionado al componente Map */}
      <Map apiUrl={apiUrl} selectedParkingId={selectedParkingId} />
    </main>
  );
};

export default ParkingManager;
