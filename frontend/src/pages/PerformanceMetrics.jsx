import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, XCircle, RefreshCw, Download } from 'lucide-react';
import { api } from '../services/api';

function PerformanceMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [normalizing, setNormalizing] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch('/api/performance/status');
      const data = await response.json();
      setStatus(data);
      
      if (data.status === 'available') {
        loadMetrics();
      } else {
        setLoading(false);
      }
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/performance/metrics');
      const data = await response.json();
      setMetrics(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const triggerEvaluation = async () => {
    setEvaluating(true);
    try {
      const response = await fetch('/api/performance/evaluate', { method: 'POST' });
      const data = await response.json();
      if (data.status === 'success') {
        setMetrics(data.results);
        setStatus({ ...status, status: 'available' });
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setEvaluating(false);
    }
  };

  const loadConfusionMatrix = async (normalize = false) => {
    try {
      const response = await fetch(`/api/performance/confusion-matrix?normalize=${normalize}`);
      const data = await response.json();
      setMetrics(prev => ({ ...prev, confusion_matrix: data.confusion_matrix, confusion_matrix_normalized: normalize }));
      setNormalizing(normalize);
    } catch (e) {
      setError(e.message);
    }
  };

  const exportResults = () => {
    if (!metrics) return;
    const dataStr = JSON.stringify(metrics, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'performance_metrics.json';
    link.click();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-gray-600">Loading performance metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center gap-2 text-red-800">
          <XCircle className="h-5 w-5" />
          <p className="font-semibold">Error loading performance metrics</p>
        </div>
        <p className="text-red-700 mt-2">{error}</p>
      </div>
    );
  }

  if (status && status.status === 'unavailable') {
    return (
      <div className="space-y-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <div className="flex items-center gap-2 text-yellow-800 mb-4">
            <AlertTriangle className="h-5 w-5" />
            <p className="font-semibold">Evaluation Not Available</p>
          </div>
          <p className="text-yellow-700 mb-4">{status.reason}</p>
          
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-medium">Model available:</span>
              <span className={status.model_available ? 'text-green-600' : 'text-red-600'}>
                {status.model_available ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Dataset available:</span>
              <span className={status.dataset_available ? 'text-green-600' : 'text-red-600'}>
                {status.dataset_available ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
          
          {!status.dataset_available && (
            <div className="mt-4 p-4 bg-yellow-100 rounded-lg">
              <p className="font-medium text-yellow-800 mb-2">Setup Required</p>
              <p className="text-yellow-700 text-sm">
                To enable performance evaluation, ensure the PTB-XL dataset is properly configured:
              </p>
              <ul className="text-yellow-700 text-sm mt-2 list-disc list-inside">
                <li>ptbxl_database.csv in project root</li>
                <li>records100/ directory with ECG files</li>
                <li>Trained model file at models/ptbxl_cnn_best.pt</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!metrics || metrics.status === 'unavailable') {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="section-title">Model Performance</h1>
          <button
            onClick={triggerEvaluation}
            disabled={evaluating}
            className="btn-primary"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${evaluating ? 'animate-spin' : ''}`} />
            {evaluating ? 'Running Evaluation...' : 'Run Evaluation'}
          </button>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center gap-2 text-blue-800">
            <Activity className="h-5 w-5" />
            <p className="font-semibold">Evaluation Not Yet Run</p>
          </div>
          <p className="text-blue-700 mt-2">
            Click "Run Evaluation" to calculate model performance metrics on the test dataset.
          </p>
        </div>
      </div>
    );
  }

  const overall = metrics.overall_metrics || {};
  const classMetrics = metrics.class_metrics || {};
  const datasetInfo = metrics.dataset_info || {};
  const evalInfo = metrics.evaluation_info || {};
  const confusionMatrix = metrics.confusion_matrix || [];
  const confusionLabels = metrics.confusion_matrix_labels || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="section-title">Model Performance Dashboard</h1>
        <div className="flex gap-2">
          <button
            onClick={triggerEvaluation}
            disabled={evaluating}
            className="btn-secondary"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${evaluating ? 'animate-spin' : ''}`} />
            {evaluating ? 'Evaluating...' : 'Re-evaluate'}
          </button>
          <button
            onClick={exportResults}
            className="btn-secondary"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Dataset Information */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Dataset Information</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Dataset</p>
            <p className="font-semibold">{datasetInfo.name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Split</p>
            <p className="font-semibold">{datasetInfo.split || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Samples</p>
            <p className="font-semibold">{datasetInfo.samples || 0}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Classes</p>
            <p className="font-semibold">{datasetInfo.classes?.length || 0}</p>
          </div>
        </div>
        
        {datasetInfo.class_distribution && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Class Distribution</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(datasetInfo.class_distribution).map(([cls, count]) => {
                const pct = datasetInfo.samples > 0 ? (count / datasetInfo.samples * 100).toFixed(1) : 0;
                return (
                  <span key={cls} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                    {cls}: {count} ({pct}%)
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Overall Metrics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Overall Metrics</h2>
        <div className="grid grid-cols-.md:grid-cols-4 gap-4">
          <MetricCard 
            label="Accuracy" 
            value={overall.accuracy ? (overall.accuracy * 100).toFixed(1) : 'N/A'} 
            suffix="%" 
          />
          <MetricCard 
            label="Precision (Macro)" 
            value={overall.precision_macro ? (overall.precision_macro * 100).toFixed(1) : 'N/A'} 
            suffix="%" 
          />
          <MetricCard 
            label="Recall (Macro)" 
            value={overall.recall_macro ? (overall.recall_macro * 100).toFixed(1) : 'N/A'} 
            suffix="%" 
          />
          <MetricCard 
            label="F1 (Macro)" 
            value={overall.f1_macro ? (overall.f1_macro * 100).toFixed(1) : 'N/A'} 
            suffix="%" 
          />
        </div>
        
        {overall.averaging_method && (
          <p className="text-sm text-gray-500 mt-4">
            Averaging method: {overall.averaging_method}
          </p>
        )}
        
        {metrics.roc_auc !== null && metrics.roc_auc !== undefined && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="font-semibold text-green-800">ROC-AUC: {(metrics.roc_auc * 100).toFixed(1)}%</p>
          </div>
        )}
      </div>

      {/* Per-Class Metrics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Per-Class Metrics</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4">Class</th>
                <th className="text-right py-2 px-4">Precision</th>
                <th className="text-right py-2 px-4">Recall</th>
                <th className="text-right py-2 px-4">F1</th>
                <th className="text-right py-2 px-4">Sensitivity</th>
                <th className="text-right py-2 px-4">Specificity</th>
                <th className="text-right py-2 px-4">Support</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(classMetrics).map(([cls, metrics]) => (
                <tr key={cls} className="border-b">
                  <td className="py-2 px-4 font-medium">{cls}</td>
                  <td className="text-right py-2 px-4">{(metrics.precision * 100).toFixed(1)}%</td>
                  <td className="text-right py-2 px-4">{(metrics.recall * 100).toFixed(1)}%</td>
                  <td className="text-right py-2 px-4">{(metrics.f1 * 100).toFixed(1)}%</td>
                  <td className="text-right py-2 px-4">{(metrics.sensitivity * 100).toFixed(1)}%</td>
                  <td className="text-right py-2 px-4">{(metrics.specificity * 100).toFixed(1)}%</td>
                  <td className="text-right py-2 px-4">{metrics.support}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confusion Matrix */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">Confusion Matrix</h2>
          <button
            onClick={() => loadConfusionMatrix(!normalizing)}
            className="btn-secondary !py-1.5 !text-xs"
          >
            {normalizing ? 'Show Counts' : 'Show Percentages'}
          </button>
        </div>
        
        {confusionMatrix.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="py-2 px-4"></th>
                  {confusionLabels.map(label => (
                    <th key={label} className="py-2 px-4 text-center">{label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {confusionMatrix.map((row, i) => (
                  <tr key={i}>
                    <td className="py-2 px-4 font-medium">{confusionLabels[i]}</td>
                    {row.map((val, j) => {
                      const maxValue = Math.max(...confusionMatrix.flat());
                      const intensity = normalizing ? val : (val / maxValue);
                      const bgColor = normalizing 
                        ? `rgba(59, 130, 246, ${intensity})`
                        : `rgba(59, 130, 246, ${intensity * 0.8})`;
                      const textColor = intensity > 0.5 ? 'white' : 'black';
                      const displayValue = normalizing ? (val * 100).toFixed(1) + '%' : val;
                      
                      return (
                        <td 
                          key={j} 
                          className="py-2 px-4 text-center"
                          style={{ backgroundColor: bgColor, color: textColor }}
                        >
                          {displayValue}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">Confusion matrix not available</p>
        )}
        
        <p className="text-sm text-gray-500 mt-2">
          Rows: Actual | Columns: Predicted
        </p>
      </div>

      {/* Evaluation Information */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Evaluation Information</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Timestamp</p>
            <p className="font-medium">{evalInfo.timestamp || 'N/A'}</p>
          </div>
          <div>
            <p className="text-gray-600">Model Version</p>
            <p className="font-medium">{evalInfo.model_version || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <div className="flex items-start gap-2">
          <AlertTriangle className="h-5 w-5 text-yellow-700 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-800">Important Notes</h3>
            <ul className="text-yellow-700 text-sm mt-2 list-disc list-inside space-y-1">
              <li>These metrics are calculated from actual model predictions on the PTB-XL test dataset</li>
              <li>Results are for research and educational purposes only</li>
              <li>This is not a clinical validation and should not be used for medical decision-making</li>
              <li>Performance may vary on different populations and clinical settings</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, suffix = '' }) {
  return (
    <div className="bg-blue-50 rounded-lg p-4">
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-2xl font-bold text-blue-600">
        {value}{suffix}
      </p>
    </div>
  );
}

export default PerformanceMetrics;
