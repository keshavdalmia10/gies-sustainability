import React from 'react';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const PUBLICATION_DATA = [
  { year: '2019', publications: 45, citations: 120 },
  { year: '2020', publications: 52, citations: 180 },
  { year: '2021', publications: 58, citations: 250 },
  { year: '2022', publications: 75, citations: 400 },
  { year: '2023', publications: 92, citations: 650 },
];

const FUNDING_DATA = [
  { year: '2019', amount: 1.2 },
  { year: '2020', amount: 1.5 },
  { year: '2021', amount: 2.1 },
  { year: '2022', amount: 3.5 },
  { year: '2023', amount: 4.8 },
];

export default function MomentumCharts() {
  return (
    <div className="grid grid-2">
      
      {/* Publication Growth */}
      <div className="card">
        <h3 className="card-title">Research Momentum</h3>
        <p className="card-subtitle mb-3">Publication and citation growth (5-year trend)</p>
        <div style={{ height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={PUBLICATION_DATA}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="publications" stroke="#0066cc" strokeWidth={2} name="Publications" />
              <Line yAxisId="right" type="monotone" dataKey="citations" stroke="#2ecc71" strokeWidth={2} name="Citations" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Funding Growth */}
      <div className="card">
        <h3 className="card-title">Grant Capture</h3>
        <p className="card-subtitle mb-3">Total external funding secured ($ Millions)</p>
        <div style={{ height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={FUNDING_DATA}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `$${value}M`} />
              <Tooltip formatter={(value) => [`$${value}M`, 'Funding']} />
              <Bar dataKey="amount" fill="#f39c12" radius={[4, 4, 0, 0]} name="Funding ($M)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
