import React from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import {
  Landmark,
  Building2,
  Briefcase,
  Camera,
  UserCheck,
  Shield,
  ArrowRight,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import { UserRole } from '../../types';

export const RoleSelector: React.FC = () => {
  const { setUserRole, setCurrentView, showToast } = useApp();

  const portals: {
    role: UserRole;
    title: string;
    icon: any;
    description: string;
    features: string[];
    buttonText: string;
    accentColor: string;
    borderGlow: string;
  }[] = [
    {
      role: 'central',
      title: 'Central Government',
      icon: Landmark,
      description: 'National-level monitoring and policy analytics for strategic infrastructure corridors.',
      features: [
        'National Dashboard',
        'State-wise Monitoring',
        'Project Analytics',
        'Performance Reports',
      ],
      buttonText: 'Access Central Portal',
      accentColor: 'from-blue-600/30 via-indigo-600/20 to-cyan-500/20 text-blue-400',
      borderGlow: 'hover:border-blue-500/60 shadow-[0_0_25px_rgba(37,99,235,0.2)]',
    },
    {
      role: 'state',
      title: 'State Government',
      icon: Building2,
      description: 'Manage projects and land acquisition activities within the state revenue hierarchy.',
      features: [
        'State Projects',
        'District Monitoring',
        'Proposal Approvals',
        'Progress Tracking',
      ],
      buttonText: 'Access State Portal',
      accentColor: 'from-purple-600/30 via-indigo-600/20 to-blue-500/20 text-purple-400',
      borderGlow: 'hover:border-purple-500/60 shadow-[0_0_25px_rgba(139,92,246,0.2)]',
    },
    {
      role: 'officer',
      title: 'District / Land Acquisition Officer',
      icon: Briefcase,
      description: 'Statutory authority executing valuation, award hearings, compensation approvals and possession.',
      features: [
        'Land Verification',
        'Compensation Approval',
        'Document Verification',
        'Possession Tracking',
      ],
      buttonText: 'Officer Login',
      accentColor: 'from-cyan-600/30 via-blue-600/20 to-teal-500/20 text-cyan-400',
      borderGlow: 'hover:border-cyan-500/60 shadow-[0_0_25px_rgba(34,211,238,0.25)]',
    },
    {
      role: 'field_officer',
      title: 'Field Officer',
      icon: Camera,
      description: 'On-ground survey teams recording GPS coordinates, geo-tagged photographs and landowner consent.',
      features: [
        'Upload Field Photos',
        'Capture GPS Coordinates',
        'Geo-tag Land Boundaries',
        'Upload Documents',
      ],
      buttonText: 'Field Officer Login',
      accentColor: 'from-emerald-600/30 via-teal-600/20 to-cyan-500/20 text-emerald-400',
      borderGlow: 'hover:border-emerald-500/60 shadow-[0_0_25px_rgba(16,185,129,0.2)]',
    },
    {
      role: 'citizen',
      title: 'Citizen / Landowner',
      icon: UserCheck,
      description: 'Direct citizen self-service window ensuring complete transparency and grievance redressing.',
      features: [
        'Track My Land',
        'View Compensation',
        'View Notifications',
        'Upload Documents & eSign',
        'Raise Grievances',
      ],
      buttonText: 'Citizen Login',
      accentColor: 'from-amber-600/30 via-orange-600/20 to-yellow-500/20 text-amber-400',
      borderGlow: 'hover:border-amber-500/60 shadow-[0_0_25px_rgba(245,158,11,0.2)]',
    },
    {
      role: 'admin',
      title: 'System Administrator',
      icon: Shield,
      description: 'Master configuration, user role management, system health and cryptographically signed audit trails.',
      features: [
        'User Management (RBAC)',
        'System Monitoring',
        'Audit Logs & Verification',
        'Geodatabase Security',
      ],
      buttonText: 'Admin Login',
      accentColor: 'from-rose-600/30 via-red-600/20 to-pink-500/20 text-rose-400',
      borderGlow: 'hover:border-rose-500/60 shadow-[0_0_25px_rgba(239,68,68,0.2)]',
    },
  ];

  const handleSelectRole = (role: UserRole) => {
    setUserRole(role);
    setCurrentView('login');
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] bg-[#071A2D] py-12 px-4 sm:px-6 lg:px-8 overflow-hidden">
      <div className="absolute inset-0 gis-grid-pattern opacity-30 pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Page Title */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-3 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5" />
            Role-Based Access Control (RBAC) Architecture
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Select Your Portal
          </h1>
          <p className="mt-3 text-slate-300 text-sm sm:text-base leading-relaxed">
            Choose your designated administrative authority or citizen access point to enter the secure
            national land acquisition workflow.
          </p>
        </div>

        {/* 6 Large Glassmorphic Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {portals.map((portal) => {
            const Icon = portal.icon;
            return (
              <GlassCard
                key={portal.role}
                interactive
                className={`p-6 sm:p-7 flex flex-col justify-between border-slate-800 transition-all duration-300 ${portal.borderGlow}`}
                onClick={() => handleSelectRole(portal.role)}
              >
                <div>
                  {/* Top Icon & Title */}
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`p-3.5 rounded-2xl border bg-gradient-to-br ${portal.accentColor} shadow-inner`}
                    >
                      <Icon className="w-7 h-7" />
                    </div>
                    <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400 bg-slate-900/80 px-2 py-1 rounded border border-slate-800">
                      Tier 0{portals.indexOf(portal) + 1}
                    </span>
                  </div>

                  <h2 className="text-xl font-bold text-white tracking-tight mb-2">
                    {portal.title}
                  </h2>

                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
                    {portal.description}
                  </p>

                  {/* Bulleted Features */}
                  <div className="space-y-2.5 mb-8 border-t border-slate-800/80 pt-4">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Core Operations:
                    </span>
                    {portal.features.map((feat) => (
                      <div key={feat} className="flex items-center gap-2 text-xs text-slate-200">
                        <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Card Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSelectRole(portal.role);
                  }}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_25px_rgba(34,211,238,0.5)] hover:brightness-110 active:scale-95 transition-all"
                >
                  <span>{portal.buttonText}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </GlassCard>
            );
          })}
        </div>
      </div>
    </div>
  );
};
