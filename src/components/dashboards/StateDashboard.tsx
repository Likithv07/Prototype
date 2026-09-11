import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatCard } from '../common/StatCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Building2,
  FolderKanban,
  MapPin,
  CheckCircle2,
  Clock,
  CreditCard,
  Flag,
  ArrowRight,
  Filter,
  Search,
  ExternalLink,
} from 'lucide-react';
import { STATES_DATA } from '../../data/mockData';

export const StateDashboard: React.FC = () => {
  const {
    selectedStateId,
    setSelectedStateId,
    setCurrentView,
    setSelectedProjectId,
    setUserRole,
    showToast,
  } = useApp();

  const [searchDistrict, setSearchDistrict] = useState('');

  const currentState = STATES_DATA.find((s) => s.id === (selectedStateId || 'TS')) || STATES_DATA[0];

  const districtsData = [
    {
      district: 'Hyderabad / Medchal',
      projects: 5,
      landProposed: 1250,
      landAcquired: 820,
      compensationCr: 614.2,
      progress: 65,
      status: 'Active',
      pendingAwards: 12,
    },
    {
      district: 'Ranga Reddy',
      projects: 4,
      landProposed: 2800,
      landAcquired: 2350,
      compensationCr: 890.5,
      progress: 84,
      status: 'Possession',
      pendingAwards: 3,
    },
    {
      district: 'Nalgonda',
      projects: 3,
      landProposed: 3400,
      landAcquired: 2900,
      compensationCr: 740.0,
      progress: 85,
      status: 'Active',
      pendingAwards: 6,
    },
    {
      district: 'Suryapet',
      projects: 2,
      landProposed: 1850,
      landAcquired: 1400,
      compensationCr: 480.2,
      progress: 75,
      status: 'Active',
      pendingAwards: 4,
    },
    {
      district: 'Khammam',
      projects: 2,
      landProposed: 2200,
      landAcquired: 1100,
      compensationCr: 390.0,
      progress: 50,
      status: 'Under Survey',
      pendingAwards: 18,
    },
    {
      district: 'Warangal Urban',
      projects: 2,
      landProposed: 1600,
      landAcquired: 1580,
      compensationCr: 510.8,
      progress: 98,
      status: 'Completed',
      pendingAwards: 0,
    },
  ];

  const filteredDistricts = districtsData.filter((d) =>
    d.district.toLowerCase().includes(searchDistrict.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse" />
            <span className="text-xs uppercase font-mono text-purple-400 font-semibold tracking-wider">
              State Land Revenue & Acquisition Directorate
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            {currentState.name} State Overview
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            District-wise progress, land consolidation, and statutory revenue awards.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={currentState.id}
            onChange={(e) => {
              setSelectedStateId(e.target.value);
              showToast(`Loaded data for ${e.target.value} State`, 'info');
            }}
            className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:border-cyan-400 focus:outline-none"
          >
            {STATES_DATA.map((st) => (
              <option key={st.id} value={st.id}>
                {st.name} ({st.code})
              </option>
            ))}
          </select>

          <button
            onClick={() => {
              setUserRole('officer');
              setCurrentView('compensation');
              showToast('Switched to District LAO Portal for award approvals', 'info');
            }}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.4)]"
          >
            <span>Review Collector Awards</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards (6 requested by prompt) */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
        <StatCard
          title="Active Projects"
          value={currentState.projectsCount}
          subtitle="Corridors in state"
          icon={FolderKanban}
          color="blue"
        />
        <StatCard
          title="Land Proposed"
          value={`${(currentState?.landProposedAcres ?? 0).toLocaleString()} Ac`}
          subtitle="Gazetted in Sec 3A"
          icon={MapPin}
          color="cyan"
        />
        <StatCard
          title="Land Acquired"
          value={`${(currentState?.landAcquiredAcres ?? 0).toLocaleString()} Ac`}
          subtitle={`${currentState?.landProposedAcres ? ((currentState.landAcquiredAcres / currentState.landProposedAcres) * 100).toFixed(0) : 0}% Completed`}
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Pending Approvals"
          value="43 Awards"
          subtitle="District Collectors"
          icon={Clock}
          color="amber"
        />
        <StatCard
          title="Compensation Pending"
          value={`₹${(currentState.compensationPaidCr * 0.28).toFixed(1)} Cr`}
          subtitle="PFMS queued"
          icon={CreditCard}
          color="purple"
        />
        <StatCard
          title="Possession Done"
          value="18 Projects"
          subtitle="Handed to NHAI"
          icon={Flag}
          color="emerald"
        />
      </div>

      {/* District-wise Progress Table */}
      <GlassCard className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-cyan-400" />
              <span>District-Wise Acquisition Performance</span>
            </h2>
            <p className="text-xs text-slate-400">
              Live metrics across revenue districts for {currentState.name}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchDistrict}
                onChange={(e) => setSearchDistrict(e.target.value)}
                placeholder="Search district..."
                className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">District</th>
                <th className="py-3 px-4">Projects</th>
                <th className="py-3 px-4">Land Acquired / Proposed</th>
                <th className="py-3 px-4">Compensation Disbursed</th>
                <th className="py-3 px-4">Progress</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredDistricts.map((row) => (
                <tr
                  key={row.district}
                  className="hover:bg-cyan-500/5 transition-colors group cursor-pointer"
                  onClick={() => {
                    setSelectedProjectId('NLA-TS-2026-001');
                    setCurrentView('projects');
                  }}
                >
                  <td className="py-3 px-4 font-semibold text-white">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{row.district}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 font-tech text-sm text-slate-200">
                    {row.projects} Projects
                  </td>
                  <td className="py-3 px-4 font-tech text-sm text-slate-200">
                    <span className="text-emerald-400 font-bold">{row.landAcquired}</span> /{' '}
                    {row.landProposed} Acres
                  </td>
                  <td className="py-3 px-4 font-tech text-sm text-purple-400 font-bold">
                    ₹{row.compensationCr} Cr
                  </td>
                  <td className="py-3 px-4 w-40">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                          style={{ width: `${row.progress}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-mono font-bold text-white">
                        {row.progress}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={row.status} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProjectId('NLA-TS-2026-001');
                        setUserRole('officer');
                        setCurrentView('compensation');
                      }}
                      className="px-2.5 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-medium inline-flex items-center gap-1 transition-all"
                    >
                      <span>Manage Awards</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};
