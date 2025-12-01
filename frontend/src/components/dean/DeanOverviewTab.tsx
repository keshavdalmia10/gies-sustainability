import React, { useEffect, useState } from 'react';
import { TrendingUp, AlertTriangle, Target, Users, FileText, DollarSign } from 'lucide-react';
import { DepartmentBarChart, DonutChart, DepartmentData } from '../AnalyticsCharts';

export default function DeanOverviewTab() {
  const [departmentData, setDepartmentData] = useState<DepartmentData[]>([]);
  const [summaryData, setSummaryData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const deptRes = await fetch('http://localhost:8000/api/v1/analytics/departments');
        const deptJson = await deptRes.json();
        setDepartmentData(deptJson);

        const summaryRes = await fetch('http://localhost:8000/api/v1/analytics/summary');
        const summaryJson = await summaryRes.json();
        setSummaryData(summaryJson);
      } catch (error) {
        console.error("Failed to fetch analytics data", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      {/* KPI Grid */}
      <div className="grid grid-4 mb-4">
        <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(46, 204, 113, 0.1)', color: 'var(--color-success)' }}>
              <DollarSign size={24} />
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', fontWeight: 600 }}>TOTAL FUNDING</div>
          </div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: '4px' }}>$24.8M</div>
          <div className="text-muted">+12% vs Last Year</div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(52, 152, 219, 0.1)', color: 'var(--color-primary)' }}>
              <Users size={24} />
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', fontWeight: 600 }}>ACTIVE FACULTY</div>
          </div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: '4px' }}>{summaryData?.faculty_engagement?.total || 114}</div>
          <div className="text-muted">{summaryData?.faculty_engagement?.percentage || 74}% of Total Faculty</div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(155, 89, 182, 0.1)', color: '#9b59b6' }}>
              <FileText size={24} />
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', fontWeight: 600 }}>SDG ARTICLES</div>
          </div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: '4px' }}>{summaryData?.sdg_relevance?.relevant || 711}</div>
          <div className="text-muted">{summaryData?.sdg_relevance?.percentage || 19}% of Total Research</div>
        </div>

        <div className="card" style={{ padding: 'var(--spacing-lg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <div style={{ padding: '8px', borderRadius: '8px', backgroundColor: 'rgba(241, 196, 15, 0.1)', color: '#f1c40f' }}>
              <Target size={24} />
            </div>
            <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', fontWeight: 600 }}>COMMUNITY CONFIDENCE</div>
          </div>
          <div style={{ fontSize: 'var(--font-size-2xl)', fontWeight: 700, marginBottom: '4px' }}>98%</div>
          <div className="text-muted">Based on 42 validations</div>
        </div>
      </div>

      {/* Top Departments Chart */}
      <div className="card mb-4">
        <h3 className="card-title">Top Departments by Publication</h3>
        <p className="card-subtitle mb-3">Publication metrics for key business departments</p>
        <DepartmentBarChart data={departmentData} />
      </div>

      {/* Strategic Bets Section */}
      <div className="grid grid-2 mb-4">
        <div className="card">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={20} color="var(--color-success)" /> Top Momentum
          </h3>
          <p className="card-subtitle mb-3">SDGs with highest growth in funding & citations</p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div>
              <div style={{ fontWeight: 600 }}>SDG 7: Clean Energy</div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-light)' }}>Led by Finance & Engineering</div>
            </div>
            <div className="badge badge-success">+45% YoY</div>
          </div>
           <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div>
              <div style={{ fontWeight: 600 }}>SDG 13: Climate Action</div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-light)' }}>Led by Economics</div>
            </div>
            <div className="badge badge-success">+28% YoY</div>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={20} color="var(--color-error)" /> Critical Gaps
          </h3>
          <p className="card-subtitle mb-3">High societal demand, low internal activity</p>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', padding: '12px', backgroundColor: '#fff5f5', borderRadius: '8px' }}>
            <div>
              <div style={{ fontWeight: 600 }}>SDG 3: Health & Well-being</div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-light)' }}>Potential: Medical School Partnership</div>
            </div>
            <div className="badge badge-error">Low Activity</div>
          </div>
           <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', backgroundColor: '#fff5f5', borderRadius: '8px' }}>
            <div>
              <div style={{ fontWeight: 600 }}>SDG 5: Gender Equality</div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-light)' }}>Potential: Leadership Grants</div>
            </div>
            <div className="badge badge-error">Nascent</div>
          </div>
        </div>
      </div>

      {/* Proportions Charts */}
      <div className="grid grid-2 mb-4">
        <div className="card">
          <h3 className="card-title">Proportion of SDG Relevant Articles</h3>
          <p className="card-subtitle mb-3">The proportion of articles that align with UN sustainability goals</p>
          {summaryData && (
            <DonutChart 
              value={summaryData.sdg_relevance.relevant} 
              total={summaryData.sdg_relevance.total} 
              label="SDG Relevant" 
              color="#0066cc" 
            />
          )}
        </div>
        <div className="card">
          <h3 className="card-title">Proportion of Faculty Engaged in SDG Research</h3>
          <p className="card-subtitle mb-3">Percentage of faculty contributing to sustainability publications</p>
          {summaryData && (
            <DonutChart 
              value={summaryData.faculty_engagement.engaged} 
              total={summaryData.faculty_engagement.total} 
              label="Engaged" 
              color="#8884d8" 
            />
          )}
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="card" style={{ backgroundColor: 'rgba(0, 102, 204, 0.05)', border: '1px solid rgba(0, 102, 204, 0.2)' }}>
        <h3 className="card-title" style={{ color: 'var(--color-primary)' }}>AI Strategic Recommendations</h3>
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          <li className="mb-2">
            <strong>Consolidate SDG 7 Efforts:</strong> Create a formal "Clean Energy Finance Center" to unify the 15+ active grants in Finance and Economics.
          </li>
          <li className="mb-2">
            <strong>Hiring Target:</strong> Recruit 2 tenure-track faculty in <strong>Health Economics (SDG 3)</strong> to bridge the gap between Business and Medicine.
          </li>
          <li>
            <strong>Donor Opportunity:</strong> The "Climate Action" portfolio has matured enough (28% growth) to pitch a $5M endowment for a new Chair.
          </li>
        </ul>
      </div>
    </div>
  );
}
