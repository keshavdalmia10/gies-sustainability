import React from 'react';
import MomentumCharts from '../MomentumCharts';

export default function DeanTrendsTab() {
  return (
    <div>
      <div className="mb-4">
        <p className="text-muted mb-4">
          Longitudinal analysis of research output, citation impact, and grant funding capture over the last 5 years.
        </p>
        <MomentumCharts />
      </div>
    </div>
  );
}
