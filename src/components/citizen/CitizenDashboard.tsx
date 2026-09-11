import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  MapPin,
  CreditCard,
  CheckCircle2,
  Clock,
  FileCheck,
  AlertCircle,
  Download,
  Fingerprint,
  FileText,
  Compass,
  MessageSquarePlus,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  ArrowRight,
} from 'lucide-react';

export const CitizenDashboard: React.FC = () => {
  const {
    landParcels,
    selectedParcelId,
    setCurrentView,
    submitConsent,
    showToast,
  } = useApp();

  // Find user's parcel (default to primary demo parcel)
  const citizenParcel =
    landParcels.find((p) => p.id === selectedParcelId) || landParcels[0];

  const [eSignConsentChecked, setESignConsentChecked] = useState(false);
  const [showSignModal, setShowSignModal] = useState(false);
  const [aadhaarOtp, setAadhaarOtp] = useState('781923');

  const handleExecuteESign = () => {
    submitConsent(citizenParcel.id);
    setShowSignModal(false);
  };

  const steps = [
    { name: 'DPR & Preliminary Section 3A', status: 'Completed', date: '10 Jan 2026' },
    { name: 'Drone LiDAR & Joint Measurement', status: 'Completed', date: '28 Jan 2026' },
    { name: 'Public Hearing & Objection Review', status: 'Completed', date: '14 Feb 2026' },
    { name: 'Section 3D Declaration Gazette', status: 'Completed', date: '02 Mar 2026' },
    { name: 'Statutory Award Calculation', status: 'Completed', date: '08 Mar 2026' },
    {
      name: 'Compensation Disbursal (PFMS DBT)',
      status: citizenParcel.compensationStatus === 'Approved' ? 'Completed' : 'In Progress',
      date: citizenParcel.compensationStatus === 'Approved' ? 'Ready for Transfer' : 'Under Officer Seal',
    },
    { name: 'Physical Handover of Possession', status: 'Pending', date: 'Est. 15 Apr 2026' },
  ];

  return (
    <div className="space-y-6 pb-16">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-amber-400 font-semibold tracking-wider">
              Citizen Direct Benefits & Transparency Portal
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            My Land Acquisition & Compensation
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Official records for Shri {citizenParcel.landownerName} • Aadhaar {citizenParcel.landownerAadhaar}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentView('grievance')}
            className="px-3.5 py-2 rounded-xl bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/40 text-xs font-semibold flex items-center gap-1.5"
          >
            <MessageSquarePlus className="w-3.5 h-3.5" />
            <span>Raise a Grievance</span>
          </button>
          <button
            onClick={() => setCurrentView('gis_map')}
            className="px-3.5 py-2 rounded-xl bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5" />
            <span>View My Land on GIS</span>
          </button>
        </div>
      </div>

      {/* Main Land Card & Live Compensation Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Land Particulars */}
        <GlassCard glow className="lg:col-span-7 p-6 border-cyan-500/30">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div>
              <span className="text-[10px] font-mono text-cyan-400 uppercase font-bold">
                Gazetted Record
              </span>
              <h2 className="text-lg font-bold text-white">
                Survey No: {citizenParcel.surveyNumber}
              </h2>
            </div>
            <StatusBadge status={citizenParcel.status} />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs mb-6">
            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Acquired Extent</span>
              <span className="font-tech text-base font-bold text-white">
                {citizenParcel.areaAcres} Acres
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Land Classification</span>
              <span className="font-semibold text-cyan-300">
                {citizenParcel.landType}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Revenue Mandal</span>
              <span className="font-semibold text-slate-200">
                {citizenParcel.village}
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Basic Unit Rate</span>
              <span className="font-mono text-slate-200">
                ₹{(citizenParcel.compensation?.governmentRatePerAcre || citizenParcel.marketValuePerAcre || 2400000).toLocaleString('en-IN')}/Ac
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Multiplier Factor</span>
              <span className="font-mono text-emerald-400 font-bold">
                {citizenParcel.multiplierFactor || 1.5}x (Rural)
              </span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-slate-400 block mb-1">Solatium Guarantee</span>
              <span className="font-mono text-purple-400 font-bold">
                100% Statutory
              </span>
            </div>
          </div>

          {/* eSign Consent Box */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/30">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Fingerprint className="w-5 h-5 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Digital Consent eSign</h3>
              </div>
              {citizenParcel.consentReceived ? (
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/40">
                  eSIGN COMPLETED
                </span>
              ) : (
                <span className="text-[10px] font-mono text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded border border-amber-500/40">
                  ACTION REQUIRED
                </span>
              )}
            </div>

            {citizenParcel.consentReceived ? (
              <p className="text-xs text-emerald-300">
                Consent form digitally eSigned on {citizenParcel.consentDate} via Aadhaar eSign
                OTP verification. Award is queued for final PFMS treasury transfer.
              </p>
            ) : (
              <div>
                <p className="text-xs text-slate-300 mb-3">
                  Under RFCTLARR 2013, confirm your acceptance of the joint survey and statutory award
                  valuation through Aadhaar eSign.
                </p>
                <button
                  onClick={() => setShowSignModal(true)}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold text-xs shadow-[0_0_15px_rgba(34,211,238,0.4)] flex items-center gap-2"
                >
                  <Fingerprint className="w-4 h-4" />
                  <span>Execute Aadhaar eSign Consent Now</span>
                </button>
              </div>
            )}
          </div>
        </GlassCard>

        {/* Compensation & Bank Payment Particulars */}
        <GlassCard glow className="lg:col-span-5 p-6 flex flex-col justify-between border-emerald-500/30">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-white">
                  Compensation Award Summary
                </h2>
              </div>
              <StatusBadge status={citizenParcel.compensationStatus} />
            </div>

            <div className="p-4 rounded-xl bg-emerald-950/50 border border-emerald-500/40 mb-4">
              <span className="text-emerald-300 text-xs block mb-0.5">
                Total Statutory Award Sanctioned:
              </span>
              <span className="font-tech text-3xl font-extrabold text-emerald-400 tracking-tight">
                ₹{(citizenParcel.compensation?.totalCompensation || citizenParcel.totalCompensation || 0).toLocaleString('en-IN')}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">
                Inclusive of 100% Solatium (₹33.75L) & Asset Valuation (₹4.75L)
              </p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between text-slate-400 border-b border-slate-800/80 pb-1.5">
                <span>Beneficiary Account:</span>
                <span className="font-mono text-white font-semibold">
                  State Bank of India (•••4892)
                </span>
              </div>
              <div className="flex justify-between text-slate-400 border-b border-slate-800/80 pb-1.5">
                <span>IFSC Code:</span>
                <span className="font-mono text-white">SBIN0004128</span>
              </div>
              <div className="flex justify-between text-slate-400 border-b border-slate-800/80 pb-1.5">
                <span>PFMS Payment Mandate:</span>
                <span className="font-mono text-cyan-400">PFMS-GOI-2026-88194</span>
              </div>
              <div className="flex justify-between text-slate-400 border-b border-slate-800/80 pb-1.5">
                <span>Disbursal Method:</span>
                <span className="text-emerald-400 font-semibold">
                  Direct Benefit Transfer (DBT)
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-3 border-t border-slate-800">
            <button
              onClick={() => showToast('Downloaded Form 16-C Award Certificate PDF', 'success')}
              className="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center gap-2 border border-slate-700 transition-all"
            >
              <Download className="w-4 h-4 text-cyan-400" />
              <span>Download Form 16-C Award Certificate</span>
            </button>
          </div>
        </GlassCard>
      </div>

      {/* Acquisition Lifecycle Milestone Tracker */}
      <GlassCard className="p-6">
        <h2 className="text-base font-bold text-white flex items-center gap-2 mb-6">
          <Clock className="w-5 h-5 text-cyan-400" />
          <span>Statutory Acquisition Milestones</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {steps.map((s, idx) => {
            const isCompleted = s.status === 'Completed';
            const isInProgress = s.status === 'In Progress';

            return (
              <div
                key={s.name}
                className={`p-4 rounded-xl border transition-all ${
                  isCompleted
                    ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
                    : isInProgress
                    ? 'bg-cyan-950/30 border-cyan-500/40 text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.2)]'
                    : 'bg-slate-900/40 border-slate-800 text-slate-500'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold">STAGE 0{idx + 1}</span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isInProgress ? (
                    <Clock className="w-4 h-4 text-cyan-400 animate-spin" />
                  ) : (
                    <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                  )}
                </div>
                <h3 className="font-semibold text-xs text-white mb-1 leading-snug">{s.name}</h3>
                <span className="text-[10px] font-mono text-slate-400 block">{s.date}</span>
              </div>
            );
          })}
        </div>
      </GlassCard>

      {/* Aadhaar eSign OTP Modal */}
      {showSignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <GlassCard glow className="max-w-md w-full p-6 border-cyan-500/40">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-800 pb-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Fingerprint className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  CDAC / NSDL Aadhaar eSign Service
                </h3>
                <p className="text-[11px] text-slate-400">
                  Legal acceptance under IT Act 2000
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs mb-6">
              <p className="text-slate-300">
                By eSigning, you record your formal consent for Survey No.{' '}
                <span className="font-mono text-cyan-400 font-bold">{citizenParcel.surveyNumber}</span>{' '}
                and approve the direct payment of{' '}
                <span className="font-tech text-sm font-bold text-emerald-400">
                  ₹{(citizenParcel.compensation?.totalCompensation || citizenParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </span>{' '}
                to your registered SBI bank account.
              </p>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Enter Aadhaar OTP (Sent to registered mobile)
                </label>
                <input
                  type="text"
                  value={aadhaarOtp}
                  onChange={(e) => setAadhaarOtp(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono text-center tracking-widest text-base focus:border-cyan-400 focus:outline-none"
                />
                <span className="text-[10px] text-slate-400 mt-1 block text-center">
                  Mock OTP: 781923
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowSignModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteESign}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white text-xs font-bold shadow-[0_0_15px_rgba(34,211,238,0.4)] flex items-center gap-1.5"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Verify & Sign Consent</span>
              </button>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
