import React, { useState } from 'react';
import ParkingAviability from '../components/ParkingAviability.jsx';
import Predictions from '../components/Predictions.jsx';

const ParkingManager = ({ apiUrl }) => {
  const [selectedParkingId, setSelectedParkingId] = useState(null);

  return (
    <main>
      {/* Pasar la función para seleccionar parking */}
      <ParkingAviability apiUrl={apiUrl} onSelectParking={setSelectedParkingId} />
      {/* Pasar el ID seleccionado al componente Predictions */}
      <Predictions apiUrl={apiUrl} selectedParkingId={selectedParkingId} />
    </main>
  );
};

export default ParkingManager;
