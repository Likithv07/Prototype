import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../common/StatusBadge';
import {
  Calculator,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RotateCcw,
  Download,
  FileText,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  Fingerprint,
} from 'lucide-react';

export const CompensationApproval: React.FC = () => {
  const {
    landParcels,
    selectedParcelId,
    setSelectedParcelId,
    updateCompensation,
    approveCompensation,
    rejectCompensation,
    showToast,
  } = useApp();

  const selectedParcel =
    landParcels.find((p) => p.id === selectedParcelId) || landParcels[0];

  // Local state for interactive calculation inputs
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

  // Modals for approval and revision
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionNotes, setRevisionNotes] = useState('');
  const [digitalSignConsent, setDigitalSignConsent] = useState(false);

  // Dynamic formula calculation according to Section 26-30 of RFCTLARR Act 2013
  const basicLandValue = landArea * marketValuePerUnit;
  const multipliedLandValue = basicLandValue * multiplierFactor;
  const marketValuePlusAssets = multipliedLandValue + assetValuation;
  const solatiumAmount = marketValuePlusAssets * (solatiumPct / 100);
  const interestAmount = multipliedLandValue * (interestPct / 100);
  const totalCalculated = marketValuePlusAssets + solatiumAmount + interestAmount;

  const handleApplyCalculationToParcel = () => {
    updateCompensation(selectedParcel.id, {
      baseRatePerAcre: marketValuePerUnit,
      governmentRatePerAcre: marketValuePerUnit * 0.9,
      marketRatePerAcre: marketValuePerUnit,
      areaAcres: landArea,
      baseAmount: multipliedLandValue,
      solatiumAmount,
      interestAmount,
      additionalAssetsAmount: assetValuation,
      totalCompensation: totalCalculated,
      status: 'Pending',
    });
    showToast('Updated statutory compensation formulation in registry', 'success');
  };

  const handleConfirmApproval = () => {
    if (!digitalSignConsent) {
      showToast('Please check the digital signature compliance box', 'warning');
      return;
    }
    approveCompensation(selectedParcel.id, 'NIC-DSC-GOV-2026-9812');
    setShowApprovalModal(false);
    setDigitalSignConsent(false);
  };

  const handleConfirmRevision = () => {
    if (!revisionNotes.trim()) {
      showToast('Please state statutory reasons for revision request', 'warning');
      return;
    }
    rejectCompensation(selectedParcel.id, revisionNotes);
    setShowRevisionModal(false);
    setRevisionNotes('');
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-700" />
            <span className="text-xs uppercase font-mono text-blue-900 font-bold tracking-wider">
              RFCTLARR Statutory Valuation & Award Section
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Compensation Calculator & Digital Award Approval
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Formulation of statutory compensation pursuant to Section 26-30 of the RFCTLARR Act, 2013.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Active Parcel:</span>
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
            className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-xs font-mono font-semibold focus:outline-none focus:border-blue-700"
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
        <div className="lg:col-span-7 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Calculator className="w-5 h-5 text-blue-700" />
              <h2 className="text-base font-bold text-slate-900">
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
              className="text-xs text-slate-500 hover:text-blue-700 flex items-center gap-1 font-medium transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>

          {/* Input Fields Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Land Area (Acres)
              </label>
              <input
                type="number"
                step="0.05"
                value={landArea}
                onChange={(e) => setLandArea(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Market Value per Unit (₹/Acre)
              </label>
              <input
                type="number"
                step="50000"
                value={marketValuePerUnit}
                onChange={(e) => setMarketValuePerUnit(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Multiplier Factor (Rural 1.5 - 2.0, Urban 1.0)
              </label>
              <select
                value={multiplierFactor}
                onChange={(e) => setMultiplierFactor(parseFloat(e.target.value))}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 font-medium focus:border-blue-700 focus:bg-white focus:outline-none"
              >
                <option value={1.0}>1.00 - Urban Municipal Zone</option>
                <option value={1.25}>1.25 - Semi-Urban Peri-metropolitan</option>
                <option value={1.5}>1.50 - Rural Zone (10-25 km radius)</option>
                <option value={2.0}>2.00 - Rural Zone (&gt;25 km radius)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Asset Valuation (Structures, Trees, Crops ₹)
              </label>
              <input
                type="number"
                step="25000"
                value={assetValuation}
                onChange={(e) => setAssetValuation(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Solatium Percentage (Section 30(1))
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={solatiumPct}
                  onChange={(e) => setSolatiumPct(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs font-medium">
                  % (Statutory 100%)
                </span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Additional Interest Percentage (12% p.a.)
              </label>
              <div className="relative">
                <input
                  type="number"
                  value={interestPct}
                  onChange={(e) => setInterestPct(parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-xs font-medium">
                  % (Section 30(3))
                </span>
              </div>
            </div>
          </div>

          {/* Output Calculated Compensation Breakdown */}
          <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 space-y-2.5">
            <div className="flex items-center justify-between text-xs border-b border-blue-200/80 pb-2">
              <span className="font-bold text-blue-950 uppercase tracking-wider font-mono">
                Calculated Award Breakdown
              </span>
              <span className="text-blue-800 font-medium text-[11px]">Section 26 - 30 RFCTLARR 2013</span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Basic Land Value (Area × Market Value):</span>
              <span className="font-mono text-slate-900 font-medium">
                ₹{basicLandValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-600">
                Multiplied Land Value (Factor × {multiplierFactor}):
              </span>
              <span className="font-mono text-blue-900 font-bold">
                ₹{multipliedLandValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Valuation of Assets Attached to Land:</span>
              <span className="font-mono text-slate-900 font-medium">
                ₹{assetValuation.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Solatium (100% on Market Value + Assets):</span>
              <span className="font-mono text-emerald-700 font-bold">
                ₹{solatiumAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="flex justify-between text-xs">
              <span className="text-slate-600">Additional Interest (12% per annum):</span>
              <span className="font-mono text-indigo-700 font-bold">
                ₹{interestAmount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>

            <div className="pt-2 border-t border-blue-200 flex justify-between items-baseline">
              <span className="text-sm font-bold text-slate-900">Total Compensation Payable:</span>
              <span className="text-xl font-bold font-mono text-emerald-700 tracking-tight">
                ₹{totalCalculated.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          <button
            onClick={handleApplyCalculationToParcel}
            className="w-full py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-2xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Apply Formulation to Selected Parcel Record</span>
          </button>
        </div>

        {/* Right Column: Statutory Review & Approval Actions */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <h2 className="text-base font-bold text-slate-900">
                  Officer Statutory Review
                </h2>
              </div>
              <StatusBadge status={selectedParcel.compensationStatus} />
            </div>

            <div className="space-y-3.5 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                <span className="text-slate-500 block mb-0.5">Landowner Legal Entity</span>
                <span className="text-slate-900 font-bold text-sm">{selectedParcel.landownerName}</span>
                <span className="text-[11px] text-slate-500 block mt-0.5">
                  Aadhaar: <span className="font-mono">{selectedParcel.landownerAadhaar}</span>
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Survey Number</span>
                  <span className="text-slate-900 font-mono font-bold">{selectedParcel.surveyNumber}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-slate-500 block mb-0.5">Village / Mandal</span>
                  <span className="text-slate-900 font-semibold">{selectedParcel.village}</span>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200">
                <span className="text-emerald-900 font-semibold block text-[11px]">Final Award Assessment</span>
                <span className="font-mono text-2xl font-bold text-emerald-700">
                  ₹{(selectedParcel.compensation?.totalCompensation || selectedParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </span>
              </div>

              {/* Supporting Documents Checklist */}
              <div className="pt-2 border-t border-slate-100">
                <span className="text-slate-700 font-semibold block mb-2">
                  Verified Statutory Enclosures:
                </span>
                <div className="space-y-1.5">
                  {[
                    'Form 16-B Field Valuation Report (Certified)',
                    'Title Deed Extract (Pahani / ROR-1B)',
                    'Joint Inspection Committee Signature Register',
                    'Geo-tagged Boundary Cadastral Polygon',
                  ].map((doc, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-600">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{doc}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 pt-4 border-t border-slate-100 space-y-2.5">
            {selectedParcel.compensationStatus === 'Approved' ? (
              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto mb-1" />
                <p className="text-xs font-bold text-slate-900">Compensation Award Digitally Sealed</p>
                <p className="text-[11px] text-emerald-800 mt-0.5">
                  Approved by {selectedParcel.approvedBy} on {selectedParcel.approvalDate}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  onClick={() => setShowApprovalModal(true)}
                  className="py-2.5 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-2xs transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Approve Award</span>
                </button>

                <button
                  onClick={() => setShowRevisionModal(true)}
                  className="py-2.5 px-3 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-300 font-semibold text-xs flex items-center justify-center gap-1 transition-colors"
                >
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Request Rev.</span>
                </button>

                <button
                  onClick={() => {
                    rejectCompensation(selectedParcel.id, 'Title discrepancy found in survey records');
                  }}
                  className="py-2.5 px-3 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-300 font-semibold text-xs flex items-center justify-center gap-1 transition-colors"
                >
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>Reject</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Compensation Summary Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-700" />
              <span>Compensation Register Summary</span>
            </h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Complete gazetted awards across survey parcels under Section 31
            </p>
          </div>
          <button
            onClick={() => showToast('Generated Section 31 Statutory Compensation Register PDF', 'success')}
            className="px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center gap-1.5 border border-slate-200 transition-colors shadow-2xs"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" />
            <span>Export Award Gazettes</span>
          </button>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-xl">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50 text-slate-700 font-mono text-[11px] uppercase border-b border-slate-200">
              <tr>
                <th className="py-3 px-4 font-semibold">Parcel ID</th>
                <th className="py-3 px-4 font-semibold">Landowner Name</th>
                <th className="py-3 px-4 font-semibold">Survey No.</th>
                <th className="py-3 px-4 font-semibold">Area</th>
                <th className="py-3 px-4 font-semibold">Calculated Amount</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Approved By</th>
                <th className="py-3 px-4 font-semibold">Approval Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {landParcels.map((parcel) => (
                <tr
                  key={parcel.id}
                  onClick={() => setSelectedParcelId(parcel.id)}
                  className={`hover:bg-blue-50/50 transition-colors cursor-pointer ${
                    selectedParcel.id === parcel.id ? 'bg-blue-50/80 font-semibold' : ''
                  }`}
                >
                  <td className="py-3 px-4 font-mono font-bold text-blue-900">
                    {parcel.id}
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-900">
                    {parcel.landownerName}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-600">
                    {parcel.surveyNumber}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-700">
                    {parcel.areaAcres} Acres
                  </td>
                  <td className="py-3 px-4 font-mono text-sm font-bold text-emerald-700">
                    ₹{(parcel.compensation?.totalCompensation || parcel.totalCompensation || 0).toLocaleString('en-IN')}
                  </td>
                  <td className="py-3 px-4">
                    <StatusBadge status={parcel.compensationStatus} />
                  </td>
                  <td className="py-3 px-4 text-slate-600">
                    {parcel.compensation?.approvedBy || parcel.approvedBy || '—'}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-500">
                    {parcel.compensation?.approvalDate || parcel.approvalDate || 'Pending'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Digital DSC Signature Confirmation Modal */}
      {showApprovalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="max-w-md w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xl">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-100 pb-3">
              <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200">
                <Fingerprint className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  NIC Class-3 Digital Signature Seal
                </h3>
                <p className="text-[11px] text-slate-500">
                  Statutory gazette award sign-off
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs mb-6">
              <p className="text-slate-600 leading-relaxed">
                You are about to issue a legally binding Land Acquisition Award under Section 31 of
                RFCTLARR Act 2013 for:
              </p>
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                <p className="text-slate-900 font-bold">{selectedParcel.landownerName}</p>
                <p className="font-mono text-blue-900 text-xs">Parcel: {selectedParcel.id}</p>
                <p className="font-mono text-lg font-bold text-emerald-700">
                  ₹{(selectedParcel.compensation?.totalCompensation || selectedParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </p>
              </div>

              <label className="flex items-start gap-2.5 p-2 rounded-lg bg-slate-50 border border-slate-200 cursor-pointer">
                <input
                  type="checkbox"
                  checked={digitalSignConsent}
                  onChange={(e) => setDigitalSignConsent(e.target.checked)}
                  className="mt-0.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                />
                <span className="text-[11px] text-slate-600 leading-snug">
                  I certify that the joint measurement survey, Solatium (100%), and title verification
                  comply with the Central & State acquisition rules.
                </span>
              </label>
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowApprovalModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmApproval}
                className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-2xs flex items-center gap-1.5 transition-colors"
              >
                <ShieldCheck className="w-4 h-4" />
                <span>Affix Digital DSC & Approve</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Revision Remarks Modal */}
      {showRevisionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="max-w-md w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xl">
            <div className="flex items-center gap-3 mb-4 border-b border-slate-100 pb-3">
              <div className="p-2.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Request Valuation Revision
                </h3>
                <p className="text-[11px] text-slate-500">
                  Return award dossier to District Revenue Committee
                </p>
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <label className="block text-xs font-semibold text-slate-700">
                Revision Remarks / Objections:
              </label>
              <textarea
                value={revisionNotes}
                onChange={(e) => setRevisionNotes(e.target.value)}
                rows={4}
                placeholder="e.g. Tree count discrepancies observed between drone LiDAR and Form 16-B; reassess horticultural valuation..."
                className="w-full p-3 rounded-xl bg-slate-50 border border-slate-300 text-slate-900 text-xs placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowRevisionModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmRevision}
                className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-2xs transition-colors"
              >
                Submit Revision Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
