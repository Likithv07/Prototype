import React from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  ArrowLeft,
  Building,
  Calendar,
  MapPin,
  Compass,
  Calculator,
  Camera,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileCheck,
  Flag,
  Share2,
  UserCheck,
} from 'lucide-react';

export const ProjectDetails: React.FC = () => {
  const {
    selectedProjectId,
    projects,
    setCurrentView,
    setUserRole,
    setSelectedParcelId,
    showToast,
  } = useApp();

  const project =
    projects.find((p) => p.id === selectedProjectId) || projects[0];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      case 'In Progress':
        return <Clock className="w-5 h-5 text-cyan-400 animate-spin" />;
      case 'Delayed':
        return <AlertTriangle className="w-5 h-5 text-rose-400" />;
      default:
        return <div className="w-3 h-3 rounded-full bg-slate-600" />;
    }
  };

  const getStatusBorder = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'border-emerald-500/40 bg-emerald-950/20 text-emerald-300';
      case 'In Progress':
        return 'border-cyan-500/40 bg-cyan-950/30 text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.2)]';
      case 'Delayed':
        return 'border-rose-500/40 bg-rose-950/20 text-rose-300';
      default:
        return 'border-slate-800 bg-slate-900/40 text-slate-400';
    }
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Back button & Actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentView('projects')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-300 hover:text-cyan-400 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Projects Master</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setCurrentView('gis_map');
              showToast(`Navigated to GIS view for ${project.id}`, 'info');
            }}
            className="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5"
          >
            <Compass className="w-4 h-4" />
            <span>Open in GIS Map</span>
          </button>
          <button
            onClick={() => {
              setUserRole('officer');
              setCurrentView('compensation');
              showToast('Opened Compensation & Award Hearing Console', 'info');
            }}
            className="px-3.5 py-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 text-xs font-semibold flex items-center gap-1.5"
          >
            <Calculator className="w-4 h-4" />
            <span>Review Awards</span>
          </button>
        </div>
      </div>

      {/* Project Overview Card */}
      <GlassCard glow className="p-6 sm:p-8 border-cyan-500/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-500/30">
                {project.id}
              </span>
              <StatusBadge status={project.status} />
              <span className="px-2.5 py-1 rounded bg-slate-800 text-xs font-medium text-slate-300 border border-slate-700">
                {project.projectType}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {project.name}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">{project.ministry}</p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
            <div className="text-left sm:text-right">
              <span className="text-xs text-slate-400 block">Overall Milestone Progress</span>
              <span className="font-tech text-2xl font-bold text-cyan-300">{project.progress}%</span>
              <div className="w-36 h-2 bg-slate-900 rounded-full mt-1 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                  style={{ width: `${project.progress}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Metadata Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 block mb-1">Implementing Agency</span>
            <span className="text-white font-semibold flex items-center gap-1.5">
              <Building className="w-3.5 h-3.5 text-cyan-400" />
              {project.implementingAgency}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 block mb-1">State & District</span>
            <span className="text-white font-semibold flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-emerald-400" />
              {project.state}, {project.district}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 block mb-1">Project Start Date</span>
            <span className="text-white font-semibold flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-blue-400" />
              {project.startDate}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-400 block mb-1">Expected Completion</span>
            <span className="text-white font-semibold flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-purple-400" />
              {project.expectedCompletionDate}
            </span>
          </div>
        </div>

        {/* Land & Financial Counters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs mt-4">
          <div className="p-3 rounded-xl bg-[#0B1E36] border border-cyan-500/20">
            <span className="text-slate-400 block">Land Required</span>
            <span className="text-lg font-bold font-tech text-white">{(project?.landRequired ?? 0).toLocaleString()} Acres</span>
          </div>
          <div className="p-3 rounded-xl bg-[#0B1E36] border border-cyan-500/20">
            <span className="text-slate-400 block">Land Acquired</span>
            <span className="text-lg font-bold font-tech text-emerald-400">{(project?.landAcquired ?? 0).toLocaleString()} Acres</span>
          </div>
          <div className="p-3 rounded-xl bg-[#0B1E36] border border-cyan-500/20">
            <span className="text-slate-400 block">Total Parcels</span>
            <span className="text-lg font-bold font-tech text-cyan-400">{project?.totalParcels ?? 0} Survey Plots</span>
          </div>
          <div className="p-3 rounded-xl bg-[#0B1E36] border border-cyan-500/20">
            <span className="text-slate-400 block">Disbursed Compensation</span>
            <span className="text-lg font-bold font-tech text-purple-400">₹{(project?.compensationDisbursedCr ?? 0).toLocaleString()} Cr</span>
          </div>
        </div>
      </GlassCard>

      {/* Vertical Lifecycle Timeline (10 Acquisition Stages) */}
      <GlassCard className="p-6 sm:p-8">
        <div className="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-cyan-400" />
              <span>Statutory 10-Stage Land Acquisition Timeline</span>
            </h2>
            <p className="text-xs text-slate-400">
              Compliant with RFCTLARR Act 2013 and Section 3A to 3D gazette processes
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-500/30">
            Current: Stage {project.lifecycle.find((s) => s.status === 'In Progress')?.id || 1}
          </span>
        </div>

        <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-emerald-500 before:via-cyan-400 before:to-slate-800">
          {project.lifecycle.map((stage) => {
            const isCompleted = stage.status === 'Completed';
            const isInProgress = stage.status === 'In Progress';
            const isDelayed = stage.status === 'Delayed';

            return (
              <div key={stage.id} className="relative group">
                {/* Node icon */}
                <div
                  className={`absolute -left-6 sm:-left-8 top-1 w-6 h-6 sm:w-8 sm:h-8 rounded-full border flex items-center justify-center bg-[#071A2D] z-10 transition-all ${
                    isCompleted
                      ? 'border-emerald-400 shadow-[0_0_12px_#10B981]'
                      : isInProgress
                      ? 'border-cyan-400 shadow-[0_0_15px_#22D3EE] animate-pulse'
                      : isDelayed
                      ? 'border-rose-400 shadow-[0_0_12px_#EF4444]'
                      : 'border-slate-700 text-slate-500'
                  }`}
                >
                  <span className="text-[11px] font-mono font-bold">
                    {stage.id}
                  </span>
                </div>

                {/* Stage Content Card */}
                <div
                  className={`p-4 sm:p-5 rounded-2xl border transition-all ${getStatusBorder(
                    stage.status
                  )}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2.5">
                      <h3 className="font-bold text-white text-sm sm:text-base tracking-tight">
                        {stage.name}
                      </h3>
                      <StatusBadge status={stage.status} />
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono">
                      <span className="text-slate-400">{stage.completedDate || stage.targetDate || '—'}</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed mb-3">
                    {stage.description}
                  </p>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-xs">
                    <div className="flex items-center gap-1.5 text-slate-400">
                      <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Authorized Officer: </span>
                      <span className="text-white font-medium">{stage.officerInCharge || 'Not assigned'}</span>
                    </div>

                    {/* Quick Action Button for In-Progress Stages */}
                    {isInProgress && stage.id === 7 && (
                      <button
                        onClick={() => {
                          setUserRole('officer');
                          setCurrentView('compensation');
                        }}
                        className="px-3 py-1 rounded-lg bg-cyan-500 text-slate-950 text-xs font-bold shadow-[0_0_12px_rgba(34,211,238,0.4)] hover:bg-cyan-400"
                      >
                        Action Award Approval →
                      </button>
                    )}
                    {isInProgress && stage.id === 3 && (
                      <button
                        onClick={() => {
                          setUserRole('field_officer');
                          setCurrentView('field_upload');
                        }}
                        className="px-3 py-1 rounded-lg bg-emerald-500 text-slate-950 text-xs font-bold shadow-[0_0_12px_rgba(16,185,129,0.4)] hover:bg-emerald-400"
                      >
                        Upload Field Verification →
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
};
