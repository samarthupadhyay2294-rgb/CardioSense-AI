import React, { useState } from 'react';
import { Play, Download, RotateCcw } from 'lucide-react';

function ECGSimulator() {
  const [params, setParams] = useState({
    abnormality: 'normal',
    heartRate: 70,
    noiseLevel: 0.0,
    baselineWander: false,
    duration: 10
  });
  const [generatedSignal, setGeneratedSignal] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/simulation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          abnormality: params.abnormality,
          heart_rate: params.heartRate,
          noise_level: params.noiseLevel,
          baseline_wander: params.baselineWander,
          duration: params.duration
        })
      });
      const data = await response.json();
      setGeneratedSignal(data);
      setAnalysisResult(null);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!generatedSignal) return;
    setLoading(true);
    try {
      const response = await fetch('/api/simulation/generate-and-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          abnormality: params.abnormality,
          heart_rate: params.heartRate,
          noise_level: params.noiseLevel,
          baseline_wander: params.baselineWander,
          duration: params.duration
        })
      });
      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setParams({
      abnormality: 'normal',
      heartRate: 70,
      noiseLevel: 0.0,
      baselineWander: false,
      duration: 10
    });
    setGeneratedSignal(null);
    setAnalysisResult(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">ECG Simulator</h2>
        <button 
          onClick={handleReset}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
        >
          <RotateCcw size={16} /> Reset
        </button>
      </div>

      {/* Educational Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-yellow-800">
          <strong>Educational/Research Use Only:</strong> This simulator generates mathematical ECG signals for testing and educational purposes. 
          These are NOT real patient recordings and should NOT be used for clinical diagnosis.
        </p>
      </div>

      {/* Parameter Controls */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Abnormality Type</label>
          <select 
            value={params.abnormality}
            onChange={(e) => setParams({...params, abnormality: e.target.value})}
            className="w-full border rounded p-2"
          >
            <option value="normal">Normal</option>
            <option value="MI">Myocardial Infarction</option>
            <option value="STTC">ST/T Changes</option>
            <option value="CD">Conduction Disturbance</option>
            <option value="HYP">Hypertrophy</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Heart Rate (BPM)</label>
          <input 
            type="range" min="40" max="120" value={params.heartRate}
            onChange={(e) => setParams({...params, heartRate: parseInt(e.target.value)})}
            className="w-full"
          />
          <span className="text-sm">{params.heartRate} BPM</span>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Noise Level</label>
          <input 
            type="range" min="0" max="0.2" step="0.01" value={params.noiseLevel}
            onChange={(e) => setParams({...params, noiseLevel: parseFloat(e.target.value)})}
            className="w-full"
          />
          <span className="text-sm">{params.noiseLevel}</span>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Duration (seconds)</label>
          <input 
            type="range" min="5" max="30" step="1" value={params.duration}
            onChange={(e) => setParams({...params, duration: parseInt(e.target.value)})}
            className="w-full"
          />
          <span className="text-sm">{params.duration}s</span>
        </div>
        <div className="col-span-2 flex items-center">
          <label className="flex items-center gap-2">
            <input 
              type="checkbox" checked={params.baselineWander}
              onChange={(e) => setParams({...params, baselineWander: e.target.checked})}
            />
            <span className="text-sm">Add Baseline Wander</span>
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button 
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          <Play size={20} /> {loading ? 'Generating...' : 'Generate ECG'}
        </button>
        <button 
          onClick={handleAnalyze}
          disabled={loading || !generatedSignal}
          className="flex items-center gap-2 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:bg-gray-300"
        >
          <Download size={20} /> {loading ? 'Analyzing...' : 'Analyze ECG'}
        </button>
      </div>

      {/* Generated Signal Info */}
      {generatedSignal && (
        <div className="mb-6 border rounded p-4 bg-blue-50">
          <h3 className="font-semibold mb-2">Generated Signal Information</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><span className="text-gray-600">Sampling Rate:</span> {generatedSignal.metadata.sampling_rate} Hz</div>
            <div><span className="text-gray-600">Duration:</span> {generatedSignal.metadata.duration}s</div>
            <div><span className="text-gray-600">Number of Leads:</span> {generatedSignal.metadata.num_leads}</div>
            <div><span className="text-gray-600">Samples:</span> {generatedSignal.metadata.num_samples}</div>
            <div><span className="text-gray-600">Abnormality:</span> {params.abnormality}</div>
            <div><span className="text-gray-600">Heart Rate:</span> {params.heartRate} BPM</div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <div className="border rounded p-4 bg-green-50">
          <h3 className="font-semibold mb-2">Analysis Results</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600">Prediction:</span>
              <span className="font-bold ml-2">{analysisResult.prediction.prediction}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className="font-bold ml-2">{(analysisResult.prediction.confidence * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Signal Quality:</span>
              <span className="font-bold ml-2 capitalize">{analysisResult.signal_quality}</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Processing Time:</span>
              <span className="font-bold ml-2">{analysisResult.prediction.processing_time}s</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ECGSimulator;