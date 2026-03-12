import { useEffect, useState } from 'react';
import { PublicationTrendChart, TrendData } from '../AnalyticsCharts';
import api from '../../services/api';

export default function DeanTrendsTab() {
  const [trendData, setTrendData] = useState<TrendData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/analytics/trends/publications');
        setTrendData(Array.isArray(res.data) ? res.data : []);
      } catch (error) {
        console.error("Failed to fetch trend data", error);
        setTrendData([]);
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
