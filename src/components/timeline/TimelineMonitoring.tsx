import React from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Clock,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Hourglass,
  ArrowRight,
  ShieldCheck,
  Building,
} from 'lucide-react';

export const TimelineMonitoring: React.FC = () => {
  const { projects, setSelectedProjectId, setCurrentView, showToast } = useApp();

  const timelineItems = [
    {
      id: 'NLA-TS-2026-001',
      name: 'Hyderabad-Vijayawada Expressway Expansion (NH-65)',
      notifDate: '15 Jan 2025',
      deadlineDate: '14 Jan 2026',
      daysRemaining: 124,
      risk: 'Safe',
      riskColor: 'text-emerald-400 bg-emerald-950/70 border-emerald-500/40',
      currentStage: 'Stage 7: Award Hearing',
      slaPercent: 66,
    },
    {
      id: 'NLA-MH-2026-002',
      name: 'Western Dedicated Freight Corridor (Section IV)',
      notifDate: '01 Apr 2025',
      deadlineDate: '31 Mar 2026',
      daysRemaining: 198,
      risk: 'Safe',
      riskColor: 'text-emerald-400 bg-emerald-950/70 border-emerald-500/40',
      currentStage: 'Stage 9: Possession Handover',
      slaPercent: 91,
    },
    {
      id: 'NLA-KA-2026-004',
      name: 'Bengaluru Peripheral Ring Road (Phase 2)',
      notifDate: '10 Feb 2025',
      deadlineDate: '09 Feb 2026',
      daysRemaining: 38,
      risk: 'High Risk (SLA Breach Threat)',
      riskColor: 'text-rose-400 bg-rose-950/80 border-rose-500/40 animate-pulse',
      currentStage: 'Stage 4: Section 3D Pending',
      slaPercent: 44,
    },
    {
      id: 'NLA-UP-2026-003',
      name: 'Ganga Expressway Phase II (Prayagraj-Varanasi)',
      notifDate: '20 May 2025',
      deadlineDate: '19 May 2026',
      daysRemaining: 245,
      risk: 'Safe',
      riskColor: 'text-cyan-400 bg-cyan-950/70 border-cyan-500/40',
      currentStage: 'Stage 6: Valuation Committee',
      slaPercent: 55,
    },
    {
      id: 'NLA-GJ-2026-005',
      name: 'Dholera Special Investment Region Rail Link',
      notifDate: '12 Mar 2025',
      deadlineDate: '11 Mar 2026',
      daysRemaining: 74,
      risk: 'Moderate Risk',
      riskColor: 'text-amber-400 bg-amber-950/70 border-amber-500/40',
      currentStage: 'Stage 7: Solatium Approval',
      slaPercent: 72,
    },
  ];

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
              Statutory 12-Month Lapsing Prevention Monitor
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Timeline Monitoring & SLA Countdown
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Automated statutory countdown under Section 19(7) of RFCTLARR Act to ensure proceedings never lapse.
          </p>
        </div>

        <button
          onClick={() => showToast('Dispatched automated SLA escalation notices to District Collectors', 'success')}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-xs font-semibold shadow-[0_0_15px_rgba(37,99,235,0.4)]"
        >
          Dispatch Collector Escalations
        </button>
      </div>

      {/* Grid of SLA Countdown Cards */}
      <div className="space-y-4">
        {timelineItems.map((item) => (
          <GlassCard key={item.id} className="p-5 sm:p-6">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/70 px-2 py-0.5 rounded border border-cyan-500/30">
                    {item.id}
                  </span>
                  <span className={`text-[11px] font-bold font-mono px-2.5 py-0.5 rounded-full border ${item.riskColor}`}>
                    {item.risk}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  {item.name}
                </h3>
                <p className="text-xs text-slate-400">
                  Current Milestone: <span className="text-slate-200 font-medium">{item.currentStage}</span>
                </p>
              </div>

              {/* Countdown badge & Dates */}
              <div className="flex flex-wrap items-center gap-4 lg:gap-8">
                <div className="text-left sm:text-right">
                  <span className="text-[11px] text-slate-400 block">Section 3A Gazette Date</span>
                  <span className="text-xs font-mono text-slate-200 font-semibold">{item.notifDate}</span>
                </div>

                <div className="text-left sm:text-right">
                  <span className="text-[11px] text-slate-400 block">12-Month Lapsing Limit</span>
                  <span className="text-xs font-mono text-rose-400 font-semibold">{item.deadlineDate}</span>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-700 min-w-[120px] text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-mono block">Days Remaining</span>
                  <span className="font-tech text-2xl font-bold text-cyan-300">
                    {item.daysRemaining}d
                  </span>
                </div>

                <button
                  onClick={() => {
                    setSelectedProjectId(item.id);
                    setCurrentView('project_details');
                  }}
                  className="px-3.5 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5 transition-all"
                >
                  <span>Lifecycle</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-4 pt-3 border-t border-slate-800">
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>Milestone Turnover Rate</span>
                <span className="font-mono text-cyan-300">{item.slaPercent}% completed</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-emerald-400 rounded-full"
                  style={{ width: `${item.slaPercent}%` }}
                />
              </div>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};
