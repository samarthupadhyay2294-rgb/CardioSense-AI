import React from 'react';
import Layout from '../components/layout/Layout';
import ECGSimulator from '../components/simulation/ECGSimulator';

function Simulation() {
  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <ECGSimulator />
      </div>
    </Layout>
  );
}

export default Simulation;