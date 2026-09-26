import React, { useState, useRef } from 'react';
import { Upload, Play, Download, Filter, Search, XCircle, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

function BatchAnalysis() {
  const [files, setFiles] = useState([]);
  const [batchResult, setBatchResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, success, failed
  const [predictionFilter, setPredictionFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedResult, setSelectedResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selected = Array.from(e.target.files);
    setFiles(prev => [...prev, ...selected]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (files.length === 0) return;

    setProcessing(true);
    setError(null);
    setBatchResult(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('/api/batch/analyze', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Batch analysis failed');
      }

      setBatchResult(data);
      setFiles([]);
    } catch (e) {
      setError(e.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleExportCSV = async () => {
    if (!batchResult) return;

    try {
      const url = `/api/batch/${batchResult.batch_id}/export/csv?status_filter=${filter !== 'all' ? filter : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) throw new Error('Export failed');
      
      const blob = await response.blob();
      const urlObj = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = urlObj;
      link.download = `batch_results_${batchResult.batch_id}.csv`;
      link.click();
      URL.revokeObjectURL(urlObj);
    } catch (e) {
      setError(e.message);
    }
  };

  const handleExportJSON = async () => {
    if (!batchResult) return;

    try {
      const url = `/api/batch/${batchResult.batch_id}/export/json?status_filter=${filter !== 'all' ? filter : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) throw new Error('Export failed');
      
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const urlObj = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = urlObj;
      link.download = `batch_results_${batchResult.batch_id}.json`;
      link.click();
      URL.revokeObjectURL(urlObj);
    } catch (e) {
      setError(e.message);
    }
  };

  const getFilteredResults = () => {
    if (!batchResult) return [];

    let results = batchResult.results;

    // Status filter
    if (filter !== 'all') {
      results = results.filter(r => r.status === filter);
    }

    // Prediction filter
    if (predictionFilter !== 'all') {
      results = results.filter(r => r.prediction_code === predictionFilter);
    }

    // Search filter
    if (searchTerm) {
      results = results.filter(r => 
        r.file_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return results;
  };

  const filteredResults = getFilteredResults();

  return (
    <div className="space-y-6">
      <h1 className="section-title">Batch ECG Analysis</h1>

      {/* Upload Section */}
      {!batchResult && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Upload ECG Files</h2>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              ref={fileInputRef}
              multiple
              accept=".mat,.csv,.npy,.txt,.dat,.hea"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600 mb-4">
              Select ECG files for batch analysis
            </p>
            <button
              onClick={() => fileInputRef.current.click()}
              className="btn-primary"
            >
              Select Files
            </button>
            <p className="text-sm text-gray-500 mt-2">
              Supported formats: MAT, CSV, NPY, TXT, WFDB (DAT/HEA)
            </p>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-3">
                <h3 className="font-semibold">Selected Files ({files.length})</h3>
                <button
                  onClick={() => setFiles([])}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Clear All
                </button>
              </div>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
                    <span className="text-sm truncate flex-1">{file.name}</span>
                    <span className="text-xs text-gray-500 ml-2">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                    <button
                      onClick={() => removeFile(index)}
                      className="ml-2 text-red-500 hover:text-red-700"
                    >
                      <XCircle className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>

              <button
                onClick={handleAnalyze}
                disabled={processing}
                className="btn-primary w-full mt-4"
              >
                {processing ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Analyze {files.length} Files
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <p className="font-semibold">Error</p>
          </div>
          <p className="text-red-700 mt-1">{error}</p>
        </div>
      )}

      {/* Results */}
      {batchResult && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">Batch Results</h2>
                <p className="text-sm text-gray-600">Batch ID: {batchResult.batch_id}</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleExportCSV}
                  className="btn-secondary"
                >
                  <Download className="h-4 w-4 mr-2" />
                  CSV
                </button>
                <button
                  onClick={handleExportJSON}
                  className="btn-secondary"
                >
                  <Download className="h-4 w-4 mr-2" />
                  JSON
                </button>
                <button
                  onClick={() => {
                    setBatchResult(null);
                    setFiles([]);
                  }}
                  className="btn-secondary"
                >
                  New Batch
                </button>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 mt-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Total Files</p>
                <p className="text-2xl font-bold text-blue-600">{batchResult.total_files}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Successful</p>
                <p className="text-2xl font-bold text-green-600">{batchResult.successful}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-red-600">{batchResult.failed}</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {((batchResult.successful / batchResult.total_files) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">Status:</span>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="border rounded-lg px-3 py-1.5 text-sm"
                >
                  <option value="all">All</option>
                  <option value="success">Successful</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Prediction:</span>
                <select
                  value={predictionFilter}
                  onChange={(e) => setPredictionFilter(e.target.value)}
                  className="border rounded-lg px-3 py-1.5 text-sm"
                >
                  <option value="all">All</option>
                  <option value="NORM">NORM</option>
                  <option value="MI">MI</option>
                  <option value="STTC">STTC</option>
                  <option value="CD">CD</option>
                  <option value="HYP">HYP</option>
                </select>
              </div>

              <div className="flex items-center gap-2 flex-1">
                <Search className="h-4 w-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search by filename..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="border rounded-lg px-3 py-1.5 text-sm flex-1"
                />
              </div>
            </div>
          </div>

          {/* Results Table */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">
              Results ({filteredResults.length} displayed)
            </h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">File</th>
                    <th className="text-left py-2 px-4">Status</th>
                    <th className="text-left py-2 px-4">Prediction</th>
                    <th className="text-right py-2 px-4">Confidence</th>
                    <th className="text-left py-2 px-4">Signal Quality</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map((result, index) => (
                    <tr 
                      key={index} 
                      className="border-b hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedResult(result)}
                    >
                      <td className="py-2 px-4">{result.file_name}</td>
                      <td className="py-2 px-4">
                        {result.status === 'success' ? (
                          <span className="flex items-center gap-1 text-green-600">
                            <CheckCircle className="h-4 w-4" />
                            Success
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600">
                            <XCircle className="h-4 w-4" />
                            Failed
                          </span>
                        )}
                      </td>
                      <td className="py-2 px-4">
                        {result.status === 'success' ? result.prediction : '-'}
                      </td>
                      <td className="text-right py-2 px-4">
                        {result.status === 'success' 
                          ? (result.confidence * 100).toFixed(1) + '%' 
                          : '-'}
                      </td>
                      <td className="py-2 px-4">
                        {result.status === 'success' ? result.signal_quality : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredResults.length === 0 && (
              <p className="text-center text-gray-500 py-8">No results match the current filters</p>
            )}
          </div>

          {/* Selected Result Detail */}
          {selectedResult && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-gray-800">
                  {selectedResult.file_name}
                </h3>
                <button
                  onClick={() => setSelectedResult(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <XCircle className="h-5 w-5" />
                </button>
              </div>

              {selectedResult.status === 'success' ? (
                <div className="space-y-4">
                  {/* Prediction */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-semibold mb-2">Prediction</h4>
                    <p className="text-lg font-bold">{selectedResult.prediction}</p>
                    <p className="text-sm text-gray-600">
                      Confidence: {(selectedResult.confidence * 100).toFixed(1)}%
                    </p>
                  </div>

                  {/* Features Summary */}
                  {selectedResult.detailed_features && (
                    <div>
                      <h4 className="font-semibold mb-2">Features</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {selectedResult.detailed_features.temporal?.II && (
                          <div>
                            <span className="text-gray-600">Heart Rate:</span>
                            <span className="ml-2 font-medium">
                              {selectedResult.detailed_features.temporal.II.heart_rate?.mean?.toFixed(0)} bpm
                            </span>
                          </div>
                        )}
                        <div>
                          <span className="text-gray-600">Signal Quality:</span>
                          <span className="ml-2 font-medium">{selectedResult.signal_quality}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Interpretation Summary */}
                  {selectedResult.clinical_interpretation && (
                    <div>
                      <h4 className="font-semibold mb-2">Clinical Interpretation</h4>
                      <div className="bg-yellow-50 rounded-lg p-4">
                        <p className="text-sm text-gray-700 mb-2">
                          <span className="font-medium">Urgency:</span> {selectedResult.clinical_interpretation.urgency}
                        </p>
                        <p className="text-sm text-gray-700 mb-2">
                          <span className="font-medium">Finding:</span> {selectedResult.clinical_interpretation.primary_findings[0]}
                        </p>
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">Recommendation:</span> {selectedResult.clinical_interpretation.recommendations[0]}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-red-50 rounded-lg p-4">
                  <h4 className="font-semibold text-red-800 mb-2">Processing Failed</h4>
                  <p className="text-sm text-red-700">
                    <span className="font-medium">Error Type:</span> {selectedResult.error_type}
                  </p>
                  <p className="text-sm text-red-700">
                    <span className="font-medium">Message:</span> {selectedResult.error}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BatchAnalysis;
