import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Calculator,
  ShieldCheck,
  RotateCcw,
  CheckCircle2,
  XCircle,
  FileText,
  AlertTriangle,
  UserCheck,
  Download,
  Fingerprint,
  Building,
  KeyRound,
  Eye,
  Sparkles,
} from 'lucide-react';
import { CompensationCalculation } from '../../types';

export const CompensationApproval: React.FC = () => {
  const {
    landParcels,
    selectedParcelId,
    setSelectedParcelId,
    calculateCompensation,
    approveCompensation,
    rejectCompensation,
    showToast,
  } = useApp();

  const selectedParcel =
    landParcels.find((p) => p.id === selectedParcelId) || landParcels[0];

  // Calculator inputs state initialized with selected parcel or default
  const [landArea, setLandArea] = useState<number>(selectedParcel.areaAcres);
  const [marketValuePerUnit, setMarketValuePerUnit] = useState<number>(
    selectedParcel.marketValuePerAcre
  );
  const [multiplierFactor, setMultiplierFactor] = useState<number>(
    selectedParcel.multiplierFactor
  );
  const [assetValuation, setAssetValuation] = useState<number>(
    selectedParcel.assetValuation
  );
  const [solatiumPct, setSolatiumPct] = useState<number>(100);
  const [interestPct, setInterestPct] = useState<number>(12);

  // Modals state
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [digitalSignConsent, setDigitalSignConsent] = useState(true);

  // Live calculation logic compliant with RFCTLARR Act 2013
  const basicLandValue = landArea * marketValuePerUnit;
  const multipliedLandValue = basicLandValue * multiplierFactor;
  const basePlusAssets = multipliedLandValue + assetValuation;
  const solatiumAmount = (basePlusAssets * solatiumPct) / 100;
  const interestAmount = (multipliedLandValue * interestPct) / 100;
  const totalCalculated = basePlusAssets + solatiumAmount + interestAmount;

  const handleApplyCalculationToParcel = () => {
    const calc: CompensationCalculation = {
      basicLandValue,
      multiplierFactor,
      multipliedLandValue,
      assetValuation,
      solatiumPercentage: solatiumPct,
      solatiumAmount,
      interestPercentage: interestPct,
      interestAmount,
      totalCompensation: totalCalculated,
    };
    calculateCompensation(selectedParcel.id, calc);
    showToast(`Award calculation updated for ${selectedParcel.id}`, 'success');
  };

  const handleConfirmApproval = () => {
    if (!digitalSignConsent) {
      showToast('Please confirm your digital DSC consent to sign the award', 'warning');
      return;
    }
    approveCompensation(selectedParcel.id, 'P. Srinivas Rao, IAS (Spl. Collector)');
    setShowApprovalModal(false);
  };

  const handleConfirmRevision = () => {
    if (!revisionNotes.trim()) {
      showToast('Please provide revision remarks for the valuation committee', 'warning');
      return;
    }
    rejectCompensation(selectedParcel.id, revisionNotes);
    setShowRevisionModal(false);
    setRevisionNotes('');
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
              RFCTLARR Statutory Valuation & Award Section
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Compensation Calculator & Digital Award Approval
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Formulation of statutory compensation pursuant to Section 26-30 of the RFCTLARR Act, 2013.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Active Parcel:</span>
          <select
            value={selectedParcel.id}
            onChange={(e) => {
              setSelectedParcelId(e.target.value);
              const p = landParcels.find((lp) => lp.id === e.target.value);
              if (p) {
                setLandArea(p.areaAcres);
                setMarketValuePerUnit(p.marketValuePerAcre);
                setMultiplierFactor(p.multiplierFactor);
                setAssetValuation(p.assetValuation);
              }
            }}
            className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700 text-cyan-300 text-xs font-mono font-semibold focus:outline-none focus:border-cyan-400"
          >
            {landParcels.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} ({p.landownerName})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main 2-Column: Calculator on Left, Review & Approval on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Calculator Inputs & Live Breakdown */}
        <GlassCard className="lg:col-span-7 p-6 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-bold text-white">
                Statutory Compensation Calculator
              </h2>
            </div>
            <button
              onClick={() => {
                setLandArea(selectedParcel.areaAcres);
                setMarketValuePerUnit(selectedParcel.marketValuePerAcre);
                setMultiplierFactor(selectedParcel.multiplierFactor);
                setAssetValuation(selectedParcel.assetValuation);
                setSolatiumPct(100);
                setInterestPct(12);
                showToast('Reset to statutory base values', 'info');
              }}
              className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>

          {/* Input Fields Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Land Area (Acres)
              </label>
              <input
                type="number"
                step="0.05"
                value={landArea}
                onChange={(e) => setLandArea(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Market Value per Unit (₹/Acre)
              </label>
              <input
                type="number"
                step="50000"
                value={marketValuePerUnit}
                onChange={(e) => setMarketValuePerUnit(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Multiplier Factor (Rural 1.5 - 2.0, Urban 1.0)
              </label>
              <select
                value={multiplierFactor}
                onChange={(e) => setMultiplierFactor(parseFloat(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:border-cyan-400 focus:outline-none"
              >
                <option value={1.0}>1.00 - Urban Municipal Zone</option>
                <option value={1.25}>1.25 - Semi-Urban Peri-metropolitan</option>
                <option value={1.5}>1.50 - Rural Zone (10-25 km radius)</option>
                <option value={2.0}>2.00 - Rural Zone (&gt;25 km radius)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Asset Valuation (Structures, Trees, Crops ₹)
              </label>
              <input
                type="number"
                step="25000"
                value={assetValuation}
                onChange={(e) => setAssetValuation(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Solatium Percentage (Section 30(1))
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={solatiumPct}
                  onChange={(e) => setSolatiumPct(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">
                  % (Statutory 100%)
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Additional Interest Percentage (12% per annum)
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={interestPct}
                  onChange={(e) => setInterestPct(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">
                  % (Section 30(3))
                </span>
              </div>
            </div>
          </div>

          {/* Output Calculated Compensation Breakdown */}
          <div className="p-4 rounded-xl bg-[#0B1E36] border border-cyan-500/30 space-y-2.5">
            <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
              <span className="font-semibold text-cyan-400 uppercase tracking-wider font-mono">
                Calculated Award Breakdown
              </span>
              <span className="text-slate-400">Section 26 - 30 RFCTLARR 2013</span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Basic Land Value (Area × Market Value):</span>
              <span className="font-mono text-slate-200">
                ₹{basicLandValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-300">
                Multiplied Land Value (Factor × {multiplierFactor}):
              </span>
              <span className="font-mono text-cyan-300 font-semibold">
                ₹{multipliedLandValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Valuation of Assets Attached to Land:</span>
              <span className="font-mono text-slate-200">
                ₹{assetValuation.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Solatium (100% on Market Value + Assets):</span>
              <span className="font-mono text-emerald-400 font-semibold">
                ₹{solatiumAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-300">Additional Interest (12% per annum):</span>
              <span className="font-mono text-purple-400 font-semibold">
                ₹{interestAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="pt-2 border-t border-slate-800 flex justify-between items-baseline">
              <span className="text-sm font-bold text-white">Total Compensation Payable:</span>
              <span className="text-xl font-bold font-tech text-cyan-300 tracking-tight">
                ₹{totalCalculated.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          <button
            onClick={handleApplyCalculationToParcel}
            className="w-full py-2.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(34,211,238,0.2)]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Apply Formulation to Selected Parcel Record</span>
          </button>
        </GlassCard>

        {/* Right Column: Statutory Review & Approval Actions */}
        <GlassCard glow className="lg:col-span-5 p-6 flex flex-col justify-between border-cyan-500/30">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h2 className="text-base font-bold text-white">
                  Officer Statutory Review
                </h2>
              </div>
              <StatusBadge status={selectedParcel.compensationStatus} />
            </div>

            <div className="space-y-3.5 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
                <span className="text-slate-400 block mb-0.5">Landowner Legal Entity</span>
                <span className="text-white font-bold text-sm">{selectedParcel.landownerName}</span>
                <span className="text-[11px] text-slate-400 block mt-0.5">
                  Aadhaar: {selectedParcel.landownerAadhaar}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Survey Number</span>
                  <span className="text-white font-mono font-bold">{selectedParcel.surveyNumber}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800">
                  <span className="text-slate-400 block mb-0.5">Village / Mandal</span>
                  <span className="text-white font-bold">{selectedParcel.village}</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
                <span className="text-emerald-300 block text-[11px]">Final Award Assessment</span>
                <span className="font-tech text-2xl font-bold text-emerald-400">
                  ₹{(selectedParcel.compensation?.totalCompensation || selectedParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </span>
              </div>

              {/* Supporting Documents Checklist */}
              <div className="pt-2 border-t border-slate-800">
                <span className="text-slate-400 font-semibold block mb-2">
                  Verified Statutory Enclosures:
                </span>
                <div className="space-y-1.5">
                  {[
                    'Form 16-B Field Valuation Report (Certified)',
                    'Title Deed Extract (Pahani / ROR-1B)',
                    'Joint Inspection Committee Signature Register',
                    'Geo-tagged Boundary Cadastral Polygon',
                  ].map((doc, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span>{doc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 pt-4 border-t border-slate-800 space-y-2.5">
            {selectedParcel.compensationStatus === 'Approved' ? (
              <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
                <p className="text-xs font-bold text-white">Compensation Award Digitally Sealed</p>
                <p className="text-[11px] text-emerald-300 mt-0.5">
                  Approved by {selectedParcel.approvedBy} on {selectedParcel.approvalDate}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  onClick={() => setShowApprovalModal(true)}
                  className="py-2.5 px-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:brightness-110 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Award</span>
                </button>

                <button
                  onClick={() => setShowRevisionModal(true)}
                  className="py-2.5 px-3 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 font-semibold text-xs flex items-center justify-center gap-1"
                >
                  <AlertTriangle className="w-4 h-4" />
                  <span>Request Rev.</span>
                </button>

                <button
                  onClick={() => {
                    rejectCompensation(selectedParcel.id, 'Title discrepancy found in survey records');
                  }}
                  className="py-2.5 px-3 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 font-semibold text-xs flex items-center justify-center gap-1"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject</span>
                </button>
              </div>
            )}
          </div>
        </GlassCard>
      </div>

      {/* Compensation Summary Table (Prompt requirement) */}
      <GlassCard className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Compensation Register Summary</span>
            </h2>
            <p className="text-xs text-slate-400">
              Complete gazetted awards across survey parcels under Section 31
            </p>
          </div>
          <button
            onClick={() => showToast('Generated Section 31 Statutory Compensation Register PDF', 'success')}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Award Gazettes</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Parcel ID</th>
                <th className="py-3 px-4">Landowner Name</th>
                <th className="py-3 px-4">Survey No.</th>
                <th className="py-3 px-4">Area</th>
                <th className="py-3 px-4">Calculated Amount</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Approved By</th>
                <th className="py-3 px-4">Approval Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {landParcels.map((parcel) => (
                <tr
                  key={parcel.id}
                  onClick={() => setSelectedParcelId(parcel.id)}
                  className={`hover:bg-cyan-500/5 transition-colors cursor-pointer ${
                    selectedParcel.id === parcel.id ? 'bg-cyan-500/10' : ''
                  }`}
                >
                  <td className="py-3 px-4 font-mono font-bold text-cyan-400">
                    {parcel.id}
                  </td>
                  <td className="py-3 px-4 font-semibold text-white">
                    {parcel.landownerName}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {parcel.surveyNumber}
                  </td>
                  <td className="py-3 px-4 font-tech text-sm text-slate-200">
                    {parcel.areaAcres} Acres
                  </td>
                  <td className="py-3 px-4 font-tech text-sm font-bold text-emerald-400">
                    ₹{(parcel.compensation?.totalCompensation || parcel.totalCompensation || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={parcel.compensationStatus} />
                  </td>
                  <td className="py-3 px-4 text-slate-300">
                    {parcel.compensation?.approvedBy || parcel.approvedBy || '—'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {parcel.compensation?.approvalDate || parcel.approvalDate || 'Pending'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Digital DSC Signature Confirmation Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <GlassCard glow className="max-w-md w-full p-6 border-emerald-500/40">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-800 pb-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                <Fingerprint className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  NIC Class-3 Digital Signature Seal
                </h3>
                <p className="text-[11px] text-slate-400">
                  Statutory gazette award sign-off
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs mb-6">
              <p className="text-slate-300 leading-relaxed">
                You are about to issue a legally binding Land Acquisition Award under Section 31 of
                RFCTLARR Act 2013 for:
              </p>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                <p className="text-white font-semibold">{selectedParcel.landownerName}</p>
                <p className="font-mono text-cyan-300">Parcel: {selectedParcel.id}</p>
                <p className="font-tech text-lg font-bold text-emerald-400">
                  ₹{(selectedParcel.compensation?.totalCompensation || selectedParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </p>
              </div>

              <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-900/60 border border-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={digitalSignConsent}
                  onChange={(e) => setDigitalSignConsent(e.target.checked)}
                  className="mt-0.5 rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-400"
                />
                <span className="text-[11px] text-slate-300">
                  I certify that the joint measurement survey, Solatium (100%), and title verification
                  comply with the Central & State acquisition rules.
                </span>
              </label>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowApprovalModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmApproval}
                className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-[0_0_15px_rgba(16,185,129,0.4)] flex items-center gap-1.5"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Affix Digital DSC & Approve</span>
              </button>
            </div>
          </GlassCard>
        </div>
      )}

      {/* Revision Remarks Modal */}
      {showRevisionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <GlassCard glow className="max-w-md w-full p-6 border-amber-500/40">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-800 pb-3">
              <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  Request Valuation Revision
                </h3>
                <p className="text-[11px] text-slate-400">
                  Return award dossier to District Revenue Committee
                </p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <label className="block text-xs font-medium text-slate-300">
                Revision Remarks / Objections:
              </label>
              <textarea
                value={revisionNotes}
                onChange={(e) => setRevisionNotes(e.target.value)}
                rows={4}
                placeholder="e.g. Tree count discrepancies observed between drone LiDAR and Form 16-B; reassess horticultural valuation..."
                className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs placeholder-slate-500 focus:outline-none focus:border-amber-400"
              />
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowRevisionModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmRevision}
                className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-slate-950 text-xs font-bold shadow-[0_0_15px_rgba(245,158,11,0.4)]"
              >
                Submit Revision Request
              </button>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
};
