import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = ''; // Leave blank to use proxy

function App() {
  const [robotPosition, setRobotPosition] = useState({ x: 0, y: 0, z: 0 });
  const [cubePosition, setCubePosition] = useState({ x: 100, y: 100, z: 0 });
  const [destination, setDestination] = useState({ x: 500, y: 500, z: 0 });
  const [currentPosition, setCurrentPosition] = useState([0, 0, 0]);
  const [message, setMessage] = useState('');

  // Fetch current robot position every second
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get(`${API_BASE_URL}/current-position`)
        .then((response) => {
          setCurrentPosition(response.data.current_position);
        })
        .catch((error) => console.error('Error fetching current position:', error));
    }, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  // Start pick and place operation
  const handlePickPlace = () => {
    axios.post(`${API_BASE_URL}/start-pick-place`, {
      cube_position: cubePosition,
      destination: destination
    })
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch((error) => console.error('Error in pick and place operation:', error));
  };

  // Move robot to home position
  const handleMoveHome = () => {
    axios.post(`${API_BASE_URL}/move-home`)
      .then((response) => {
        setMessage(response.data.message);
        setCurrentPosition(response.data.current_position);
      })
      .catch((error) => console.error('Error moving home:', error));
  };

  // Set starting positions
  const handleSetStartPositions = () => {
    axios.post(`${API_BASE_URL}/set-start-positions`, {
      robot_position: robotPosition,
      cube_position: cubePosition
    })
      .then((response) => {
        setMessage(response.data.message);
      })
      .catch((error) => console.error('Error setting start positions:', error));
  };

  // Helper function to ensure the input value is always an integer
  const handleIntegerChange = (setter, field, value) => {
    // Make sure only integers are passed, ignore non-numeric input
    const parsedValue = parseInt(value, 10);
    
    if (!isNaN(parsedValue)) {
      setter(prev => ({
        ...prev,
        [field]: parsedValue
      }));
    }
  };

  // Convert current position to a normalized 2x2 meter grid
  const robotX = currentPosition[0] / 1000; // Convert to meters (2x2 grid)
  const robotY = currentPosition[1] / 1000; // Convert to meters (2x2 grid)

  return (
    <div className="App">
      <h1>Pick and Place Robot</h1>

      <h2>Set Starting Positions</h2>
      <div>
        <label>Robot Position (X, Y, Z): </label>
        <input type="number" value={robotPosition.x} onChange={(e) => handleIntegerChange(setRobotPosition, 'x', e.target.value)} />
        <input type="number" value={robotPosition.y} onChange={(e) => handleIntegerChange(setRobotPosition, 'y', e.target.value)} />
        <input type="number" value={robotPosition.z} onChange={(e) => handleIntegerChange(setRobotPosition, 'z', e.target.value)} />
      </div>

      <div>
        <label>Cube Position (X, Y, Z): </label>
        <input type="number" value={cubePosition.x} onChange={(e) => handleIntegerChange(setCubePosition, 'x', e.target.value)} />
        <input type="number" value={cubePosition.y} onChange={(e) => handleIntegerChange(setCubePosition, 'y', e.target.value)} />
        <input type="number" value={cubePosition.z} onChange={(e) => handleIntegerChange(setCubePosition, 'z', e.target.value)} />
      </div>

      <button onClick={handleSetStartPositions}>Set Start Positions</button>

      <h2>Destination Position</h2>
      <div>
        <label>Destination (X, Y, Z): </label>
        <input type="number" value={destination.x} onChange={(e) => handleIntegerChange(setDestination, 'x', e.target.value)} />
        <input type="number" value={destination.y} onChange={(e) => handleIntegerChange(setDestination, 'y', e.target.value)} />
        <input type="number" value={destination.z} onChange={(e) => handleIntegerChange(setDestination, 'z', e.target.value)} />
      </div>

      <h2>Controls</h2>
      <button onClick={handleMoveHome}>Move Robot to Home</button>
      <button onClick={handlePickPlace}>Start Pick and Place</button>

      <h2>Current Robot Position</h2>
      <p>X: {currentPosition[0]}, Y: {currentPosition[1]}, Z: {currentPosition[2]}</p>

      <h3>{message}</h3>

      {/* Visualization */}
      <h2>Robot Movement Visualization</h2>
      <svg width="400" height="400" viewBox="0 0 2 2" style={{ border: "1px solid black" }}>
        {/* Application footprint boundary */}
        <rect x="0" y="0" width="2" height="2" fill="none" stroke="blue" strokeWidth="0.01" />

        {/* Table A (Top-Left) */}
        <rect x="0" y="0" width="0.5" height="0.5" fill="blue" />
        <text x="0.1" y="0.4" fontSize="0.1" fill="white">Table A</text>

        {/* Table B (Bottom-Right, rotated) */}
        <rect x="1.5" y="1.5" width="0.5" height="0.5" fill="blue" transform="rotate(45 1.75 1.75)" />
        <text x="1.6" y="1.9" fontSize="0.1" fill="white">Table B</text>

        {/* Robot (green circle) */}
        <circle cx={robotX} cy={robotY} r="0.05" fill="green" />
        <text x={robotX + 0.1} y={robotY + 0.1} fontSize="0.05" fill="black">Robot</text>

        {/* Movement line from Table A to Robot's current position */}
        <line x1="0.25" y1="0.25" x2={robotX} y2={robotY} stroke="red" strokeWidth="0.01" />
      </svg>
    </div>
  );
}

export default App;
