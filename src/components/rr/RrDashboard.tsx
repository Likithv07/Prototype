import React from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatCard } from '../common/StatCard';
import {
  HeartHandshake,
  Users,
  Home,
  Briefcase,
  GraduationCap,
  Building,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

export const RrDashboard: React.FC = () => {
  const { showToast } = useApp();

  const colonies = [
    {
      name: 'BhoomiSetu Ananda Nilayam Resettlement Colony',
      location: 'Ghatkesar, Medchal District, Telangana',
      allottedUnits: 142,
      completedUnits: 138,
      schoolHospitalStatus: 'Operational',
      waterElectricity: '100% Underground Grid',
      livelihoodGrantsDisbursedCr: 4.82,
    },
    {
      name: 'Pragati Nagar R&R Township',
      location: 'Daund, Pune District, Maharashtra',
      allottedUnits: 210,
      completedUnits: 185,
      schoolHospitalStatus: 'Under Construction (85%)',
      waterElectricity: 'Grid Connected',
      livelihoodGrantsDisbursedCr: 7.15,
    },
    {
      name: 'Samruddhi Model Resettlement Village',
      location: 'Bhiwandi, Thane District, Maharashtra',
      allottedUnits: 98,
      completedUnits: 98,
      schoolHospitalStatus: 'Operational & Handed to Gram Panchayat',
      waterElectricity: '100% Solar Powered',
      livelihoodGrantsDisbursedCr: 3.40,
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
              Second Schedule RFCTLARR Act 2013
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Rehabilitation & Resettlement (R&R) Command
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Monitoring housing allotments, livelihood grants, and skill training for project-affected families.
          </p>
        </div>

        <button
          onClick={() => showToast('Disbursed Q1 R&R subsistence allowance batch to 842 families', 'success')}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white text-xs font-semibold shadow-[0_0_15px_rgba(34,211,238,0.4)]"
        >
          Disburse R&R Subsistence Grant
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Affected Families Identified"
          value="1,24,500"
          subtitle="SIA baseline survey"
          icon={Users}
          color="cyan"
        />
        <StatCard
          title="Displaced Requiring Housing"
          value="34,200"
          subtitle="Pucca houses in R&R zones"
          icon={Home}
          color="blue"
        />
        <StatCard
          title="Livelihood Grants Disbursed"
          value="₹842 Crore"
          subtitle="One-time statutory grant"
          icon={Briefcase}
          color="emerald"
        />
        <StatCard
          title="Skill Training Enrolled"
          value="18,450"
          subtitle="PMKVY certified trades"
          icon={GraduationCap}
          color="purple"
        />
      </div>

      {/* Resettlement Colonies Live Status */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Building className="w-5 h-5 text-cyan-400" />
              <span>Model Resettlement Colonies & Social Infrastructure</span>
            </h2>
            <p className="text-xs text-slate-400">
              Infrastructure standards compliant with Third Schedule of RFCTLARR 2013
            </p>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded border border-emerald-500/40">
            92.4% Average Handover
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {colonies.map((col) => (
            <div
              key={col.name}
              className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between hover:border-cyan-500/40 transition-all group"
            >
              <div>
                <h3 className="font-bold text-white text-sm mb-1 group-hover:text-cyan-300 transition-colors">
                  {col.name}
                </h3>
                <p className="text-[11px] text-slate-400 mb-4">{col.location}</p>

                <div className="space-y-2.5 text-xs">
                  <div className="flex justify-between text-slate-300">
                    <span>Constructed Units:</span>
                    <span className="font-mono text-emerald-400 font-bold">
                      {col.completedUnits} / {col.allottedUnits}
                    </span>
                  </div>

                  <div className="flex justify-between text-slate-300">
                    <span>Civic Amenities:</span>
                    <span className="text-cyan-300 font-medium">{col.schoolHospitalStatus}</span>
                  </div>

                  <div className="flex justify-between text-slate-300">
                    <span>Power & Water Grid:</span>
                    <span className="text-white font-medium">{col.waterElectricity}</span>
                  </div>

                  <div className="flex justify-between text-slate-300">
                    <span>Livelihood Grant Paid:</span>
                    <span className="font-mono text-purple-400 font-bold">
                      ₹{col.livelihoodGrantsDisbursedCr} Cr
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
                <span className="text-slate-400">Handover status:</span>
                <span className="text-emerald-400 font-bold font-mono">
                  {((col.completedUnits / col.allottedUnits) * 100).toFixed(0)}% Ready
                </span>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};
