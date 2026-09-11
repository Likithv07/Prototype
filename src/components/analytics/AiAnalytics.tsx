import React from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  Clock,
  Compass,
  FileSearch,
  Cpu,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export const AiAnalytics: React.FC = () => {
  const { projects, landParcels, setCurrentView, setSelectedParcelId, showToast } = useApp();

  const predictions = [
    {
      title: 'Project Delay Risk Prediction',
      riskLevel: 'High',
      badgeColor: 'border-rose-500/40 text-rose-300 bg-rose-500/10',
      description: 'NLA-KA-2026-004 (Bengaluru Peripheral Ring Road) exhibits 78% probability of delay past Section 3D statutory 12-month limit due to heavy litigation in Sarjapur taluk.',
      recommendation: 'Convene Joint Spl. Collector Hearing under Section 15(2) to resolve 14 pending landowner objections before April 30.',
      actionText: 'Inspect Karnataka Corridor',
      targetProject: 'NLA-KA-2026-004',
    },
    {
      title: 'Compensation Discrepancy Detection',
      riskLevel: 'Medium',
      badgeColor: 'border-amber-500/40 text-amber-300 bg-amber-500/10',
      description: 'Survey Parcel TS-HYD-2026-001247 exhibits a 24% valuation variance compared to adjacent registered transaction records in Bibinagar village.',
      recommendation: 'Run automated cadastral comparison with SRO registration sales data to corroborate commercial land rate multiplier.',
      actionText: 'Review Valuation Dossier',
      targetParcel: 'TS-HYD-2026-001247',
    },
    {
      title: 'Land Boundary Overlap & Title Dispute Risk',
      riskLevel: 'Low',
      badgeColor: 'border-emerald-500/40 text-emerald-300 bg-emerald-500/10',
      description: 'AI satellite polygon difference check detected 99.4% agreement with village cadastral maps for Western Dedicated Freight Corridor (NLA-MH-2026-002).',
      recommendation: 'Proceed directly to Section 3D statutory gazette notification without additional ground resurvey.',
      actionText: 'View GIS Cadastral Alignment',
      targetView: 'gis_map',
    },
    {
      title: 'Timeline Bottleneck Prediction',
      riskLevel: 'Medium',
      badgeColor: 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10',
      description: 'PFMS Treasury server latency currently averaging 3.8 business days for rural DBT bank batch settlement in Vidarbha region.',
      recommendation: 'Trigger API batch grouping at 18:00 hrs IST daily to optimize Reserve Bank of India NEFT clearing window.',
      actionText: 'Optimize Payment Pipeline',
      targetView: 'compensation',
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
              Cognitive Predictive Intelligence Core
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            AI Land Acquisition Analytics & Risk Engine
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Machine learning models detecting title disputes, statutory timeline bottlenecks and valuation anomalies.
          </p>
        </div>

        <button
          onClick={() => showToast('AI model re-calibrated against 42,000 national acquisition cases', 'success')}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white text-xs font-semibold flex items-center gap-2 shadow-[0_0_15px_rgba(37,99,235,0.4)]"
        >
          <Sparkles className="w-4 h-4" />
          <span>Re-run Predictive Scan</span>
        </button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard className="p-4 border-emerald-500/30">
          <span className="text-xs text-slate-400">Model Accuracy Score</span>
          <div className="text-2xl font-bold font-tech text-emerald-400 mt-1">96.8%</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Trained on RFCTLARR gazettes</p>
        </GlassCard>
        <GlassCard className="p-4 border-cyan-500/30">
          <span className="text-xs text-slate-400">Predicted Bottlenecks Averted</span>
          <div className="text-2xl font-bold font-tech text-cyan-300 mt-1">142 Days</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Average time saved per project</p>
        </GlassCard>
        <GlassCard className="p-4 border-amber-500/30">
          <span className="text-xs text-slate-400">Active Valuation Alerts</span>
          <div className="text-2xl font-bold font-tech text-amber-400 mt-1">7 Flagged</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Under Joint Collector review</p>
        </GlassCard>
        <GlassCard className="p-4 border-purple-500/30">
          <span className="text-xs text-slate-400">Litigation Risk Reduction</span>
          <div className="text-2xl font-bold font-tech text-purple-400 mt-1">-64%</div>
          <p className="text-[10px] text-slate-400 mt-0.5">Via automated pre-survey consent</p>
        </GlassCard>
      </div>

      {/* Predictions Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {predictions.map((p) => (
          <GlassCard key={p.title} glow className="p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                  <h3 className="font-bold text-white text-sm sm:text-base">{p.title}</h3>
                </div>
                <span
                  className={`text-[11px] font-bold font-mono px-2.5 py-0.5 rounded-full border ${p.badgeColor}`}
                >
                  {p.riskLevel} RISK
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                {p.description}
              </p>

              {/* AI Smart Recommendation Box */}
              <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-xs">
                <div className="flex items-center gap-1.5 text-cyan-300 font-semibold mb-1">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Smart Recommendation for Officers:</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-[11px]">
                  {p.recommendation}
                </p>
              </div>
            </div>

            {/* Action link */}
            <div className="mt-5 pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => {
                  if (p.targetView) {
                    setCurrentView(p.targetView as any);
                  } else if (p.targetParcel) {
                    setSelectedParcelId(p.targetParcel);
                    setCurrentView('compensation');
                  } else {
                    setCurrentView('projects');
                  }
                  showToast(`Opened resolution module for ${p.title}`, 'info');
                }}
                className="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5 transition-all"
              >
                <span>{p.actionText}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  );
};
