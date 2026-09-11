import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { SectorType } from '../../types';
import { SECTORS_CONFIG } from '../../data/sectorData';
import {
  Layers,
  ArrowRight,
  ShieldCheck,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle2,
  FileText,
  DollarSign,
  TrendingUp,
  Download,
  Share2,
  ExternalLink,
  ChevronRight,
  Sparkles,
  Search,
  Filter,
  Check,
  Compass,
  Calculator,
  UserCheck,
  Building,
  Zap,
  Train,
  Truck,
  Eye,
  LogOut,
  RefreshCw,
} from 'lucide-react';

export const SectorDashboard: React.FC = () => {
  const {
    activeSector,
    setActiveSector,
    userRole,
    setUserRole,
    loggedInUser,
    logout,
    setCurrentView,
    setSelectedProjectId,
    setSelectedParcelId,
    projects,
    landParcels,
    showToast,
  } = useApp();

  const [activeTab, setActiveTab] = useState<'overview' | 'corridors' | 'actions' | 'statutory'>('overview');
  const [filterQuery, setFilterQuery] = useState('');
  const [selectedActionItem, setSelectedActionItem] = useState<string | null>(null);

  const sector = SECTORS_CONFIG[activeSector] || SECTORS_CONFIG.highways;

  const handleSwitchSector = (s: SectorType) => {
    setActiveSector(s);
    const roleMapping: Record<SectorType, any> = {
      highways: 'central',
      railways: 'central',
      power: 'officer',
      urban: 'state',
      revenue: 'officer',
      citizen: 'citizen',
    };
    setUserRole(roleMapping[s]);
    showToast(`Switched active view to ${SECTORS_CONFIG[s].name}`, 'info');
  };

  const handleActionExecute = (actionTitle: string) => {
    showToast(`Executed: ${actionTitle}`, 'success');
  };

  const getSectorIcon = (sec: SectorType) => {
    switch (sec) {
      case 'highways':
        return Truck;
      case 'railways':
        return Train;
      case 'power':
        return Zap;
      case 'urban':
        return Building;
      case 'revenue':
        return ShieldCheck;
      case 'citizen':
        return UserCheck;
      default:
        return Layers;
    }
  };

  const SectorIcon = getSectorIcon(activeSector);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header & Sector Switcher */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-sm backdrop-blur-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-11 h-11 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
              <SectorIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">
                  {sector.badge}
                </span>
                <span className="text-xs text-slate-400">
                  {sector.department}
                </span>
              </div>
              <h1 className="text-xl font-bold text-white mt-1">
                {sector.name} Dashboard
              </h1>
              <p className="text-xs text-slate-400 mt-0.5 max-w-2xl">
                {sector.heroTagline}
              </p>
            </div>
          </div>

          {/* Right Action: Officer identity & Log Out */}
          <div className="flex items-center gap-3 self-end lg:self-center">
            <div className="text-right hidden sm:block">
              <span className="text-xs text-slate-300 font-medium block">
                {loggedInUser || sector.officerDesignation}
              </span>
              <span className="text-[11px] text-emerald-400 font-mono">
                Class-3 DSC Verified
              </span>
            </div>
            <button
              onClick={logout}
              id="sector-logout-btn"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 border border-slate-700 rounded-lg transition-colors"
              title="Sign Out to BhoomiSetu Landing Page"
            >
              <LogOut className="w-3.5 h-3.5 text-slate-400" />
              <span>Log Out</span>
            </button>
          </div>
        </div>

        {/* Minimal Sector Switcher Bar */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 scrollbar-none">
            <span className="text-xs text-slate-400 font-medium mr-1 shrink-0">
              Sector:
            </span>
            {(['highways', 'railways', 'power', 'urban', 'revenue', 'citizen'] as SectorType[]).map((secKey) => {
              const secItem = SECTORS_CONFIG[secKey];
              const isCurrent = activeSector === secKey;
              const IconComp = getSectorIcon(secKey);
              return (
                <button
                  key={secKey}
                  onClick={() => handleSwitchSector(secKey)}
                  id={`sector-switch-${secKey}`}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 ${
                    isCurrent
                      ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  <IconComp className="w-3.5 h-3.5" />
                  <span>{secItem.shortName}</span>
                </button>
              );
            })}
          </div>

          <div className="flex items-center gap-2 text-xs">
            <button
              onClick={() => setCurrentView('gis_map')}
              className="px-2.5 py-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-md flex items-center gap-1"
            >
              <Compass className="w-3 h-3 text-cyan-400" />
              <span>GIS Map</span>
            </button>
            <button
              onClick={() => setCurrentView('compensation')}
              className="px-2.5 py-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-md flex items-center gap-1"
            >
              <Calculator className="w-3 h-3 text-emerald-400" />
              <span>Valuation Calculator</span>
            </button>
            <button
              onClick={() => setCurrentView('documents')}
              className="px-2.5 py-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700/80 border border-slate-700 rounded-md flex items-center gap-1"
            >
              <FileText className="w-3 h-3 text-amber-400" />
              <span>Gazettes</span>
            </button>
          </div>
        </div>
      </div>

      {/* Primary KPI Metric Cards (Main info needed specifically for this sector) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {sector.primaryMetrics.map((metric, idx) => (
          <div
            key={idx}
            className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-sm relative overflow-hidden"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
              <span>{metric.label}</span>
              {metric.statusColor === 'emerald' ? (
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
              ) : metric.statusColor === 'cyan' ? (
                <span className="w-2 h-2 rounded-full bg-cyan-400" />
              ) : (
                <span className="w-2 h-2 rounded-full bg-amber-400" />
              )}
            </div>
            <div className="text-2xl font-bold font-tech text-white tracking-tight">
              {metric.value}
            </div>
            <p className="text-[11px] text-slate-400 mt-1 leading-tight">
              {metric.subtext}
            </p>
            {metric.trend && (
              <div className="mt-2 text-[10px] text-emerald-400 flex items-center gap-1 font-medium">
                <TrendingUp className="w-3 h-3" />
                <span>{metric.trend}</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Urgent Interventions & Action Items for the Sector */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              High-Priority Interventions ({sector.name})
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            Automated SLA Tracking
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {sector.actionItems.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/90 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    {item.category}
                  </span>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded ${
                      item.urgency === 'critical'
                        ? 'text-rose-400 bg-rose-950/40 border border-rose-800/40'
                        : item.urgency === 'high'
                        ? 'text-amber-400 bg-amber-950/40 border border-amber-800/40'
                        : 'text-slate-400 bg-slate-800'
                    }`}
                  >
                    {item.urgency}
                  </span>
                </div>
                <h3 className="text-xs font-semibold text-slate-200 line-clamp-1">
                  {item.title}
                </h3>
                <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                  {item.detail}
                </p>
              </div>

              <button
                onClick={() => handleActionExecute(item.actionText)}
                className="mt-3 w-full py-1.5 px-3 rounded-md bg-slate-800 hover:bg-emerald-600 hover:text-white text-emerald-400 border border-slate-700 hover:border-emerald-500 text-xs font-medium transition-all flex items-center justify-center gap-1"
              >
                <span>{item.actionText}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Sector-Specific Deep Dive Panels */}
      {activeSector === 'highways' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
                National Highway & Expressway Corridor Packages
              </h2>
              <p className="text-xs text-slate-400">
                Tracking 60-meter continuous Right-of-Way (RoW) acquisition and Section 3D gazette vesting
              </p>
            </div>
            <button
              onClick={() => setCurrentView('projects')}
              className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 self-start sm:self-auto"
            >
              <span>View All 12 Packages</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2.5 font-medium">Package / Corridor</th>
                  <th className="pb-2.5 font-medium">State / District</th>
                  <th className="pb-2.5 font-medium">Total Land</th>
                  <th className="pb-2.5 font-medium">60m RoW Cleared</th>
                  <th className="pb-2.5 font-medium">Statutory Milestone</th>
                  <th className="pb-2.5 font-medium">Disbursed (Cr)</th>
                  <th className="pb-2.5 font-medium text-right">Civil Handover</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                <tr className="hover:bg-slate-800/30">
                  <td className="py-3 font-semibold text-white">
                    NH-65 Corridor Expansion (Hyderabad–Vijayawada)
                  </td>
                  <td className="py-3 text-slate-400">Telangana (Nalgonda)</td>
                  <td className="py-3 font-mono">1,250 Ac</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-emerald-400 h-full rounded-full" style={{ width: '65%' }} />
                      </div>
                      <span className="font-mono text-[11px] text-emerald-400">65%</span>
                    </div>
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-cyan-950/50 text-cyan-300 border border-cyan-800/40">
                      Sec 3D Declared
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-200">₹614.2 Cr</td>
                  <td className="py-3 text-right">
                    <span className="text-emerald-400 font-medium">Ready (Pkg 1-2)</span>
                  </td>
                </tr>
                <tr className="hover:bg-slate-800/30">
                  <td className="py-3 font-semibold text-white">
                    Varanasi–Ranchi–Kolkata Green Expressway
                  </td>
                  <td className="py-3 text-slate-400">Uttar Pradesh (Chandauli)</td>
                  <td className="py-3 font-mono">1,850 Ac</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-amber-400 h-full rounded-full" style={{ width: '40%' }} />
                      </div>
                      <span className="font-mono text-[11px] text-amber-400">40%</span>
                    </div>
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-amber-950/50 text-amber-300 border border-amber-800/40">
                      Sec 3A Hearings
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-200">₹410.8 Cr</td>
                  <td className="py-3 text-right">
                    <span className="text-amber-400 font-medium">Pending Forest RoW</span>
                  </td>
                </tr>
                <tr className="hover:bg-slate-800/30">
                  <td className="py-3 font-semibold text-white">
                    Bengaluru–Chennai Expressway (Section 1)
                  </td>
                  <td className="py-3 text-slate-400">Karnataka (Kolar)</td>
                  <td className="py-3 font-mono">1,600 Ac</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-emerald-400 h-full rounded-full" style={{ width: '92%' }} />
                      </div>
                      <span className="font-mono text-[11px] text-emerald-400">92%</span>
                    </div>
                  </td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-950/50 text-emerald-300 border border-emerald-800/40">
                      Sec 3G Awards Paid
                    </span>
                  </td>
                  <td className="py-3 font-mono text-slate-200">₹1,220.0 Cr</td>
                  <td className="py-3 text-right">
                    <span className="text-emerald-400 font-medium">Possession Given</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeSector === 'railways' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Railways & High-Speed Rail Corridor Verification
            </h2>
            <p className="text-xs text-slate-400">
              Joint Measurement Surveys (JMS) and 30m track safety zone clearance with State Revenue
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-3">
              <span className="font-semibold text-white block">
                Joint Measurement Survey (JMS) Status
              </span>
              <div className="space-y-2">
                <div className="flex justify-between text-slate-400">
                  <span>Completed Joint Surveys</span>
                  <span className="text-emerald-400 font-mono font-bold">1,840 Plots (94.3%)</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Pending Revenue Tehsildar Sign-off</span>
                  <span className="text-amber-400 font-mono font-bold">64 Plots</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Disputed Cadastral Boundaries</span>
                  <span className="text-rose-400 font-mono font-bold">46 Plots</span>
                </div>
              </div>
              <button
                onClick={() => showToast('Dispatched verification request to District Tehsildar', 'success')}
                className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 text-xs font-medium"
              >
                Send Tehsildar Expedite Notice
              </button>
            </div>

            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-3">
              <span className="font-semibold text-white block">
                High-Speed Rail Safety Zone & Yards
              </span>
              <div className="space-y-2">
                <div className="flex justify-between text-slate-400">
                  <span>30m Safety Buffer Zone Clear</span>
                  <span className="text-emerald-400 font-mono font-bold">328 km / 360 km</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Traction Substations (TSS) Sites</span>
                  <span className="text-cyan-400 font-mono font-bold">8 of 9 Possessed</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Passenger Station Yards Acquired</span>
                  <span className="text-purple-400 font-mono font-bold">12 / 12 Stations</span>
                </div>
              </div>
              <button
                onClick={() => setCurrentView('gis_map')}
                className="w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 text-xs font-medium"
              >
                Inspect Track Center-Line GIS
              </button>
            </div>
          </div>
        </div>
      )}

      {activeSector === 'power' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              765kV / 400kV Transmission Tower Footings & Wire RoW
            </h2>
            <p className="text-xs text-slate-400">
              Distinguishing permanent base plot acquisition from line-stringing easement rights under Indian Telegraph Act
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 block mb-1">Tower Base Acquisitions</span>
              <span className="text-xl font-bold font-tech text-white">1,420 Tower Bases</span>
              <p className="text-slate-400 text-[11px] mt-1">
                400 m² permanent purchase per base location for foundation pile works
              </p>
            </div>
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 block mb-1">Crop & Tree Diminution</span>
              <span className="text-xl font-bold font-tech text-emerald-400">₹84.6 Cr Sanctioned</span>
              <p className="text-slate-400 text-[11px] mt-1">
                85% land value diminution compensation for transmission wire corridor
              </p>
            </div>
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800">
              <span className="text-slate-400 block mb-1">Grid Substation Assembly</span>
              <span className="text-xl font-bold font-tech text-cyan-400">120 Acres Acquired</span>
              <p className="text-slate-400 text-[11px] mt-1">
                765kV Inter-State transmission pooling substation in Wardha
              </p>
            </div>
          </div>
        </div>
      )}

      {activeSector === 'urban' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Industrial Corridors & Land Pooling Schemes (TPS)
            </h2>
            <p className="text-xs text-slate-400">
              Equitable land reconstitution for industrial clusters and smart cities
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
              <span className="font-semibold text-white block">Land Pooling (50:50 Reconstitution)</span>
              <p className="text-slate-400 text-[11px]">
                Under Town Planning Schemes, 4,100 agricultural plots were pooled and reconstituted into developed commercial/industrial plots with trunk utilities.
              </p>
              <div className="flex justify-between font-mono text-slate-300 pt-2 border-t border-slate-800">
                <span>Farmer Consent Rate:</span>
                <span className="text-emerald-400 font-bold">92.4% Verified</span>
              </div>
            </div>

            <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 space-y-2">
              <span className="font-semibold text-white block">Plug-and-Play Industrial Allotment</span>
              <p className="text-slate-400 text-[11px]">
                142 demarcated plots ready with utility pipelines, optic fiber, and power substation connections for global manufacturing investment.
              </p>
              <div className="flex justify-between font-mono text-slate-300 pt-2 border-t border-slate-800">
                <span>Allotted to Anchor Units:</span>
                <span className="text-cyan-400 font-bold">48 Mega Plots</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSector === 'revenue' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
                District Revenue Administration & Statutory Section 19 SLA
              </h2>
              <p className="text-xs text-slate-400">
                Mandatory 12-month lapsing countdown per RFCTLARR Act 2013 and Class-3 DSC award sign-off
              </p>
            </div>
            <button
              onClick={() => setCurrentView('compensation')}
              className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              <span>Award Determination Queue</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="p-4 rounded-lg bg-amber-950/20 border border-amber-500/30 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/20 text-amber-300 flex items-center justify-center shrink-0">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <span className="font-semibold text-white text-xs block">
                  Statutory Section 19 Lapsing Watchdog: 0 Notices Lapsed
                </span>
                <span className="text-[11px] text-slate-300">
                  NH-65 Expressway Package 1 requires award declaration within 22 days to avoid automatic statutory lapse.
                </span>
              </div>
            </div>
            <button
              onClick={() => setCurrentView('compensation')}
              className="px-3 py-1.5 rounded-lg bg-amber-500 text-slate-950 font-semibold text-xs shrink-0 hover:bg-amber-400"
            >
              Sign Collector Award
            </button>
          </div>
        </div>
      )}

      {activeSector === 'citizen' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Landowner Self-Service Portal & Certified Award
            </h2>
            <p className="text-xs text-slate-400">
              Transparent statutory valuation breakdown per RFCTLARR Act 2013 with 100% Solatium
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800 text-xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
              <div>
                <span className="text-slate-400 block text-[11px]">Landowner Name & Survey Plot</span>
                <span className="text-sm font-bold text-white">Rajesh Kumar • Survey No. 145/2 (1.75 Acres)</span>
                <span className="text-slate-400 block text-[11px]">Village Shivampet, Nalgonda, Telangana</span>
              </div>
              <div className="text-left sm:text-right">
                <span className="text-slate-400 block text-[11px]">Total Sanctioned Award</span>
                <span className="text-2xl font-bold font-tech text-emerald-400">₹72,25,000</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Basic Market Rate</span>
                <span className="font-mono text-slate-200">₹24,00,000 / Ac</span>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">Rural Multiplier</span>
                <span className="font-mono text-emerald-400 font-bold">1.5x Factor</span>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">100% Solatium</span>
                <span className="font-mono text-emerald-400 font-bold">₹33,75,000</span>
              </div>
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800">
                <span className="text-slate-400 block text-[10px]">DBT Bank Link</span>
                <span className="font-mono text-cyan-400">SBI (•••• 4091)</span>
              </div>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-2">
              <span className="text-[11px] text-slate-400">
                Aadhaar eSign seals your direct treasury deposit via PFMS with zero deductions.
              </span>
              <button
                onClick={() => {
                  showToast('Aadhaar OTP verification initiated. Digital consent signed!', 'success');
                }}
                className="w-full sm:w-auto px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
              >
                Aadhaar eSign Consent Agreement
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Highlights & Key Features of this Sector */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
          Sector Workflow Capabilities
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {sector.keyHighlights.map((highlight, index) => (
            <div key={index} className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{highlight}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
