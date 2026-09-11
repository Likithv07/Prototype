import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatCard } from '../common/StatCard';
import {
  FolderKanban,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  CreditCard,
  Users,
  Compass,
  ArrowUpRight,
  TrendingUp,
  Landmark,
  Building,
  Activity,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { STATES_DATA } from '../../data/mockData';

export const CentralDashboard: React.FC = () => {
  const {
    projects,
    landParcels,
    setCurrentView,
    setSelectedProjectId,
    setSelectedStateId,
    setUserRole,
    showToast,
  } = useApp();

  const [activeState, setActiveState] = useState<string>('TS');
  const [chartMetric, setChartMetric] = useState<'land' | 'compensation'>('land');

  // Computed metrics
  const totalProjects = projects.length + 172; // Representative national scale
  const totalLandProposed = projects.reduce((acc, p) => acc + p.landRequired, 0) + 184500;
  const totalLandAcquired = projects.reduce((acc, p) => acc + p.landAcquired, 0) + 142100;
  const totalCompensationCr = projects.reduce((acc, p) => acc + p.compensationDisbursedCr, 0) + 42150;
  const affectedFamilies = 124500;
  const displacedFamilies = 34200;
  const delayedProjects = projects.filter((p) => p.status === 'Delayed').length + 14;
  const completedProjects = projects.filter((p) => p.status === 'Completed').length + 86;

  const currentStateData = STATES_DATA.find((s) => s.id === activeState) || STATES_DATA[0];

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
              PRAGATI Apex Monitoring Console
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            National Land Acquisition Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time multi-state monitoring across strategic national infrastructure corridors.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentView('gis_map')}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.4)] hover:brightness-110 active:scale-95 transition-all"
          >
            <Compass className="w-4 h-4" />
            <span>Launch National GIS Portal</span>
          </button>
        </div>
      </div>

      {/* Animated KPI Cards Grid (8 stats requested) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Projects"
          value={totalProjects.toLocaleString()}
          subtitle="Across 28 States & UTs"
          icon={FolderKanban}
          color="blue"
          trend={{ value: '12%', isPositive: true }}
        />
        <StatCard
          title="Total Land Proposed"
          value={`${(totalLandProposed / 1000).toFixed(1)}k Ac`}
          subtitle="Approved in DPRs"
          icon={MapPin}
          color="cyan"
          trend={{ value: '8.4%', isPositive: true }}
        />
        <StatCard
          title="Total Land Acquired"
          value={`${(totalLandAcquired / 1000).toFixed(1)}k Ac`}
          subtitle={`${((totalLandAcquired / totalLandProposed) * 100).toFixed(1)}% Acquisition Rate`}
          icon={CheckCircle2}
          color="emerald"
          trend={{ value: '15.2%', isPositive: true }}
        />
        <StatCard
          title="Compensation Disbursed"
          value={`₹${(totalCompensationCr / 1000).toFixed(1)}k Cr`}
          subtitle="Direct Benefit Transfers"
          icon={CreditCard}
          color="purple"
          trend={{ value: '19.8%', isPositive: true }}
        />
        <StatCard
          title="Affected Families"
          value={affectedFamilies.toLocaleString()}
          subtitle="RFCTLARR beneficiaries"
          icon={Users}
          color="cyan"
        />
        <StatCard
          title="Displaced Families"
          value={displacedFamilies.toLocaleString()}
          subtitle="89% Resettled with Housing"
          icon={Building}
          color="amber"
        />
        <StatCard
          title="Delayed Projects"
          value={delayedProjects}
          subtitle="Requires Collector Intervention"
          icon={AlertTriangle}
          color="rose"
        />
        <StatCard
          title="Completed Projects"
          value={completedProjects}
          subtitle="Possession fully handed over"
          icon={CheckCircle2}
          color="emerald"
        />
      </div>

      {/* Main Command Section: Interactive India Map & State Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Clickable Interactive India Map */}
        <GlassCard glow className="lg:col-span-7 p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>Interactive National Geographic Matrix</span>
              </h2>
              <p className="text-xs text-slate-400">Click any state polygon to inspect real-time acquisition statistics</p>
            </div>
            <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2 py-1 rounded border border-cyan-500/40">
              STATE: {currentStateData.name} ({currentStateData.code})
            </span>
          </div>

          {/* Map Canvas */}
          <div className="relative w-full h-[380px] bg-[#0B1E36]/80 rounded-xl border border-cyan-500/20 overflow-hidden flex items-center justify-center p-2">
            <div className="absolute inset-0 gis-grid-pattern opacity-40 pointer-events-none" />

            <svg
              viewBox="220 180 420 540"
              className="w-full h-full select-none cursor-pointer"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* State Polygons */}
              {STATES_DATA.map((state) => {
                const isSelected = activeState === state.id;
                return (
                  <g key={state.id} onClick={() => setActiveState(state.id)}>
                    <path
                      d={state.svgPathCoord}
                      fill={
                        isSelected
                          ? 'rgba(34, 211, 238, 0.45)'
                          : 'rgba(37, 99, 235, 0.2)'
                      }
                      stroke={isSelected ? '#22D3EE' : 'rgba(56, 189, 248, 0.4)'}
                      strokeWidth={isSelected ? '2.5' : '1.2'}
                      className="transition-all duration-300 hover:fill-cyan-500/30 hover:stroke-cyan-300"
                    />
                    {/* Centroid Marker */}
                    <circle
                      cx={state.centroid[0]}
                      cy={state.centroid[1]}
                      r={isSelected ? '6' : '4'}
                      fill={isSelected ? '#22D3EE' : '#3B82F6'}
                      stroke="#071A2D"
                      strokeWidth="1.5"
                    />
                    <text
                      x={state.centroid[0]}
                      y={state.centroid[1] - 8}
                      textAnchor="middle"
                      fill={isSelected ? '#22D3EE' : '#94A3B8'}
                      fontSize={isSelected ? '12' : '10'}
                      fontWeight={isSelected ? 'bold' : '500'}
                      fontFamily="Rajdhani, sans-serif"
                    >
                      {state.code}
                    </text>
                  </g>
                );
              })}

              {/* Major National Corridor Network Overlay */}
              <path
                d="M 360,275 Q 400,350 485,480 T 465,660"
                fill="none"
                stroke="rgba(34, 211, 238, 0.7)"
                strokeWidth="2.5"
                strokeDasharray="6 3"
              />
              <path
                d="M 300,375 L 400,460 L 485,480 L 530,520"
                fill="none"
                stroke="rgba(139, 92, 246, 0.7)"
                strokeWidth="2.5"
                strokeDasharray="6 3"
              />
            </svg>

            {/* Quick State Selector Buttons Floating Bar */}
            <div className="absolute bottom-2 left-2 right-2 flex items-center gap-1.5 overflow-x-auto py-1 px-1 bg-slate-950/80 rounded-lg border border-slate-800 backdrop-blur-md">
              {STATES_DATA.map((st) => (
                <button
                  key={st.id}
                  onClick={() => setActiveState(st.id)}
                  className={`px-2 py-1 rounded text-[11px] font-mono whitespace-nowrap transition-all ${
                    activeState === st.id
                      ? 'bg-cyan-500 text-slate-950 font-bold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {st.name}
                </button>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* Right: Detailed State Card (Displaying all requested fields) */}
        <GlassCard glow className="lg:col-span-5 p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-cyan-400 font-bold">
                  State Performance Profile
                </span>
                <h3 className="text-xl font-bold text-white">{currentStateData.name}</h3>
              </div>
              <button
                onClick={() => {
                  setSelectedStateId(currentStateData.id);
                  setUserRole('state');
                  setCurrentView('dashboard');
                  showToast(`Switched view to ${currentStateData.name} State Portal`, 'info');
                }}
                className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1"
              >
                <span>Drill to State</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-300">Number of Active Projects</span>
                <span className="text-lg font-bold font-tech text-white">
                  {currentStateData.projectsCount} Corridors
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-300">Land Proposed (DPR)</span>
                <span className="text-lg font-bold font-tech text-cyan-400">
                  {(currentStateData?.landProposedAcres ?? 0).toLocaleString()} Acres
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-300">Land Acquired (Possession)</span>
                <span className="text-lg font-bold font-tech text-emerald-400">
                  {(currentStateData?.landAcquiredAcres ?? 0).toLocaleString()} Acres
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-300">Compensation Paid</span>
                <span className="text-lg font-bold font-tech text-purple-400">
                  ₹{(currentStateData?.compensationPaidCr ?? 0).toLocaleString()} Crore
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-300">Affected Families Documented</span>
                <span className="text-lg font-bold font-tech text-amber-400">
                  {(currentStateData?.affectedFamilies ?? 0).toLocaleString()} Families
                </span>
              </div>
            </div>

            {/* Progress Gauge */}
            <div className="mt-5 pt-4 border-t border-slate-800">
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-400">Acquisition Efficiency Ratio</span>
                <span className="text-cyan-300 font-bold font-mono">
                  {((currentStateData.landAcquiredAcres / currentStateData.landProposedAcres) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-emerald-400 rounded-full transition-all duration-700"
                  style={{
                    width: `${((currentStateData.landAcquiredAcres / currentStateData.landProposedAcres) * 100).toFixed(1)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Charts Section: 4 Distinct Command Center Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: State-wise Land Acquisition Progress */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">State-wise Land Acquisition Progress</h3>
              <p className="text-xs text-slate-400">Proposed vs Acquired Land in major infrastructure hubs</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-2.5 h-2.5 rounded bg-blue-500" /> Proposed
              </span>
              <span className="flex items-center gap-1.5 text-cyan-300">
                <span className="w-2.5 h-2.5 rounded bg-cyan-400" /> Acquired
              </span>
            </div>
          </div>

          <div className="h-64 flex items-end gap-3 pt-6 pb-2 border-b border-slate-800">
            {STATES_DATA.slice(0, 6).map((st) => {
              const proposedHeight = Math.min(100, (st.landProposedAcres / 50000) * 100);
              const acquiredHeight = Math.min(100, (st.landAcquiredAcres / 50000) * 100);
              return (
                <div key={st.code} className="flex-1 flex flex-col items-center h-full justify-end group">
                  <div className="w-full flex items-end justify-center gap-1 h-full">
                    {/* Proposed bar */}
                    <div
                      style={{ height: `${proposedHeight}%` }}
                      className="w-3.5 sm:w-5 bg-blue-600/40 rounded-t-sm border-t border-blue-400/60 group-hover:bg-blue-600/60 transition-all"
                      title={`${st.name} Proposed: ${st.landProposedAcres} Ac`}
                    />
                    {/* Acquired bar */}
                    <div
                      style={{ height: `${acquiredHeight}%` }}
                      className="w-3.5 sm:w-5 bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t-sm shadow-[0_0_12px_rgba(34,211,238,0.4)] group-hover:brightness-125 transition-all"
                      title={`${st.name} Acquired: ${st.landAcquiredAcres} Ac`}
                    />
                  </div>
                  <span className="text-[11px] font-mono text-slate-400 mt-2">{st.code}</span>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between items-center text-xs text-slate-400 pt-3">
            <span>High performer: Maharashtra (39,800 Ac)</span>
            <span className="text-cyan-400 font-mono">Real-time sync</span>
          </div>
        </GlassCard>

        {/* Chart 2: Compensation Trends (Quarterly Disbursement) */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Compensation Trends (PFMS Tranches)</h3>
              <p className="text-xs text-slate-400">Quarterly statutory awards credited via Direct Benefit Transfer</p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/70 border border-emerald-500/40 px-2 py-0.5 rounded">
              Total: ₹42.1k Cr
            </span>
          </div>

          <div className="h-64 relative flex items-center justify-center">
            {/* SVG Area Line Chart */}
            <svg viewBox="0 0 500 200" className="w-full h-full">
              <defs>
                <linearGradient id="compGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#8B5CF6" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Horizontal Grid lines */}
              <line x1="40" y1="40" x2="480" y2="40" stroke="rgba(255,255,255,0.06)" />
              <line x1="40" y1="90" x2="480" y2="90" stroke="rgba(255,255,255,0.06)" />
              <line x1="40" y1="140" x2="480" y2="140" stroke="rgba(255,255,255,0.06)" />

              {/* Fill Area */}
              <path
                d="M 50,150 L 120,130 L 190,110 L 260,85 L 330,70 L 400,45 L 470,30 L 470,170 L 50,170 Z"
                fill="url(#compGrad)"
              />

              {/* Stroke Line */}
              <path
                d="M 50,150 L 120,130 L 190,110 L 260,85 L 330,70 L 400,45 L 470,30"
                fill="none"
                stroke="#A855F7"
                strokeWidth="3"
                strokeLinecap="round"
              />

              {/* Data points */}
              {[
                { x: 50, y: 150, val: '₹3.2k Cr', q: 'Q1-24' },
                { x: 120, y: 130, val: '₹4.8k Cr', q: 'Q2-24' },
                { x: 190, y: 110, val: '₹6.1k Cr', q: 'Q3-24' },
                { x: 260, y: 85, val: '₹7.9k Cr', q: 'Q4-24' },
                { x: 330, y: 70, val: '₹8.6k Cr', q: 'Q1-25' },
                { x: 400, y: 45, val: '₹10.5k Cr', q: 'Q2-25' },
                { x: 470, y: 30, val: '₹12.4k Cr', q: 'Q3-25' },
              ].map((pt, i) => (
                <g key={i}>
                  <circle cx={pt.x} cy={pt.y} r="4.5" fill="#C084FC" stroke="#071A2D" strokeWidth="2" />
                  <text x={pt.x} y="190" textAnchor="middle" fill="#64748B" fontSize="11" fontFamily="sans-serif">
                    {pt.q}
                  </text>
                </g>
              ))}
            </svg>
          </div>
        </GlassCard>

        {/* Chart 3: Project Status Distribution */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Project Status Distribution</h3>
              <p className="text-xs text-slate-400">178 National infrastructure projects categorized by active phase</p>
            </div>
            <span className="text-xs font-mono text-cyan-300">Live Breakdown</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
            {/* SVG Donut */}
            <div className="relative flex items-center justify-center h-48">
              <svg viewBox="0 0 100 100" className="w-40 h-40 transform -rotate-90">
                <circle cx="50" cy="50" r="38" fill="none" stroke="#1E293B" strokeWidth="12" />
                {/* Completed - 40% */}
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="none"
                  stroke="#10B981"
                  strokeWidth="12"
                  strokeDasharray="95.5 238.7"
                  strokeDashoffset="0"
                />
                {/* Possession - 25% */}
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="none"
                  stroke="#22D3EE"
                  strokeWidth="12"
                  strokeDasharray="59.7 238.7"
                  strokeDashoffset="-95.5"
                />
                {/* Compensation - 20% */}
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="none"
                  stroke="#8B5CF6"
                  strokeWidth="12"
                  strokeDasharray="47.7 238.7"
                  strokeDashoffset="-155.2"
                />
                {/* Delayed - 15% */}
                <circle
                  cx="50"
                  cy="50"
                  r="38"
                  fill="none"
                  stroke="#EF4444"
                  strokeWidth="12"
                  strokeDasharray="35.8 238.7"
                  strokeDashoffset="-202.9"
                />
              </svg>
              <div className="absolute text-center">
                <span className="font-tech text-2xl font-bold text-white">178</span>
                <span className="block text-[10px] text-slate-400">Total Projects</span>
              </div>
            </div>

            {/* Donut Legend */}
            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  <span className="text-slate-300">Completed (Handover Done)</span>
                </div>
                <span className="font-mono font-bold text-white">86 (48%)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
                  <span className="text-slate-300">Possession Underway</span>
                </div>
                <span className="font-mono font-bold text-white">44 (25%)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-400" />
                  <span className="text-slate-300">Compensation Stage</span>
                </div>
                <span className="font-mono font-bold text-white">34 (19%)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
                  <span className="text-slate-300">Delayed / Litigation</span>
                </div>
                <span className="font-mono font-bold text-rose-400">14 (8%)</span>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Chart 4: Timeline Performance & SLA Compliance */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white">Timeline Performance & Milestone SLAs</h3>
              <p className="text-xs text-slate-400">Average statutory cycle turnaround vs RFCTLARR 2013 benchmarks</p>
            </div>
            <button
              onClick={() => setCurrentView('timeline_monitoring')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              <span>Inspect SLAs</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3.5 pt-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Proposal to Section 3A Notification</span>
                <span className="font-mono text-emerald-400">42 Days (Target 60 Days) • FAST</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-400 rounded-full" style={{ width: '70%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Drone LiDAR & Cadastral Verification</span>
                <span className="font-mono text-cyan-400">38 Days (Target 45 Days) • ON TRACK</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-400 rounded-full" style={{ width: '84%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">Compensation Assessment & Public Hearing</span>
                <span className="font-mono text-purple-400">68 Days (Target 70 Days) • ON TRACK</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-purple-400 rounded-full" style={{ width: '97%' }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-300">PFMS Direct Benefit Transfer Disbursement</span>
                <span className="font-mono text-emerald-400">4.2 Days • INSTANT ELECTRONIC</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-400 rounded-full" style={{ width: '92%' }} />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
