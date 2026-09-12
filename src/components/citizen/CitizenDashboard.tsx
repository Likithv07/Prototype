import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../common/StatusBadge';
import { CitizenAiChatbot } from './CitizenAiChatbot';
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
  MessageSquarePlus,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  ArrowRight,
  Sparkles,
  Bot,
  Building,
  HelpCircle,
  Landmark,
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

  const [showSignModal, setShowSignModal] = useState(false);
  const [showAiChatbot, setShowAiChatbot] = useState(false);
  const [aadhaarOtp, setAadhaarOtp] = useState('781923');

  const handleExecuteESign = () => {
    submitConsent(citizenParcel.id);
    setShowSignModal(false);
    showToast('Aadhaar eSign Consent verified and recorded on Blockchain', 'success');
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
    <div className="space-y-6 pb-20 relative">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-700" />
            <span className="text-xs uppercase font-mono text-blue-900 font-bold tracking-wider">
              Citizen Direct Benefits & Land Transparency Window
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            My Land Acquisition & Compensation
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Official records for <strong className="text-slate-900 font-semibold">Shri {citizenParcel.landownerName}</strong> • Aadhaar{' '}
            <span className="font-mono text-slate-700">{citizenParcel.landownerAadhaar}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* AI Chatbot Trigger Button */}
          <button
            onClick={() => setShowAiChatbot(true)}
            id="citizen-ask-ai-btn"
            className="px-3.5 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold flex items-center gap-2 shadow-2xs transition-colors"
          >
            <Bot className="w-4 h-4 text-blue-200" />
            <span>Ask BhoomiMitra AI</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          </button>

          <button
            onClick={() => setCurrentView('grievance')}
            className="px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-semibold flex items-center gap-1.5 shadow-2xs transition-colors"
          >
            <MessageSquarePlus className="w-3.5 h-3.5 text-slate-500" />
            <span>Raise a Grievance</span>
          </button>
        </div>
      </div>

      {/* Main Land Card & Live Compensation Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Land Particulars */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <span className="text-[10px] font-mono text-blue-800 uppercase font-bold">
                Gazetted Revenue Record
              </span>
              <h2 className="text-lg font-bold text-slate-900">
                Survey No: {citizenParcel.surveyNumber}
              </h2>
            </div>
            <StatusBadge status={citizenParcel.status} />
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Acquired Extent</span>
              <span className="font-mono text-base font-bold text-slate-900">
                {citizenParcel.areaAcres} Acres
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Land Classification</span>
              <span className="font-semibold text-slate-900">
                {citizenParcel.landType}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Revenue Mandal</span>
              <span className="font-semibold text-slate-900">
                {citizenParcel.village}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Basic Unit Rate</span>
              <span className="font-mono font-semibold text-slate-800">
                ₹{(citizenParcel.compensation?.governmentRatePerAcre || citizenParcel.marketValuePerAcre || 2400000).toLocaleString('en-IN')}/Ac
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Multiplier Factor</span>
              <span className="font-mono text-emerald-700 font-bold">
                {citizenParcel.multiplierFactor || 1.5}x (Rural)
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block mb-1">Solatium Guarantee</span>
              <span className="font-mono text-indigo-700 font-bold">
                100% Statutory
              </span>
            </div>
          </div>

          {/* eSign Consent Box */}
          <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Fingerprint className="w-5 h-5 text-blue-700" />
                <h3 className="text-sm font-bold text-slate-900">Digital Consent eSign</h3>
              </div>
              {citizenParcel.consentReceived ? (
                <span className="text-[10px] font-mono text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300 font-bold">
                  eSIGN COMPLETED
                </span>
              ) : (
                <span className="text-[10px] font-mono text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300 font-bold">
                  ACTION REQUIRED
                </span>
              )}
            </div>

            {citizenParcel.consentReceived ? (
              <p className="text-xs text-emerald-900">
                Consent form digitally eSigned on {citizenParcel.consentDate} via Aadhaar eSign
                OTP verification. Award is queued for final PFMS treasury transfer.
              </p>
            ) : (
              <div>
                <p className="text-xs text-slate-700 mb-3 leading-relaxed">
                  Under the RFCTLARR Act 2013, confirm your acceptance of the joint survey and statutory award
                  valuation through Aadhaar eSign to initiate treasury release.
                </p>
                <button
                  onClick={() => setShowSignModal(true)}
                  className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-2xs flex items-center gap-2 transition-colors"
                >
                  <Fingerprint className="w-4 h-4" />
                  <span>Execute Aadhaar eSign Consent Now</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Compensation & Bank Payment Particulars */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-emerald-600" />
                <h2 className="text-base font-bold text-slate-900">
                  Compensation Award Summary
                </h2>
              </div>
              <StatusBadge status={citizenParcel.compensationStatus} />
            </div>

            <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 mb-4">
              <span className="text-emerald-900 text-xs block font-semibold mb-0.5">
                Total Statutory Award Sanctioned:
              </span>
              <span className="font-mono text-3xl font-extrabold text-emerald-700 tracking-tight">
                ₹{(citizenParcel.compensation?.totalCompensation || citizenParcel.totalCompensation || 0).toLocaleString('en-IN')}
              </span>
              <p className="text-[11px] text-emerald-800 mt-1">
                Inclusive of 100% Solatium (₹33.75L) & Asset Valuation (₹4.75L)
              </p>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between text-slate-600 border-b border-slate-100 pb-1.5">
                <span>Beneficiary Account:</span>
                <span className="font-mono text-slate-900 font-semibold">
                  State Bank of India (•••4892)
                </span>
              </div>
              <div className="flex justify-between text-slate-600 border-b border-slate-100 pb-1.5">
                <span>IFSC Code:</span>
                <span className="font-mono text-slate-800 font-medium">SBIN0004128</span>
              </div>
              <div className="flex justify-between text-slate-600 border-b border-slate-100 pb-1.5">
                <span>PFMS Mandate ID:</span>
                <span className="font-mono text-blue-900 font-bold">PFMS-GOI-2026-88194</span>
              </div>
              <div className="flex justify-between text-slate-600 border-b border-slate-100 pb-1.5">
                <span>Disbursal Route:</span>
                <span className="text-emerald-700 font-semibold">
                  Direct Benefit Transfer (DBT)
                </span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-3 border-t border-slate-100">
            <button
              onClick={() => showToast('Downloaded Form 16-C Award Certificate PDF', 'success')}
              className="w-full py-2.5 px-4 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center justify-center gap-2 border border-slate-200 transition-colors shadow-2xs"
            >
              <Download className="w-4 h-4 text-blue-700" />
              <span>Download Form 16-C Award Certificate</span>
            </button>
          </div>
        </div>
      </div>

      {/* Acquisition Lifecycle Milestone Tracker */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2 mb-6">
          <Clock className="w-5 h-5 text-blue-700" />
          <span>Statutory Acquisition Milestones (RFCTLARR 2013)</span>
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
                    ? 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                    : isInProgress
                    ? 'bg-blue-50/80 border-blue-300 text-blue-950 shadow-2xs'
                    : 'bg-slate-50 border-slate-200 text-slate-500'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-slate-500">
                    STAGE 0{idx + 1}
                  </span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : isInProgress ? (
                    <Clock className="w-4 h-4 text-blue-700 animate-spin" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-slate-300" />
                  )}
                </div>
                <h3 className="font-semibold text-xs text-slate-900 mb-1 leading-snug">{s.name}</h3>
                <span className="text-[10px] font-mono text-slate-500 block">{s.date}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Floating AI Assistant Trigger Pill */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setShowAiChatbot(true)}
          className="px-4 py-3 rounded-full bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white shadow-xl hover:shadow-2xl flex items-center gap-2.5 transition-transform hover:scale-105 group border border-white/20"
        >
          <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div className="text-left">
            <span className="text-xs font-bold block leading-tight">BhoomiMitra AI</span>
            <span className="text-[10px] text-blue-200 block leading-tight">Citizen Help Sahayak</span>
          </div>
          <Sparkles className="w-4 h-4 text-yellow-300 ml-1 animate-pulse" />
        </button>
      </div>

      {/* Aadhaar eSign OTP Modal */}
      {showSignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/50 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="max-w-md w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xl">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-100 pb-3">
              <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
                <Fingerprint className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  CDAC / NSDL Aadhaar eSign Service
                </h3>
                <p className="text-[11px] text-slate-500">
                  Legal digital acceptance under IT Act 2000
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs mb-6">
              <p className="text-slate-600 leading-relaxed">
                By eSigning, you record your formal consent for Survey No.{' '}
                <span className="font-mono text-blue-900 font-bold">{citizenParcel.surveyNumber}</span>{' '}
                and approve the direct payment of{' '}
                <span className="font-mono text-sm font-bold text-emerald-700">
                  ₹{(citizenParcel.compensation?.totalCompensation || citizenParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </span>{' '}
                to your registered SBI bank account.
              </p>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Enter Aadhaar OTP (Sent to registered mobile)
                </label>
                <input
                  type="text"
                  value={aadhaarOtp}
                  onChange={(e) => setAadhaarOtp(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 font-mono text-center tracking-widest text-base focus:border-blue-700 focus:bg-white focus:outline-none"
                />
                <span className="text-[10px] text-slate-500 mt-1 block text-center">
                  Mock OTP: 781923
                </span>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowSignModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteESign}
                className="px-5 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-bold shadow-2xs flex items-center gap-1.5 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Verify & Sign Consent</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Citizen AI Chatbot Popup Modal */}
      <CitizenAiChatbot
        isOpen={showAiChatbot}
        onClose={() => setShowAiChatbot(false)}
      />
    </div>
  );
};
