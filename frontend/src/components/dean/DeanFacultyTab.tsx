import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const ENGAGEMENT_DATA = [
  { name: 'Engaged in SDG Research', value: 114 },
  { name: 'Not Yet Engaged', value: 40 },
];

const COLORS = ['#0066cc', '#e0e0e0'];

const TOP_FACULTY = [
  { name: "Prof. Jane Doe", dept: "Finance", sdgs: [7, 13], pubs: 12, funding: "$2.1M" },
  { name: "Prof. Alan Smith", dept: "Economics", sdgs: [1, 8], pubs: 15, funding: "$1.8M" },
  { name: "Prof. Sarah Lee", dept: "Marketing", sdgs: [12], pubs: 8, funding: "$0.9M" },
  { name: "Prof. David Kim", dept: "Accountancy", sdgs: [16], pubs: 6, funding: "$0.5M" },
];

export default function DeanFacultyTab() {
  return (
    <div className="grid grid-2">
      
      {/* Engagement Chart */}
      <div className="card">
        <h3 className="card-title">Faculty Engagement</h3>
        <p className="card-subtitle mb-3">Proportion of faculty contributing to sustainability goals</p>
        <div style={{ height: '300px', position: 'relative' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={ENGAGEMENT_DATA}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
              >
                {ENGAGEMENT_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -65%)', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 700, color: '#0066cc' }}>74%</div>
            <div style={{ fontSize: '12px', color: '#666' }}>Engaged</div>
          </div>
        </div>
      </div>

      {/* Top Contributors */}
      <div className="card">
        <h3 className="card-title">Top Contributors</h3>
        <p className="card-subtitle mb-3">Faculty leading in impact metrics</p>
        
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
              <th style={{ textAlign: 'left', padding: '8px', fontSize: '12px' }}>Name</th>
              <th style={{ textAlign: 'left', padding: '8px', fontSize: '12px' }}>Dept</th>
              <th style={{ textAlign: 'right', padding: '8px', fontSize: '12px' }}>Pubs</th>
              <th style={{ textAlign: 'right', padding: '8px', fontSize: '12px' }}>Funding</th>
            </tr>
          </thead>
          <tbody>
            {TOP_FACULTY.map((f, i) => (
              <tr key={i} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 8px', fontWeight: 600 }}>{f.name}</td>
                <td style={{ padding: '12px 8px', color: 'var(--color-text-light)' }}>{f.dept}</td>
                <td style={{ padding: '12px 8px', textAlign: 'right' }}>{f.pubs}</td>
                <td style={{ padding: '12px 8px', textAlign: 'right', color: 'var(--color-success)' }}>{f.funding}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
