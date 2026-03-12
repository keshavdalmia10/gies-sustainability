import { useDeferredValue, useEffect, useState } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts';
import api from '../../services/api';
import './DeanInteractiveDashboard.css';

type SummaryMetrics = {
  publications: number;
  faculty: number;
  departments: number;
  sdgs: number;
};

type TrendPoint = {
  label: string;
  year: number;
  publications: number;
};

type DepartmentMetric = {
  name: string;
  publications: number;
  citations: number;
  impact: number;
  sdgCounts: Record<string, number>;
  papers: string[];
};

type FacultyMetric = {
  name: string;
  department: string;
  publications: number;
  citations: number;
  impact: number;
};

type HeatmapSelection = {
  department: string;
  sdg: string;
  count: number;
};

const CHART_COLORS = ['#1f6feb', '#2f855a', '#c2410c', '#9a3412', '#0f766e', '#7c3aed'];

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function toArray(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }

  if (!isRecord(value)) {
    return [];
  }

  if (Array.isArray(value.items)) {
    return value.items;
  }

  if (Array.isArray(value.results)) {
    return value.results;
  }

  if (Array.isArray(value.data)) {
    return value.data;
  }

  if (Array.isArray(value.departments)) {
    return value.departments;
  }

  if (Array.isArray(value.trends)) {
    return value.trends;
  }

  if (Array.isArray(value.faculty)) {
    return value.faculty;
  }

  return [];
}

function pickString(source: unknown, keys: string[], fallback = ''): string {
  if (!isRecord(source)) {
    return fallback;
  }

  for (const key of keys) {
    const value = source[key];
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
  }

  return fallback;
}

function pickNumber(source: unknown, keys: string[], fallback = 0): number {
  if (!isRecord(source)) {
    return fallback;
  }

  for (const key of keys) {
    const value = source[key];
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === 'string' && value.trim()) {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }

  return fallback;
}

function normalizeSdgLabel(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return 'Unmapped';
  }

  if (/^sdg\s+/i.test(trimmed)) {
    return trimmed.toUpperCase();
  }

  const numberMatch = trimmed.match(/^(\d{1,2})$/);
  if (numberMatch) {
    return `SDG ${numberMatch[1]}`;
  }

  return trimmed;
}

function pickCount(source: unknown, keys: string[]): number {
  if (!isRecord(source)) {
    return 0;
  }

  for (const key of keys) {
    const value = source[key];
    if (Array.isArray(value)) {
      return value.length;
    }
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === 'string' && value.trim()) {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }

  return 0;
}

function normalizeSummary(payload: unknown): SummaryMetrics {
  const source = isRecord(payload) ? payload : {};
  return {
    publications: pickNumber(source, ['publications', 'publication_count', 'total_publications', 'papers'], 0),
    faculty: pickNumber(source, ['faculty', 'faculty_count', 'researchers'], 0),
    departments: pickNumber(source, ['departments', 'department_count'], 0),
    sdgs: pickNumber(source, ['sdgs', 'sdg_count', 'goals'], 0),
  };
}

function normalizeTrends(payload: unknown): TrendPoint[] {
  const items = toArray(payload);
  return items
    .map((item) => {
      const year = pickNumber(item, ['year', 'publication_year'], 0);
      const label = pickString(item, ['label', 'period'], year ? String(year) : 'Unknown');
      return {
        label,
        year,
        publications: pickNumber(item, ['count', 'publications', 'publication_count', 'value'], 0),
      };
    })
    .filter((item) => item.publications > 0);
}

function extractSdgCounts(item: unknown): Record<string, number> {
  if (!isRecord(item)) {
    return {};
  }

  const candidate =
    item.sdg_counts ??
    item.sdgCounts ??
    item.sdg_breakdown ??
    item.sdgBreakdown ??
    item.sdgs ??
    null;

  if (Array.isArray(candidate)) {
    const entries = candidate
      .map((entry) => {
        const key = normalizeSdgLabel(pickString(entry, ['sdg', 'name', 'label', 'goal'], ''));
        const count = pickNumber(entry, ['count', 'publications', 'value'], 0);
        return key ? [key, count] : null;
      })
      .filter(Boolean) as Array<[string, number]>;

    return Object.fromEntries(entries);
  }

  if (isRecord(candidate)) {
    return Object.fromEntries(
      Object.entries(candidate).map(([key, value]) => [
        normalizeSdgLabel(key),
        typeof value === 'number' ? value : Number(value) || 0,
      ]),
    );
  }

  return {};
}

function extractPaperTitles(item: unknown): string[] {
  if (!isRecord(item)) {
    return [];
  }

  const collections = [item.papers, item.publications, item.items];
  for (const collection of collections) {
    if (!Array.isArray(collection)) {
      continue;
    }

    const titles = collection
      .map((entry) => {
        if (typeof entry === 'string') {
          return entry.trim();
        }
        return pickString(entry, ['title', 'name', 'paper_title'], '');
      })
      .filter(Boolean);

    if (titles.length > 0) {
      return titles;
    }
  }

  return [];
}

function normalizeDepartments(payload: unknown): DepartmentMetric[] {
  const items = toArray(payload);
  return items
    .map((item) => ({
      name: pickString(item, ['department', 'name', 'label'], 'Unknown Department'),
      publications: pickCount(item, ['publications', 'count', 'publication_count']),
      citations: pickNumber(item, ['citations', 'citation_count'], 0),
      impact: pickNumber(item, ['impact', 'impact_score'], 0),
      sdgCounts: extractSdgCounts(item),
      papers: extractPaperTitles(item),
    }))
    .filter((item) => item.publications > 0 || Object.keys(item.sdgCounts).length > 0);
}

function normalizeFaculty(payload: unknown): FacultyMetric[] {
  const items = toArray(payload);
  return items
    .map((item) => ({
      name: pickString(item, ['faculty', 'name', 'researcher'], 'Unknown Researcher'),
      department: pickString(item, ['department', 'unit'], 'Unknown Department'),
      publications: pickCount(item, ['publications', 'count', 'publication_count']),
      citations: pickNumber(item, ['citations', 'citation_count'], 0),
      impact: pickNumber(item, ['impact', 'impact_score'], 0),
    }))
    .filter((item) => item.publications > 0 || item.citations > 0 || item.impact > 0);
}

function normalizeSdgTotals(payload: unknown): Record<string, number> {
  const items = toArray(payload);
  const totals: Record<string, number> = {};

  for (const item of items) {
    const label = normalizeSdgLabel(pickString(item, ['sdg', 'name', 'label', 'goal'], ''));
    if (!label) {
      continue;
    }
    totals[label] = (totals[label] || 0) + pickNumber(item, ['count', 'publications', 'value'], 0);
  }

  return totals;
}

function blendHeatColor(value: number, max: number): string {
  const ratio = max === 0 ? 0 : value / max;
  const alpha = Math.min(0.88, 0.12 + ratio * 0.76);
  return `rgba(31, 111, 235, ${alpha})`;
}

export default function DeanInteractiveDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summary, setSummary] = useState<SummaryMetrics>({
    publications: 0,
    faculty: 0,
    departments: 0,
    sdgs: 0,
  });
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [departments, setDepartments] = useState<DepartmentMetric[]>([]);
  const [faculty, setFaculty] = useState<FacultyMetric[]>([]);
  const [sdgTotals, setSdgTotals] = useState<Record<string, number>>({});

  const [selectedDepartment, setSelectedDepartment] = useState('All departments');
  const [selectedSdg, setSelectedSdg] = useState('All SDGs');
  const [search, setSearch] = useState('');
  const deferredSearch = useDeferredValue(search);
  const [yearStart, setYearStart] = useState(0);
  const [yearEnd, setYearEnd] = useState(0);
  const [selectedHeatmapCell, setSelectedHeatmapCell] = useState<HeatmapSelection | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadAnalytics() {
      setLoading(true);
      setError('');

      try {
        const [summaryResponse, trendsResponse, departmentsResponse, facultyResponse, sdgResponse] =
          await Promise.all([
            api.get('/analytics/summary'),
            api.get('/analytics/trends/publications'),
            api.get('/analytics/departments'),
            api.get('/analytics/faculty/top'),
            api.get('/analytics/sdg/distribution'),
          ]);

        if (cancelled) {
          return;
        }

        const normalizedSummary = normalizeSummary(summaryResponse.data);
        const normalizedTrends = normalizeTrends(trendsResponse.data);
        const normalizedDepartments = normalizeDepartments(departmentsResponse.data);
        const normalizedFaculty = normalizeFaculty(facultyResponse.data);
        const normalizedSdgTotals = normalizeSdgTotals(sdgResponse.data);

        const years = normalizedTrends
          .map((item) => item.year)
          .filter((year) => Number.isFinite(year) && year > 0)
          .sort((left, right) => left - right);

        setSummary({
          ...normalizedSummary,
          departments: normalizedSummary.departments || normalizedDepartments.length,
          sdgs: normalizedSummary.sdgs || Object.keys(normalizedSdgTotals).length,
        });
        setTrends(normalizedTrends);
        setDepartments(normalizedDepartments);
        setFaculty(normalizedFaculty);
        setSdgTotals(normalizedSdgTotals);
        setYearStart(years[0] || 0);
        setYearEnd(years[years.length - 1] || 0);
      } catch (loadError) {
        if (!cancelled) {
          setError('Analytics data could not be loaded.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      cancelled = true;
    };
  }, []);

  const availableYears = trends
    .map((item) => item.year)
    .filter((year) => Number.isFinite(year) && year > 0)
    .sort((left, right) => left - right);

  const availableDepartments = [
    'All departments',
    ...Array.from(new Set(departments.map((item) => item.name))).sort((left, right) =>
      left.localeCompare(right),
    ),
  ];
  const availableSdgs = [
    'All SDGs',
    ...Array.from(
      new Set([
        ...Object.keys(sdgTotals),
        ...departments.flatMap((item) => Object.keys(item.sdgCounts)),
      ]),
    ).sort((left, right) => left.localeCompare(right)),
  ];

  const normalizedSearch = deferredSearch.trim().toLowerCase();
  const safeYearStart = yearStart && yearEnd ? Math.min(yearStart, yearEnd) : yearStart || yearEnd;
  const safeYearEnd = yearStart && yearEnd ? Math.max(yearStart, yearEnd) : yearEnd || yearStart;

  const filteredTrends = trends.filter((item) => {
    if (!safeYearStart || !safeYearEnd) {
      return true;
    }
    return item.year >= safeYearStart && item.year <= safeYearEnd;
  });

  const filteredDepartments = departments
    .filter((item) => selectedDepartment === 'All departments' || item.name === selectedDepartment)
    .filter((item) => {
      if (selectedSdg === 'All SDGs') {
        return true;
      }
      return (item.sdgCounts[selectedSdg] || 0) > 0;
    })
    .filter((item) => {
      if (!normalizedSearch) {
        return true;
      }
      return item.name.toLowerCase().includes(normalizedSearch);
    });

  const filteredFaculty = faculty
    .filter((item) => selectedDepartment === 'All departments' || item.department === selectedDepartment)
    .filter((item) => {
      if (!normalizedSearch) {
        return true;
      }
      const haystack = `${item.name} ${item.department}`.toLowerCase();
      return haystack.includes(normalizedSearch);
    });

  const departmentChartData = filteredDepartments
    .map((item) => ({
      name: item.name,
      publications:
        selectedSdg === 'All SDGs' ? item.publications : item.sdgCounts[selectedSdg] || 0,
      citations: item.citations,
      impact: item.impact,
    }))
    .sort((left, right) => right.publications - left.publications)
    .slice(0, 8);

  const aggregatedSdgTotals = availableSdgs
    .filter((sdg) => sdg !== 'All SDGs')
    .map((sdg) => ({
      name: sdg,
      value: filteredDepartments.reduce((sum, department) => sum + (department.sdgCounts[sdg] || 0), 0),
    }))
    .filter((entry) => entry.value > 0)
    .sort((left, right) => right.value - left.value);

  const facultyScatterData = filteredFaculty
    .map((item) => ({
      x: item.publications || 0,
      y: item.citations || item.impact || item.publications || 0,
      z: Math.max(60, item.impact || item.citations || item.publications || 1),
      name: item.name,
      department: item.department,
    }))
    .slice(0, 24);

  const heatmapSdgs = availableSdgs.filter((sdg) => sdg !== 'All SDGs');
  const heatmapMax = Math.max(
    0,
    ...filteredDepartments.flatMap((department) =>
      heatmapSdgs.map((sdg) => department.sdgCounts[sdg] || 0),
    ),
  );

  const strongestCell = filteredDepartments
    .flatMap((department) =>
      heatmapSdgs.map((sdg) => ({
        department: department.name,
        sdg,
        count: department.sdgCounts[sdg] || 0,
      })),
    )
    .sort((left, right) => right.count - left.count)[0];

  const leadDepartment = filteredDepartments
    .slice()
    .sort((left, right) => right.publications - left.publications)[0];

  const leadingResearcher = filteredFaculty
    .slice()
    .sort(
      (left, right) =>
        right.impact + right.citations + right.publications -
        (left.impact + left.citations + left.publications),
    )[0];

  const selectedDepartmentDetails = selectedHeatmapCell
    ? departments.find((item) => item.name === selectedHeatmapCell.department)
    : null;

  const detailPaperList = selectedDepartmentDetails?.papers || [];

  function resetFilters() {
    setSelectedDepartment('All departments');
    setSelectedSdg('All SDGs');
    setSearch('');
    setSelectedHeatmapCell(null);
    if (availableYears.length > 0) {
      setYearStart(availableYears[0]);
      setYearEnd(availableYears[availableYears.length - 1]);
    }
  }

  return (
    <div className="dean-dashboard-shell">
      <section className="dean-dashboard-hero">
        <div>
          <p className="dean-eyebrow">Interactive Dean Dashboard</p>
          <h1>Research momentum, sustainability strength, and faculty impact in one view.</h1>
          <p className="dean-hero-copy">
            This view replaces static summaries with clickable charts, shared filters, and an
            interactive SDG heatmap so the dashboard tells a clearer research story.
          </p>
        </div>
        <div className="dean-kpi-grid">
          <article className="dean-kpi-card">
            <span>Publications</span>
            <strong>{summary.publications.toLocaleString()}</strong>
          </article>
          <article className="dean-kpi-card">
            <span>Faculty</span>
            <strong>{summary.faculty.toLocaleString()}</strong>
          </article>
          <article className="dean-kpi-card">
            <span>Departments</span>
            <strong>{summary.departments.toLocaleString()}</strong>
          </article>
          <article className="dean-kpi-card">
            <span>SDGs Covered</span>
            <strong>{summary.sdgs.toLocaleString()}</strong>
          </article>
        </div>
      </section>

      <section className="dean-filter-bar">
        <label>
          <span>Department</span>
          <select
            value={selectedDepartment}
            onChange={(event) => setSelectedDepartment(event.target.value)}
          >
            {availableDepartments.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>SDG</span>
          <select value={selectedSdg} onChange={(event) => setSelectedSdg(event.target.value)}>
            {availableSdgs.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Start year</span>
          <select value={yearStart} onChange={(event) => setYearStart(Number(event.target.value))}>
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>End year</span>
          <select value={yearEnd} onChange={(event) => setYearEnd(Number(event.target.value))}>
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </label>
        <label className="dean-search-field">
          <span>Search</span>
          <input
            type="search"
            placeholder="Search researcher or department"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <button type="button" className="dean-reset-button" onClick={resetFilters}>
          Reset filters
        </button>
      </section>

      <section className="dean-story-strip">
        <article className="dean-story-card">
          <span>Strongest SDG signal</span>
          <strong>
            {strongestCell
              ? `${strongestCell.department} is leading in ${strongestCell.sdg}`
              : 'Waiting for SDG-linked department data'}
          </strong>
          <p>
            {strongestCell
              ? `${strongestCell.count} mapped publications anchor the strongest heatmap cell.`
              : 'As richer SDG mappings land, this card will automatically sharpen its insight.'}
          </p>
        </article>
        <article className="dean-story-card">
          <span>Momentum signal</span>
          <strong>
            {filteredTrends.length > 1
              ? `${filteredTrends[filteredTrends.length - 1].label} closes at ${filteredTrends[
                  filteredTrends.length - 1
                ].publications} publications`
              : 'Trend data is available, but not yet dense enough for a stronger callout'}
          </strong>
          <p>
            The momentum chart below responds to the year window so the dean can isolate growth
            periods instead of reading a single static line.
          </p>
        </article>
        <article className="dean-story-card">
          <span>Faculty story</span>
          <strong>
            {leadingResearcher
              ? `${leadingResearcher.name} is the most visible researcher in the current view`
              : 'Faculty leaderboard will appear once faculty analytics return data'}
          </strong>
          <p>
            Use search to highlight a person, then follow their department footprint and SDG
            alignment across the charts.
          </p>
        </article>
      </section>

      {error ? <div className="dean-state-panel dean-error-panel">{error}</div> : null}
      {loading ? <div className="dean-state-panel">Loading interactive analytics…</div> : null}

      {!loading && !error ? (
        <div className="dean-chart-grid">
          <article className="dean-chart-card dean-chart-card-wide">
            <div className="dean-card-header">
              <div>
                <p className="dean-card-kicker">Momentum</p>
                <h2>Research output over time</h2>
              </div>
            </div>
            <div className="dean-chart-frame">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={filteredTrends}>
                  <defs>
                    <linearGradient id="deanMomentum" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#1f6feb" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#1f6feb" stopOpacity={0.04} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#d8e2ec" strokeDasharray="3 3" />
                  <XAxis dataKey="label" stroke="#5b6472" />
                  <YAxis stroke="#5b6472" />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="publications"
                    stroke="#1f6feb"
                    fill="url(#deanMomentum)"
                    strokeWidth={3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dean-chart-card">
            <div className="dean-card-header">
              <div>
                <p className="dean-card-kicker">Distribution</p>
                <h2>SDG mix</h2>
              </div>
            </div>
            <div className="dean-chart-frame">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={aggregatedSdgTotals}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={65}
                    outerRadius={100}
                    paddingAngle={2}
                    onClick={(entry) => {
                      const nextSdg = (entry as { name?: string }).name;
                      if (nextSdg) {
                        setSelectedSdg(nextSdg);
                      }
                    }}
                  >
                    {aggregatedSdgTotals.map((entry, index) => (
                      <Cell key={entry.name} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dean-chart-card">
            <div className="dean-card-header">
              <div>
                <p className="dean-card-kicker">Comparison</p>
                <h2>Department output</h2>
              </div>
            </div>
            <div className="dean-chart-frame">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={departmentChartData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid stroke="#d8e2ec" strokeDasharray="3 3" />
                  <XAxis type="number" stroke="#5b6472" />
                  <YAxis type="category" dataKey="name" width={130} stroke="#5b6472" />
                  <Tooltip />
                  <Bar
                    dataKey="publications"
                    fill="#2f855a"
                    radius={[0, 8, 8, 0]}
                    onClick={(entry) => {
                      const nextDepartment = (entry as { name?: string }).name;
                      if (nextDepartment) {
                        setSelectedDepartment(nextDepartment);
                      }
                    }}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dean-chart-card">
            <div className="dean-card-header">
              <div>
                <p className="dean-card-kicker">Faculty map</p>
                <h2>Researcher influence</h2>
              </div>
            </div>
            <div className="dean-chart-frame">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                  <CartesianGrid stroke="#d8e2ec" strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Publications"
                    stroke="#5b6472"
                    tickLine={false}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Influence"
                    stroke="#5b6472"
                    tickLine={false}
                  />
                  <ZAxis type="number" dataKey="z" range={[80, 600]} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter data={facultyScatterData} fill="#c2410c" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="dean-chart-card dean-chart-card-tall">
            <div className="dean-card-header">
              <div>
                <p className="dean-card-kicker">Interactive heatmap</p>
                <h2>Department by SDG strength</h2>
              </div>
            </div>
            <div className="dean-heatmap-shell">
              <div
                className="dean-heatmap-grid"
                style={{
                  gridTemplateColumns: `minmax(180px, 1.4fr) repeat(${heatmapSdgs.length}, minmax(72px, 1fr))`,
                }}
              >
                <div className="dean-heatmap-corner">Department</div>
                {heatmapSdgs.map((sdg) => (
                  <div key={sdg} className="dean-heatmap-column-header">
                    {sdg}
                  </div>
                ))}
                {filteredDepartments.map((department) => (
                  <FragmentRow
                    key={department.name}
                    department={department}
                    heatmapSdgs={heatmapSdgs}
                    heatmapMax={heatmapMax}
                    isActiveDepartment={department.name === selectedDepartment}
                    onSelectDepartment={setSelectedDepartment}
                    onSelectCell={(selection) => {
                      setSelectedHeatmapCell(selection);
                      setSelectedDepartment(selection.department);
                      setSelectedSdg(selection.sdg);
                    }}
                  />
                ))}
              </div>
              <aside className="dean-detail-panel">
                <p className="dean-card-kicker">Selected cell</p>
                <h3>
                  {selectedHeatmapCell
                    ? `${selectedHeatmapCell.department} · ${selectedHeatmapCell.sdg}`
                    : 'Pick a heatmap cell'}
                </h3>
                <p>
                  {selectedHeatmapCell
                    ? `${selectedHeatmapCell.count} publications are mapped to this department and goal pairing.`
                    : 'Selecting a cell updates the rest of the dashboard and opens a focused story panel.'}
                </p>
                {detailPaperList.length > 0 ? (
                  <div className="dean-paper-list">
                    {detailPaperList.slice(0, 5).map((paper) => (
                      <div key={paper} className="dean-paper-chip">
                        {paper}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="dean-detail-fallback">
                    <strong>
                      {leadDepartment
                        ? `${leadDepartment.name} remains the highest-volume department in view.`
                        : 'No paper-level drilldown was returned by the analytics endpoint.'}
                    </strong>
                    <p>
                      The dashboard still uses real analytics totals for filtering, comparison, and
                      storytelling while waiting for per-paper drilldown data.
                    </p>
                  </div>
                )}
              </aside>
            </div>
          </article>
        </div>
      ) : null}
    </div>
  );
}

type FragmentRowProps = {
  department: DepartmentMetric;
  heatmapSdgs: string[];
  heatmapMax: number;
  isActiveDepartment: boolean;
  onSelectDepartment: (department: string) => void;
  onSelectCell: (selection: HeatmapSelection) => void;
};

function FragmentRow({
  department,
  heatmapSdgs,
  heatmapMax,
  isActiveDepartment,
  onSelectDepartment,
  onSelectCell,
}: FragmentRowProps) {
  return (
    <>
      <button
        type="button"
        className={`dean-heatmap-row-label ${isActiveDepartment ? 'is-active' : ''}`}
        onClick={() => onSelectDepartment(department.name)}
      >
        <span>{department.name}</span>
        <small>{department.publications} pubs</small>
      </button>
      {heatmapSdgs.map((sdg) => {
        const count = department.sdgCounts[sdg] || 0;
        const isEmpty = count === 0;
        return (
          <button
            key={`${department.name}-${sdg}`}
            type="button"
            className={`dean-heatmap-cell ${isEmpty ? 'is-empty' : ''}`}
            style={{ backgroundColor: blendHeatColor(count, heatmapMax) }}
            title={`${department.name} · ${sdg}: ${count} publications`}
            onClick={() => onSelectCell({ department: department.name, sdg, count })}
          >
            {count}
          </button>
        );
      })}
    </>
  );
}
