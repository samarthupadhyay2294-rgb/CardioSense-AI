import React from 'react';
import { AlertTriangle, CheckCircle, Info, Activity, AlertCircle } from 'lucide-react';

function ClinicalInterpreter({ interpretation }) {
  if (!interpretation) return null;

  const urgencyColors = {
    emergency: 'bg-red-50 border-red-500 text-red-800',
    urgent: 'bg-orange-50 border-orange-500 text-orange-800',
    routine: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    none: 'bg-green-50 border-green-500 text-green-800'
  };

  const urgencyIcons = {
    emergency: AlertTriangle,
    urgent: AlertTriangle,
    routine: Info,
    none: CheckCircle
  };

  const UrgencyIcon = urgencyIcons[interpretation.urgency] || Info;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Clinical Interpretation</h2>
      
      {/* Clinical Significance */}
      <div className={`mb-6 p-4 rounded-lg border-l-4 ${urgencyColors[interpretation.urgency]}`}>
        <div className="flex items-start gap-3">
          <UrgencyIcon className="mt-1 flex-shrink-0 w-5 h-5" />
          <div>
            <h3 className="font-semibold mb-2">Clinical Significance</h3>
            <p className="text-sm">{interpretation.clinical_significance}</p>
          </div>
        </div>
      </div>
      
      {/* Prediction Context */}
      {interpretation.prediction_context && (
        <div className="mb-6 bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold mb-3 flex items-center gap-2 text-sm">
            <Activity className="text-blue-500 w-4 h-4" />
            Prediction Context
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Prediction:</span>
              <span className="ml-2 font-medium">{interpretation.prediction_context.prediction}</span>
            </div>
            <div>
              <span className="text-gray-600">Confidence:</span>
              <span className="ml-2 font-medium">
                {(interpretation.prediction_context.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-gray-600">Confidence Level:</span>
              <span className="ml-2 font-medium capitalize">
                {interpretation.prediction_context.confidence_level}
              </span>
            </div>
          </div>
        </div>
      )}
      
      {/* Primary Findings */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Activity className="text-blue-500 w-4 h-4" />
          Primary Findings
        </h3>
        <ul className="space-y-2">
          {interpretation.primary_findings.map((finding, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <span className="text-blue-500 mt-1">•</span>
              <span>{finding}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Secondary Findings */}
      {interpretation.secondary_findings && interpretation.secondary_findings.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Info className="text-purple-500 w-4 h-4" />
            <span>Additional Findings</span>
          </h3>
          <ul className="space-y-2">
            {interpretation.secondary_findings.map((finding, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="text-purple-500 mt-1">•</span>
                <span>{finding}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Recommendations */}
      <div className="mb-6">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <CheckCircle className="text-green-500 w-4 h-4" />
          Recommendations
        </h3>
        <ol className="space-y-2">
          {interpretation.recommendations.map((recommendation, index) => (
            <li key={index} className="flex items-start gap-2 text-sm">
              <span className="bg-green-100 text-green-800 rounded-full w-5 h-5 flex items-center justify-center text-xs flex-shrink-0">
                {index + 1}
              </span>
              <span>{recommendation}</span>
            </li>
          ))}
        </ol>
      </div>
      
      {/* Differential Diagnosis */}
      {interpretation.differential_diagnosis && interpretation.differential_diagnosis.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3">Differential Diagnosis</h3>
          <div className="flex flex-wrap gap-2">
            {interpretation.differential_diagnosis.map((diagnosis, index) => (
              <span key={index} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                {diagnosis}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Limitations */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-semibold mb-2 text-yellow-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          Limitations & Disclaimer
        </h3>
        <ul className="space-y-1 text-sm text-yellow-700">
          {interpretation.limitations.map((limitation, index) => (
            <li key={index} className="flex items-start gap-2">
              <span>⚠️</span>
              <span>{limitation}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default ClinicalInterpreter;
