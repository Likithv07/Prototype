import React, { useState, useMemo } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  FolderKanban,
  Search,
  Filter,
  Plus,
  ArrowRight,
  MapPin,
  Building,
  TrendingUp,
  Download,
} from 'lucide-react';
import { ProjectType, ProjectStatus } from '../../types';

export const ProjectsList: React.FC = () => {
  const { projects, setSelectedProjectId, setCurrentView, showToast } = useApp();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [stateFilter, setStateFilter] = useState<string>('ALL');
  const [districtFilter, setDistrictFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');

  const projectTypes: ProjectType[] = [
    'Highway',
    'Railway',
    'Metro',
    'Airport',
    'Industrial Corridor',
    'Power Plant',
    'Smart City',
    'Defence',
  ];

  const filteredProjects = useMemo(() => {
    return projects.filter((p) => {
      const matchSearch =
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.ministry.toLowerCase().includes(searchTerm.toLowerCase());

      const matchStatus = statusFilter === 'ALL' || p.status === statusFilter;
      const matchState = stateFilter === 'ALL' || p.state === stateFilter;
      const matchDistrict = districtFilter === 'ALL' || p.district === districtFilter;
      const matchType = typeFilter === 'ALL' || p.projectType === typeFilter;

      return matchSearch && matchStatus && matchState && matchDistrict && matchType;
    });
  }, [projects, searchTerm, statusFilter, stateFilter, districtFilter, typeFilter]);

  const uniqueStates = Array.from(new Set(projects.map((p) => p.state)));
  const uniqueDistricts = Array.from(new Set(projects.map((p) => p.district)));

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
              National Infrastructure Pipeline
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Projects Management
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Multi-sector acquisition tracking across Road, Rail, Aviation, Industrial & Defence sectors.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => showToast('Exported National Project Master Register (CSV)', 'success')}
            className="px-3.5 py-2 rounded-xl glass-panel text-slate-300 hover:text-white border border-slate-700 text-xs font-semibold flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Register</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <GlassCard className="p-4 sm:p-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search Project ID, Name..."
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
            />
          </div>

          {/* Project Type Filter */}
          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Project Types</option>
              {projectTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Compensation Stage">Compensation Stage</option>
              <option value="Possession">Possession</option>
              <option value="Completed">Completed</option>
              <option value="Delayed">Delayed</option>
            </select>
          </div>

          {/* State Filter */}
          <div>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All States</option>
              {uniqueStates.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* District Filter */}
          <div>
            <select
              value={districtFilter}
              onChange={(e) => setDistrictFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
            >
              <option value="ALL">All Districts</option>
              {uniqueDistricts.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>
      </GlassCard>

      {/* Projects Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-mono text-slate-400">
            Showing <span className="text-cyan-400 font-bold">{filteredProjects.length}</span> verified infrastructure corridors
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Project ID</th>
                <th className="py-3 px-4">Project Name & Ministry</th>
                <th className="py-3 px-4">Location</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Land Req. / Acquired</th>
                <th className="py-3 px-4">Progress</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredProjects.map((proj) => (
                <tr
                  key={proj.id}
                  onClick={() => {
                    setSelectedProjectId(proj.id);
                    setCurrentView('project_details');
                  }}
                  className="hover:bg-cyan-500/5 transition-colors cursor-pointer group"
                >
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400 whitespace-nowrap">
                    {proj.id}
                  </td>
                  <td className="py-3 px-4">
                    <p className="font-semibold text-white group-hover:text-cyan-300 transition-colors">
                      {proj.name}
                    </p>
                    <p className="text-[11px] text-slate-400">{proj.ministry}</p>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <p className="text-slate-200">{proj.state}</p>
                    <p className="text-[11px] text-slate-400">{proj.district}</p>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-[11px] text-slate-300">
                      {proj.projectType}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-tech text-sm whitespace-nowrap">
                    <span className="text-emerald-400 font-bold">{proj.landAcquired}</span> /{' '}
                    {proj.landRequired} Ac
                  </td>
                  <td className="py-3 px-4 w-32">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                          style={{ width: `${proj.progress}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-mono font-bold text-white">
                        {proj.progress}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <StatusBadge status={proj.status} />
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedProjectId(proj.id);
                        setCurrentView('project_details');
                      }}
                      className="px-3 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold inline-flex items-center gap-1 transition-all"
                    >
                      <span>View Details</span>
                      <ArrowRight className="w-3.5 h-3.5" />
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
