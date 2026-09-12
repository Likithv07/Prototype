import React from 'react';
import { useApp } from '../../context/AppContext';
import { StatCard } from '../common/StatCard';
import {
  Users,
  Home,
  Briefcase,
  GraduationCap,
  Building,
  CheckCircle2,
  HeartHandshake,
  MapPin,
  TrendingUp,
} from 'lucide-react';

export const RrDashboard: React.FC = () => {
  const { showToast } = useApp();

  const colonies = [
    {
      name: 'Bhoomi Awas Enclave, Suryapet',
      location: 'Telangana (NH-65 Project)',
      allottedUnits: 450,
      completedUnits: 420,
      schoolHospitalStatus: 'Operational',
      waterElectricity: '100% Commissioned',
      livelihoodGrantsDisbursedCr: 24.5,
    },
    {
      name: 'Sahyadri Shanti Vihar, Raigad',
      location: 'Maharashtra (WDFC Corridor)',
      allottedUnits: 720,
      completedUnits: 680,
      schoolHospitalStatus: 'PHC & Primary School Ready',
      waterElectricity: '100% Commissioned',
      livelihoodGrantsDisbursedCr: 58.2,
    },
    {
      name: 'Pragati Nagar Township, Varanasi',
      location: 'Uttar Pradesh (Ganga Expressway)',
      allottedUnits: 600,
      completedUnits: 510,
      schoolHospitalStatus: 'Under Construction (85%)',
      waterElectricity: '90% Commissioned',
      livelihoodGrantsDisbursedCr: 38.0,
    },
  ];

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-700" />
            <span className="text-xs uppercase font-mono text-blue-900 font-bold tracking-wider">
              Second Schedule RFCTLARR Act 2013
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Rehabilitation & Resettlement (R&R) Command
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Monitoring housing allotments, livelihood grants, and skill training for project-affected families.
          </p>
        </div>

        <button
          onClick={() => showToast('Disbursed Q1 R&R subsistence allowance batch to 842 families', 'success')}
          className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold shadow-2xs transition-colors"
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
          color="blue"
        />
        <StatCard
          title="Displaced Requiring Housing"
          value="34,200"
          subtitle="Pucca houses in R&R zones"
          icon={Home}
          color="cyan"
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
      <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Building className="w-5 h-5 text-blue-700" />
              <span>Model Resettlement Colonies & Social Infrastructure</span>
            </h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Infrastructure standards compliant with Third Schedule of RFCTLARR 2013
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">
            92.4% Average Handover
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {colonies.map((col) => (
            <div
              key={col.name}
              className="p-5 rounded-2xl border border-slate-200 bg-slate-50/60 flex flex-col justify-between hover:border-blue-300 transition-all group"
            >
              <div>
                <h3 className="font-bold text-slate-900 text-sm mb-1 group-hover:text-blue-700 transition-colors">
                  {col.name}
                </h3>
                <p className="text-[11px] text-slate-500 mb-4">{col.location}</p>

                <div className="space-y-2.5 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Constructed Units:</span>
                    <span className="font-mono text-emerald-700 font-bold">
                      {col.completedUnits} / {col.allottedUnits}
                    </span>
                  </div>

                  <div className="flex justify-between text-slate-600">
                    <span>Civic Amenities:</span>
                    <span className="text-blue-900 font-semibold">{col.schoolHospitalStatus}</span>
                  </div>

                  <div className="flex justify-between text-slate-600">
                    <span>Power & Water Grid:</span>
                    <span className="text-slate-800 font-medium">{col.waterElectricity}</span>
                  </div>

                  <div className="flex justify-between text-slate-600">
                    <span>Livelihood Grant Paid:</span>
                    <span className="font-mono text-purple-700 font-bold">
                      ₹{col.livelihoodGrantsDisbursedCr} Cr
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-200 flex justify-between items-center text-xs">
                <span className="text-slate-500 font-medium">Handover status:</span>
                <span className="text-emerald-700 font-bold font-mono">
                  {((col.completedUnits / col.allottedUnits) * 100).toFixed(0)}% Ready
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
