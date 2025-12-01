import React, { useEffect, useState } from 'react';
import { PublicationTrendChart, TrendData } from '../AnalyticsCharts';

export default function DeanTrendsTab() {
  const [trendData, setTrendData] = useState<TrendData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/analytics/trends/publications');
        const json = await res.json();
        setTrendData(json);
      } catch (error) {
        console.error("Failed to fetch trend data", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <div className="mb-4">
        <h3 className="card-title mb-2">Annual Publication Trend</h3>
        <p className="text-muted mb-4">
          Total articles, top journal articles, and SDG relevant articles by year
        </p>
        <div className="card">
           <PublicationTrendChart data={trendData} />
        </div>
      </div>
    </div>
  );
}
