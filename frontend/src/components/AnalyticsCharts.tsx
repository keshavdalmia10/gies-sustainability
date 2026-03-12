import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';

// --- Types ---
export interface DepartmentData {
  department: string;
  total_articles: number;
  sustain_articles: number;
  top_journal_articles: number;
}

export interface TrendData {
  year: number;
  total_articles: number;
  sustain_articles: number;
  top_journal_articles: number;
}

export interface FacultyData {
  name: string;
  department: string;
  total_articles: number;
  sustain_articles: number;
  top_journal_articles: number;
}

export interface SDGData {
  sdg: number;
  count: number;
  label: string;
}

// --- Colors ---
const COLORS = {
  primary: '#0066cc',
  secondary: '#2ecc71',
  accent: '#f39c12',
  textLight: '#666',
  grid: '#e0e0e0'
};

const SDG_COLORS = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C5192D', '#FF3A21', '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367', '#FD9D24', '#BF8B2E', '#3F7E44', '#0A97D9', '#56C02B', '#00689D', '#19486A'
];

// --- Components ---

export const DepartmentBarChart: React.FC<{ data: DepartmentData[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 20, right: 30, left: 100, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
        <XAxis type="number" />
        <YAxis dataKey="department" type="category" width={150} />
        <Tooltip />
        <Legend />
        <Bar dataKey="total_articles" name="Total Articles" fill={COLORS.primary} radius={[0, 4, 4, 0]} />
        <Bar dataKey="sustain_articles" name="SDG Articles" fill={COLORS.secondary} radius={[0, 4, 4, 0]} />
        <Bar dataKey="top_journal_articles" name="Top Journal Articles" fill={COLORS.accent} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const PublicationTrendChart: React.FC<{ data: TrendData[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="year" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="total_articles" name="Total Articles" stroke={COLORS.primary} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="sustain_articles" name="SDG Relevant Articles" stroke={COLORS.secondary} strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="top_journal_articles" name="Top Journal Articles" stroke={COLORS.accent} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export const FacultyBarChart: React.FC<{ data: FacultyData[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={500}>
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 20, right: 30, left: 120, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
        <XAxis type="number" />
        <YAxis dataKey="name" type="category" width={150} tick={{fontSize: 12}} />
        <Tooltip />
        <Legend />
        <Bar dataKey="total_articles" name="Total Articles" fill={COLORS.primary} radius={[0, 4, 4, 0]} barSize={20} />
        <Bar dataKey="sustain_articles" name="Sustainable Articles" fill={COLORS.secondary} radius={[0, 4, 4, 0]} barSize={20} />
        <Bar dataKey="top_journal_articles" name="Top Journal Articles" fill={COLORS.accent} radius={[0, 4, 4, 0]} barSize={20} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export const SDGDistributionChart: React.FC<{ data: SDGData[] }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart
        data={data}
        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" angle={-45} textAnchor="end" height={60} interval={0} tick={{fontSize: 10}} />
        <YAxis />
        <Tooltip />
        <Bar dataKey="count" name="Articles">
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={SDG_COLORS[index % SDG_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

export const DonutChart: React.FC<{ value: number, total: number, label: string, color: string }> = ({ value, total, label, color }) => {
  const data = [
    { name: 'Value', value: value },
    { name: 'Remaining', value: total - value },
  ];
  const percentage = total > 0 ? Math.round((value / total) * 100) : 0;

  return (
    <div style={{ height: '250px', position: 'relative' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            startAngle={90}
            endAngle={-270}
            dataKey="value"
          >
            <Cell key="value" fill={color} />
            <Cell key="remaining" fill="#e0e0e0" />
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
        <div style={{ fontSize: '24px', fontWeight: 700, color: color }}>{percentage}%</div>
        <div style={{ fontSize: '12px', color: '#666' }}>{label}</div>
      </div>
    </div>
  );
};
