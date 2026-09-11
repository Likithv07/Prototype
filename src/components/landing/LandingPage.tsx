import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { SECTORS_CONFIG } from '../../data/sectorData';
import { SectorType } from '../../types';
import {
  Compass,
  FileCheck2,
  Calculator,
  ShieldCheck,
  Search,
  ArrowRight,
  TrendingUp,
  Layers,
  Sparkles,
  CheckCircle2,
  Lock,
  Building,
  Zap,
  Train,
  Truck,
  UserCheck,
  ExternalLink,
  ChevronRight,
  Clock,
  Landmark,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { setCurrentView, setActiveSector, setSelectedParcelId, showToast } = useApp();
  const [trackingId, setTrackingId] = useState('');
  const [searchResult, setSearchResult] = useState<any | null>(null);

  const handleTrackSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!trackingId.trim()) {
      showToast('Please enter a Survey Number or Parcel ID', 'warning');
      return;
    }
    const sample = {
      id: trackingId.trim(),
      village: 'Village Shivampet, Nalgonda, Telangana',
      area: '1.75 Acres (7,082 m²)',
      sector: 'Highways (NH-65 Expressway)',
      status: 'Section 3D Gazetted (Title Vested in Govt)',
      solatium: '₹33,75,000 (100% Calculated)',
      totalAward: '₹72,25,000',
      bankStatus: 'PFMS Pre-Validated (SBI)',
    };
    setSearchResult(sample);
    showToast(`Survey Plot ${trackingId.trim()} found in BhoomiSetu registry`, 'success');
  };

  const handleEnterSector = (sectorKey: SectorType) => {
    setActiveSector(sectorKey);
    setCurrentView('login');
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

  return (
    <div className="space-y-16 py-4 max-w-7xl mx-auto">
      {/* Top Banner / Hero introducing BhoomiSetu */}
      <section className="relative rounded-2xl bg-slate-900/80 border border-slate-800 p-8 sm:p-12 shadow-sm overflow-hidden">
        {/* Top bar inside hero with brand and highlighted Login button */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 mb-8 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Landmark className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white tracking-wide">
                  BhoomiSetu
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                  National Portal
                </span>
              </div>
              <span className="text-xs text-slate-400 block">
                Digital Land Acquisition Governance • Govt. of India
              </span>
            </div>
          </div>

          {/* Highlighted Login button in the top right */}
          <div className="flex items-center gap-3 self-start sm:self-auto">
            <button
              onClick={() => setCurrentView('login')}
              id="landing-header-login-btn"
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm hover:shadow transition-all flex items-center gap-2 group"
            >
              <Lock className="w-3.5 h-3.5 text-emerald-200 group-hover:text-white" />
              <span>Sector Login</span>
              <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
            </button>
          </div>
        </div>

        {/* Hero Copy */}
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/90 text-slate-300 border border-slate-700 text-xs">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>Statutory Compliance with RFCTLARR Act 2013</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Unified Digital Governance for National Land Acquisition
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            <strong className="text-white">BhoomiSetu</strong> is India’s centralized digital bridge connecting Infrastructure Sectors, State Revenue Authorities, and Citizens. Built to eliminate administrative delays, enforce statutory 12-month lapsing timelines, automate 100% Solatium calculations, and disburse compensation straight into landowners’ bank accounts through direct PFMS integration.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setCurrentView('login')}
              id="landing-hero-login-btn"
              className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-sm transition-all flex items-center gap-2"
            >
              <span>Access Sector Portals</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <a
              href="#sectors-section"
              className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
            >
              Explore 6 Core Sectors
            </a>
            <a
              href="#track-parcel-section"
              className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-all"
            >
              Check Survey Plot Status
            </a>
          </div>
        </div>

        {/* Key Metrics Strip */}
        <div className="mt-10 pt-8 border-t border-slate-800 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-3.5 rounded-lg bg-slate-950/40 border border-slate-800/80">
            <span className="text-2xl font-bold font-tech text-white">6 Sectors</span>
            <span className="block text-xs text-slate-400 mt-0.5">Highways, Rail, Power, Urban, Revenue, Citizen</span>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-950/40 border border-slate-800/80">
            <span className="text-2xl font-bold font-tech text-emerald-400">8,420+ km</span>
            <span className="block text-xs text-slate-400 mt-0.5">Corridors DGPS Demarcated</span>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-950/40 border border-slate-800/80">
            <span className="text-2xl font-bold font-tech text-cyan-400">18,500+</span>
            <span className="block text-xs text-slate-400 mt-0.5">Survey Plots Digitized</span>
          </div>
          <div className="p-3.5 rounded-lg bg-slate-950/40 border border-slate-800/80">
            <span className="text-2xl font-bold font-tech text-emerald-400">₹4,820 Cr</span>
            <span className="block text-xs text-slate-400 mt-0.5">Disbursed via Direct Bank PFMS</span>
          </div>
        </div>
      </section>

      {/* About BhoomiSetu - Architectural Pillars */}
      <section className="space-y-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Core Architecture
          </span>
          <h2 className="text-2xl font-bold text-white mt-1">
            How BhoomiSetu Solves the Land Acquisition Bottleneck
          </h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Designed to address the four historic root causes of infrastructure delays in India: title ambiguity, valuation disputes, statutory deadline lapsing, and payment delays.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Calculator className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white">Automated RFCTLARR Valuation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Computes base market rates, applies rural distance multipliers (1.5x–2.0x), calculates 100% Solatium, and adds 12% statutory interest automatically.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <Compass className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white">Cadastral DGPS & Drone GIS</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Integrates drone orthomosaic maps with village revenue Khasra sheets to pinpoint exact survey boundaries with sub-meter accuracy.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white">Section 19 SLA Watchdog</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enforces the strict 12-month statutory deadline between Preliminary Notification and Award Declaration, sending automated alerts to District Collectors.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-white">PFMS Direct Benefit Transfer</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Links sanctioned awards directly to beneficiary bank accounts via Aadhaar, guaranteeing immediate compensation release without middlemen.
            </p>
          </div>
        </div>
      </section>

      {/* Sector Portals Section */}
      <section id="sectors-section" className="space-y-6 scroll-mt-20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              Sector Specialization
            </span>
            <h2 className="text-2xl font-bold text-white mt-1">
              Sector-Specific Portals & Dashboards
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select your sector to authenticate and view information tailored to your operational workflows:
            </p>
          </div>
          <button
            onClick={() => setCurrentView('login')}
            className="self-start sm:self-auto text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
          >
            <span>Proceed to Login</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(['highways', 'railways', 'power', 'urban', 'revenue', 'citizen'] as SectorType[]).map((secKey) => {
            const sec = SECTORS_CONFIG[secKey];
            const IconComponent = getSectorIcon(secKey);
            return (
              <div
                key={secKey}
                className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">
                      {sec.badge}
                    </span>
                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                      <IconComponent className="w-4 h-4" />
                    </div>
                  </div>

                  <h3 className="text-sm font-bold text-white">{sec.name}</h3>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed line-clamp-3">
                    {sec.tagline}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  <button
                    onClick={() => handleEnterSector(secKey)}
                    id={`enter-sector-${secKey}`}
                    className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-emerald-600 hover:text-white text-emerald-400 border border-slate-700 hover:border-emerald-500 text-xs font-semibold transition-all flex items-center justify-center gap-1.5"
                  >
                    <span>Enter {sec.shortName} Portal</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Public Land Parcel Tracking Bar */}
      <section id="track-parcel-section" className="rounded-xl bg-slate-900/60 border border-slate-800 p-6 sm:p-8 space-y-4 scroll-mt-20">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Citizen Transparency
          </span>
          <h2 className="text-xl font-bold text-white mt-1">
            Search Public Survey Plot & Compensation Status
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enter your Survey Number, Khasra Number, or Land Parcel ID to view gazette status, valuation breakdown, and disbursement timeline.
          </p>
        </div>

        <form onSubmit={handleTrackSubmit} className="flex flex-col sm:flex-row gap-2 max-w-xl">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={trackingId}
              onChange={(e) => setTrackingId(e.target.value)}
              placeholder="e.g. TS-HYD-2026-001245 or Sy. No. 145/2"
              className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button
            type="submit"
            id="track-parcel-submit-btn"
            className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors shrink-0 flex items-center justify-center gap-1.5"
          >
            <span>Search Plot</span>
            <Search className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Quick Demo Search Pills */}
        <div className="flex items-center gap-2 text-xs text-slate-400 flex-wrap">
          <span className="text-[11px]">Demo queries:</span>
          <button
            type="button"
            onClick={() => {
              setTrackingId('TS-HYD-2026-001245');
              handleTrackSubmit({ preventDefault: () => {} } as any);
            }}
            className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-mono border border-slate-700"
          >
            TS-HYD-2026-001245 (Shivampet)
          </button>
          <button
            type="button"
            onClick={() => {
              setTrackingId('MH-PAL-2026-003810');
              handleTrackSubmit({ preventDefault: () => {} } as any);
            }}
            className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-mono border border-slate-700"
          >
            MH-PAL-2026-003810 (Bullet Train)
          </button>
        </div>

        {/* Search Result Card if searched */}
        {searchResult && (
          <div className="mt-4 p-4 rounded-lg bg-slate-950 border border-emerald-500/30 text-xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-800">
              <div>
                <span className="text-[11px] text-emerald-400 font-mono font-medium block">
                  VERIFIED RECORD FOUND
                </span>
                <span className="text-sm font-bold text-white">
                  Plot ID: {searchResult.id} • {searchResult.village}
                </span>
              </div>
              <span className="px-2 py-1 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px] font-semibold self-start sm:self-auto">
                {searchResult.status}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <span className="text-slate-400 text-[11px] block">Project Sector</span>
                <span className="text-slate-200 font-medium">{searchResult.sector}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Notified Area</span>
                <span className="text-slate-200 font-mono">{searchResult.area}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">100% Solatium Award</span>
                <span className="text-emerald-400 font-mono font-bold">{searchResult.solatium}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Total Sanctioned</span>
                <span className="text-emerald-400 font-mono font-bold">{searchResult.totalAward}</span>
              </div>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-2">
              <span className="text-[11px] text-slate-400">
                Direct Benefit Transfer status: <strong className="text-cyan-400">{searchResult.bankStatus}</strong>
              </span>
              <button
                onClick={() => {
                  setActiveSector('citizen');
                  setCurrentView('login');
                }}
                className="w-full sm:w-auto px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center justify-center gap-1"
              >
                <span>Login to eSign Consent</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Minimal Footer */}
      <footer className="pt-8 border-t border-slate-800/80 text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-slate-300 font-semibold">BhoomiSetu Portal</span>
          <span className="block text-[11px] text-slate-400">
            Compliant with RFCTLARR Act 2013 & National Spatial Data Infrastructure
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setCurrentView('login')}
            className="text-emerald-400 hover:underline font-semibold"
          >
            Sector Login
          </button>
          <button
            onClick={() => setCurrentView('scope')}
            className="hover:text-slate-300"
          >
            Statutory Scope
          </button>
          <button
            onClick={() => setCurrentView('gis_map')}
            className="hover:text-slate-300"
          >
            GIS Map
          </button>
        </div>
      </footer>
    </div>
  );
};
