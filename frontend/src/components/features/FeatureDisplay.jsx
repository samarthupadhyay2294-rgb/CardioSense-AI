import React, { useState } from 'react';
import { Activity, Waves, BarChart3 } from 'lucide-react';

function FeatureDisplay({ features }) {
  const [selectedLead, setSelectedLead] = useState('II');
  
  if (!features) return null;

  const temporalFeatures = features.temporal || {};
  const frequencyFeatures = features.frequency || {};
  const morphologicalFeatures = features.morphological || {};
  const leadNames = Object.keys(temporalFeatures);

  const selectedTemporal = temporalFeatures[selectedLead] || {};
  const selectedFrequency = frequencyFeatures[selectedLead] || {};
  const selectedMorphological = morphologicalFeatures[selectedLead] || {};

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">ECG Feature Analysis</h2>
        
        {/* Lead Selector */}
        <div>
          <label className="block text-sm font-medium mb-2">Select Lead</label>
          <select 
            value={selectedLead}
            onChange={(e) => setSelectedLead(e.target.value)}
            className="border rounded p-2"
          >
            {leadNames.map(lead => (
              <option key={lead} value={lead}>{lead}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Temporal Features */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="text-blue-500" />
          <h3 className="text-lg font-semibold">Temporal Features - Lead {selectedLead}</h3>
        </div>
        
        {selectedTemporal.heart_rate && (
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-xs text-gray-600">Mean HR</div>
              <div className="font-bold">{selectedTemporal.heart_rate.mean?.toFixed(0)} BPM</div>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-xs text-gray-600">Min HR</div>
              <div className="font-bold">{selectedTemporal.heart_rate.min?.toFixed(0)} BPM</div>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-xs text-gray-600">Max HR</div>
              <div className="font-bold">{selectedTemporal.heart_rate.max?.toFixed(0)} BPM</div>
            </div>
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-xs text-gray-600">HR Std</div>
              <div className="font-bold">{selectedTemporal.heart_rate.std?.toFixed(1)}</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4">
          {selectedTemporal.qrs_features && (
            <div className="border rounded p-3 bg-blue-50">
              <h4 className="font-bold text-sm mb-2">QRS Features</h4>
              <div className="space-y-1 text-xs">
                <div>Duration: {selectedTemporal.qrs_features.duration?.toFixed(3)}s</div>
                <div>Amplitude: {selectedTemporal.qrs_features.amplitude?.toFixed(3)} mV</div>
                {selectedTemporal.qrs_features.estimated && (
                  <div className="text-yellow-600">*Estimated</div>
                )}
              </div>
            </div>
          )}
          
          {selectedTemporal.st_segment && (
            <div className="border rounded p-3 bg-blue-50">
              <h4 className="font-bold text-sm mb-2">ST Segment</h4>
              <div className="space-y-1 text-xs">
                <div>Elevation: {selectedTemporal.st_segment.elevation?.toFixed(3)} mV</div>
                <div>Depression: {selectedTemporal.st_segment.depression?.toFixed(3)} mV</div>
                {selectedTemporal.st_segment.estimated && (
                  <div className="text-yellow-600">*Estimated</div>
                )}
              </div>
            </div>
          )}
          
          <div className="border rounded p-3 bg-blue-50">
            <h4 className="font-bold text-sm mb-2">Intervals</h4>
            <div className="space-y-1 text-xs">
              <div>PR: {selectedTemporal.pr_interval?.toFixed(3)}s</div>
              <div>QT: {selectedTemporal.qt_interval?.toFixed(3)}s</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Frequency Features */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Waves className="text-green-500" />
          <h3 className="text-lg font-semibold">Frequency Features - Lead {selectedLead}</h3>
        </div>
        
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-green-50 p-3 rounded">
            <div className="text-xs text-gray-600">Dominant Freq</div>
            <div className="font-bold">{selectedFrequency.dominant_frequency?.toFixed(1)} Hz</div>
          </div>
          <div className="bg-green-50 p-3 rounded">
            <div className="text-xs text-gray-600">Spectral Entropy</div>
            <div className="font-bold">{selectedFrequency.spectral_entropy?.toFixed(3)}</div>
          </div>
          <div className="bg-green-50 p-3 rounded">
            <div className="text-xs text-gray-600">Total Power</div>
            <div className="font-bold">{selectedFrequency.total_power?.toExponential(2)}</div>
          </div>
          <div className="bg-green-50 p-3 rounded">
            <div className="text-xs text-gray-600">Band Power</div>
            <div className="font-bold text-xs">
              {selectedFrequency.band_power?.medium?.toExponential(2)}
            </div>
          </div>
        </div>
      </div>
      
      {/* Morphological Features */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="text-purple-500" />
          <h3 className="text-lg font-semibold">Morphological Features - Lead {selectedLead}</h3>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">Mean</div>
            <div className="font-bold">{selectedMorphological.mean?.toFixed(4)}</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">Std Dev</div>
            <div className="font-bold">{selectedMorphological.std?.toFixed(4)}</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">RMS</div>
            <div className="font-bold">{selectedMorphological.rms?.toFixed(4)}</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">Skewness</div>
            <div className="font-bold">{selectedMorphological.skewness?.toFixed(3)}</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">Kurtosis</div>
            <div className="font-bold">{selectedMorphological.kurtosis?.toFixed(3)}</div>
          </div>
          <div className="bg-purple-50 p-3 rounded">
            <div className="text-xs text-gray-600">Zero Crossings</div>
            <div className="font-bold">{selectedMorphological.zero_crossings}</div>
          </div>
        </div>
      </div>

      {/* Feature Estimation Disclaimer */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Feature Estimation:</strong> Temporal features (QRS, ST segment, intervals) are estimated signal features 
          using basic signal processing algorithms. They are NOT clinically validated measurements and should be 
          interpreted as approximate signal characteristics for educational/research purposes only.
        </p>
      </div>
    </div>
  );
}

export default FeatureDisplay;