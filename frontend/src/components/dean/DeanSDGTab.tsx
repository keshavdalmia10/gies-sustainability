import React, { useEffect, useState } from 'react';
import SDGHeatmap from '../SDGHeatmap';
import { SDGDistributionChart, SDGData } from '../AnalyticsCharts';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip 
} from 'recharts';

const RADAR_DATA = [
  { subject: 'SDG 1: Poverty', A: 120, fullMark: 150 },
  { subject: 'SDG 3: Health', A: 40, fullMark: 150 },
  { subject: 'SDG 5: Gender', A: 60, fullMark: 150 },
  { subject: 'SDG 7: Energy', A: 145, fullMark: 150 },
  { subject: 'SDG 8: Work', A: 130, fullMark: 150 },
  { subject: 'SDG 9: Industry', A: 100, fullMark: 150 },
  { subject: 'SDG 13: Climate', A: 110, fullMark: 150 },
];

export default function DeanSDGTab() {
  const [sdgData, setSdgData] = useState<SDGData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/analytics/sdg/distribution');
        const json = await res.json();
        setSdgData(json);
      } catch (error) {
        console.error("Failed to fetch SDG data", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      {/* UN SDG Distribution Chart */}
      <div className="card mb-4">
        <h3 className="card-title">UN Sustainable Development Goals Distribution</h3>
        <p className="card-subtitle mb-3">Total mentions of each UN SDG across all articles</p>
        <SDGDistributionChart data={sdgData} />
      </div>

      <div className="grid grid-2 mb-4">
        {/* Radar Chart - Portfolio Balance */}
        <div className="card">
          <h3 className="card-title">Impact Portfolio Shape</h3>
          <p className="card-subtitle mb-3">Visualizing the balance of research across key SDGs</p>
          <div style={{ height: '350px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={RADAR_DATA}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={30} domain={[0, 150]} />
                <Radar name="Research Output" dataKey="A" stroke="#0066cc" fill="#0066cc" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Context/Explanation */}
        <div className="card">
          <h3 className="card-title">Portfolio Analysis</h3>
          <p className="card-subtitle mb-3">Key takeaways from the data</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ padding: '12px', backgroundColor: '#f0f9ff', borderRadius: '8px', borderLeft: '4px solid #0066cc' }}>
              <strong>Strong Economic Focus:</strong> The portfolio is heavily weighted towards economic SDGs (1, 8, 9), reflecting the Business School's core strengths.
            </div>
            <div style={{ padding: '12px', backgroundColor: '#f0fff4', borderRadius: '8px', borderLeft: '4px solid #2ecc71' }}>
              <strong>Energy Leadership:</strong> SDG 7 is a standout peak, driven by the new "Green Finance" initiative.
            </div>
            <div style={{ padding: '12px', backgroundColor: '#fff5f5', borderRadius: '8px', borderLeft: '4px solid #e74c3c' }}>
              <strong>Social Gap:</strong> There is a noticeable dip in social SDGs (3, 5), representing an opportunity for interdisciplinary growth.
            </div>
          </div>
        </div>
      </div>

      {/* Heatmap */}
      <SDGHeatmap />
    </div>
  );
}
