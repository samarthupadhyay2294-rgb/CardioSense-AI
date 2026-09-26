import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import { useTheme } from '../../context/ThemeContext';

const LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];

const LEAD_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8B500', '#52B788'
];

function ECG12LeadGrid({ signalData, samplingRate = 100 }) {
  const { theme } = useTheme();
  const [selectedLead, setSelectedLead] = useState(null);
  const isDark = theme === 'dark';

  const textColor = '#475569';
  const gridColor = 'rgba(148,163,184,0.25)';

  const createLeadPlot = (leadIndex, leadName, plotHeight = 160) => {
    const leadSignal = signalData[leadIndex] || [];
    const time = Array.from({ length: leadSignal.length }, (_, i) => i / samplingRate);
    
    return {
      data: [{
        x: time,
        y: leadSignal,
        type: 'scatter',
        mode: 'lines',
        line: { 
          color: LEAD_COLORS[leadIndex],
          width: 1.5
        },
        name: leadName,
        hovertemplate: `${leadName}: %{y:.3f} mV<extra></extra>`
      }],
      layout: {
        title: {
          text: leadName,
          font: { size: 14, weight: 'bold', color: textColor, family: 'Inter, sans-serif' }
        },
        xaxis: {
          title: { text: 'Time (s)', font: { color: textColor, size: 10 } },
          showgrid: true,
          gridcolor: gridColor,
          zerolinecolor: gridColor,
          tickfont: { color: textColor, size: 9 },
          fixedrange: true
        },
        yaxis: {
          title: { text: 'Amplitude (mV)', font: { color: textColor, size: 10 } },
          showgrid: true,
          gridcolor: gridColor,
          zerolinecolor: gridColor,
          tickfont: { color: textColor, size: 9 },
          fixedrange: true
        },
        margin: { t: 30, r: 12, b: 40, l: 50 },
        height: plotHeight,
        showlegend: false,
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff'
      },
      config: {
        responsive: true,
        displayModeBar: false,
        displaylogo: false,
        staticPlot: false
      }
    };
  };

  const standardLayout = [
    ['I', 'II', 'III'],
    ['aVR', 'aVL', 'aVF'],
    ['V1', 'V2', 'V3'],
    ['V4', 'V5', 'V6']
  ];

  return (
    <div className="ecg-lead-grid rounded-lg p-2" style={{ background: '#ffffff' }}>
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-lg font-bold" style={{ color: '#1e293b' }}>12-Lead ECG Display</h2>
        <div className="flex gap-2">
          <button 
            onClick={() => setSelectedLead(null)}
            className="px-3 py-1 rounded text-sm hover:opacity-80"
            style={{ background: '#e2e8f0', color: '#475569' }}
          >
            Reset View
          </button>
        </div>
      </div>

      {/* Standard 3x4 Grid Layout */}
      <div className="ecg-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '10px',
        width: '100%',
        maxWidth: '100%',
        boxSizing: 'border-box'
      }}>
        {standardLayout.flat().map((leadName) => {
          const leadIndex = LEAD_NAMES.indexOf(leadName);
          return (
            <div 
              key={leadName}
              className={`rounded-lg cursor-pointer transition-all ${
                selectedLead === leadIndex ? 'ring-2 ring-blue-500' : ''
              }`}
              style={{
                border: '1px solid #e2e8f0',
                padding: '4px',
                background: '#ffffff',
                minWidth: 0,
                overflow: 'hidden'
              }}
              onClick={() => setSelectedLead(leadIndex)}
            >
              <Plot {...createLeadPlot(leadIndex, leadName)} />
            </div>
          );
        })}
      </div>

      {/* Enlarged Single Lead View */}
      {selectedLead !== null && (
        <div className="mt-4 rounded-lg p-4" style={{ border: '1px solid #bfdbfe', background: '#eff6ff' }}>
          <h3 className="font-semibold mb-2" style={{ color: '#1e293b' }}>Enlarged View: {LEAD_NAMES[selectedLead]}</h3>
          <Plot {...{
            ...createLeadPlot(selectedLead, LEAD_NAMES[selectedLead], 280),
            layout: {
              ...createLeadPlot(selectedLead, LEAD_NAMES[selectedLead]).layout,
              height: 280,
              fixedrange: false
            }
          }} />
        </div>
      )}

      {/* Lead Information Panel */}
      <div className="mt-3 grid grid-cols-4 gap-2 text-sm">
        {LEAD_NAMES.map((name, index) => (
          <div key={name} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-sm"
              style={{ backgroundColor: LEAD_COLORS[index] }}
            />
            <span className="font-medium" style={{ color: '#334155', fontSize: '12px' }}>{name}</span>
          </div>
        ))}
      </div>

      {/* Clinical Format Disclaimer */}
      <div className="mt-3 rounded-lg p-3" style={{ background: '#fffbeb', border: '1px solid #fde68a' }}>
        <p style={{ fontSize: '11px', color: '#92400e' }}>
          <strong>Clinical Display Format:</strong> This 12-lead grid follows standard clinical presentation. 
          Leads are displayed in the conventional format used in medical practice for educational/research purposes.
        </p>
      </div>
    </div>
  );
}

export default ECG12LeadGrid;
