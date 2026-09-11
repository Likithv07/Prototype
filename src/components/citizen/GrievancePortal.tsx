import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  MessageSquarePlus,
  FileText,
  UploadCloud,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Send,
  Search,
  Check,
  Shield,
  FileCheck,
} from 'lucide-react';
import { Grievance, GrievanceCategory } from '../../types';

export const GrievancePortal: React.FC = () => {
  const { grievances, addGrievance, landParcels, showToast } = useApp();

  const [category, setCategory] = useState<GrievanceCategory>('Compensation Issue');
  const [parcelId, setParcelId] = useState(landParcels[0]?.id || 'TS-HYD-2026-001245');
  const [description, setDescription] = useState('');
  const [citizenName, setCitizenName] = useState('Rajesh Kumar Reddy');
  const [phone, setPhone] = useState('+91 98765 43210');
  const [documentAttached, setDocumentAttached] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) {
      showToast('Please provide grievance description details', 'warning');
      return;
    }

    addGrievance({
      parcelId,
      citizenName,
      mobile: phone,
      category,
      subject: `${category} for Parcel ${parcelId}`,
      description,
    });

    setDescription('');
    setDocumentAttached(false);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-amber-400 font-semibold tracking-wider">
              Statutory Grievance Redressal Mechanism (CPGRAMS Integrated)
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Grievance Redressal & Citizen Petitions
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Escalate valuation disputes, survey measurement errors, or resettlement claims directly to the District Collector.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Raise Grievance Form */}
        <GlassCard glow className="lg:col-span-5 p-6 border-amber-500/30">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
            <MessageSquarePlus className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-white">Lodge a Formal Grievance</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Grievance Category
              </label>
              <select
                value={category}
                onChange={(e: any) => setCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:border-amber-400 focus:outline-none"
              >
                <option value="Compensation Issue">Compensation Issue (Valuation / Solatium)</option>
                <option value="Measurement Error">Measurement Error (Area / Survey Boundaries)</option>
                <option value="Delayed Payment">Delayed Payment (PFMS Transfer Latency)</option>
                <option value="Title Dispute">Title Dispute / Heirship Conflict</option>
                <option value="Resettlement & Rehabilitation">Resettlement & Rehabilitation (R&R Housing)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Land Parcel ID
                </label>
                <select
                  value={parcelId}
                  onChange={(e) => setParcelId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white font-mono focus:border-amber-400 focus:outline-none"
                >
                  {landParcels.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id} (Sy {p.surveyNumber})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Contact Mobile
                </label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:border-amber-400 focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Detailed Grounds of Objection
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder="State your factual objection clearly. Specify survey tree counts, structure dimensions, or legal inheritance details..."
                className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-400"
              />
            </div>

            {/* Document Upload Button */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Supporting Documentation
              </label>
              <div
                onClick={() => {
                  setDocumentAttached(true);
                  showToast('Affidavit / Registered Title Deed attached', 'info');
                }}
                className={`p-3 rounded-xl border-2 border-dashed cursor-pointer flex items-center justify-center gap-2 text-xs transition-all ${
                  documentAttached
                    ? 'border-emerald-500/50 bg-emerald-950/30 text-emerald-300'
                    : 'border-slate-700 hover:border-amber-400/50 text-slate-400'
                }`}
              >
                {documentAttached ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Title_Deed_Certified_Extract.pdf attached (2.4 MB)</span>
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-4 h-4 text-slate-400" />
                    <span>Click to attach Revenue Record or Affidavit</span>
                  </>
                )}
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-amber-600 via-orange-600 to-yellow-600 hover:brightness-110 text-slate-950 font-bold text-xs sm:text-sm shadow-[0_0_20px_rgba(245,158,11,0.3)] flex items-center justify-center gap-2 active:scale-95 transition-all"
            >
              <Send className="w-4 h-4" />
              <span>Submit Statutory Grievance Petition</span>
            </button>
          </form>
        </GlassCard>

        {/* Right: Grievance Status Tracker */}
        <GlassCard className="lg:col-span-7 p-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-cyan-400" />
              <span>Grievance Registry & Resolution Status</span>
            </h2>
            <span className="text-xs font-mono text-cyan-300">
              {grievances.length} Registered Petitions
            </span>
          </div>

          <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
            {grievances.map((grv) => (
              <div
                key={grv.id}
                className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-2 text-xs hover:border-cyan-500/40 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-cyan-400">{grv.id}</span>
                    <span className="text-slate-400">•</span>
                    <span className="text-white font-semibold">{grv.category}</span>
                  </div>
                  <StatusBadge status={grv.status} />
                </div>

                <p className="text-slate-300 leading-relaxed">{grv.description}</p>

                {grv.resolutionNotes && (
                  <div className="p-2.5 rounded-lg bg-emerald-950/50 border border-emerald-500/30 text-emerald-300 text-[11px]">
                    <span className="font-bold block text-emerald-200">Official Hearing Finding:</span>
                    {grv.resolutionNotes}
                  </div>
                )}

                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                  <span>Filed by: {grv.citizenName} ({grv.parcelId})</span>
                  <span>Date: {grv.submittedDate}</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
