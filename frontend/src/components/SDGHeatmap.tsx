import React from 'react';

// Mock Data Structure for Heatmap
// Rows: Departments
// Columns: SDGs (1-17)
// Value: Activity Score (0-100)

interface HeatmapData {
  department: string;
  scores: { [sdg: number]: number };
}

const DEPARTMENTS = [
  "Finance",
  "Accountancy",
  "Business Admin",
  "Economics",
  "Marketing"
];

const MOCK_HEATMAP_DATA: HeatmapData[] = [
  {
    department: "Finance",
    scores: { 1: 10, 7: 90, 8: 60, 13: 40, 17: 20 }
  },
  {
    department: "Accountancy",
    scores: { 8: 50, 12: 85, 13: 70, 16: 30 }
  },
  {
    department: "Business Admin",
    scores: { 3: 40, 5: 60, 8: 80, 9: 75, 12: 50 }
  },
  {
    department: "Economics",
    scores: { 1: 80, 8: 90, 10: 70, 13: 30 }
  },
  {
    department: "Marketing",
    scores: { 3: 30, 12: 90, 13: 20 }
  }
];

const SDG_LABELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17];

export default function SDGHeatmap() {
  
  const getColor = (score: number) => {
    if (!score) return '#f8f9fa'; // Empty
    if (score >= 80) return '#2ecc71'; // High - Green
    if (score >= 50) return '#f1c40f'; // Medium - Yellow
    return '#e74c3c'; // Low - Red
  };

  const getOpacity = (score: number) => {
      if (!score) return 1;
      // Scale opacity based on score for a "heat" effect
      return 0.3 + (score / 100) * 0.7;
  };

  return (
    <div className="card" style={{ overflowX: 'auto' }}>
      <h3 className="card-title">Cross-Departmental Impact Matrix</h3>
      <p className="card-subtitle mb-3">Heatmap of research activity by SDG and Department</p>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left', padding: '10px', borderBottom: '2px solid var(--color-border)' }}>Department</th>
            {SDG_LABELS.map(sdg => (
              <th key={sdg} style={{ padding: '10px', fontSize: '12px', borderBottom: '2px solid var(--color-border)' }}>
                SDG {sdg}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {MOCK_HEATMAP_DATA.map((row, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid var(--color-border)' }}>
              <td style={{ padding: '10px', fontWeight: 600, fontSize: '14px' }}>{row.department}</td>
              {SDG_LABELS.map(sdg => {
                const score = row.scores[sdg] || 0;
                return (
                  <td key={sdg} style={{ padding: '4px' }}>
                    <div 
                      title={`Score: ${score}`}
                      style={{ 
                        height: '30px', 
                        width: '100%', 
                        backgroundColor: getColor(score),
                        opacity: getOpacity(score),
                        borderRadius: '4px'
                      }}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      
      <div style={{ display: 'flex', gap: '16px', marginTop: '16px', fontSize: '12px', color: 'var(--color-text-light)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#2ecc71', borderRadius: '2px' }}></div> High Activity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#f1c40f', borderRadius: '2px' }}></div> Medium Activity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: '#e74c3c', borderRadius: '2px' }}></div> Nascent
        </div>
      </div>
    </div>
  );
}
