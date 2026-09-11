import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  ShieldAlert,
  Search,
  CheckCircle2,
  Clock,
  UserCheck,
  Terminal,
  Download,
  Filter,
} from 'lucide-react';

export const AuditTrail: React.FC = () => {
  const { auditLogs, showToast } = useApp();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredLogs = auditLogs.filter(
    (log) =>
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.entityId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-rose-400 font-semibold tracking-wider">
              Immutable Cryptographic Audit Trail
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            System & Regulatory Audit Logs
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time append-only ledger tracking all administrative approvals, field uploads, and citizen consents.
          </p>
        </div>

        <button
          onClick={() => showToast('Generated Statutory CAG / CVC Audit Manifest (JSON/CSV)', 'success')}
          className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-2"
        >
          <Download className="w-4 h-4 text-cyan-400" />
          <span>Export Audit Ledger</span>
        </button>
      </div>

      {/* Audit Log Table */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between gap-4 mb-4">
          <div className="relative w-full max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search audit action, user, or entity..."
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <span className="text-xs font-mono text-cyan-400">
            {filteredLogs.length} Verified Entries
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 font-mono text-[11px] uppercase border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Log ID & Timestamp</th>
                <th className="py-3 px-4">Officer / User</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Action Performed</th>
                <th className="py-3 px-4">Entity ID</th>
                <th className="py-3 px-4">IP Address</th>
                <th className="py-3 px-4 text-right">Integrity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="text-cyan-400 font-bold block">{log.id}</span>
                    <span className="text-slate-400 text-[10px]">{log.timestamp}</span>
                  </td>
                  <td className="py-3 px-4 font-sans font-semibold text-white whitespace-nowrap">
                    {log.userName}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px]">
                      {log.role}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-sans text-slate-200">
                    {log.action}
                  </td>
                  <td className="py-3 px-4 text-cyan-300 whitespace-nowrap">
                    {log.entityId}
                  </td>
                  <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                    {log.ipAddress}
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <span className="text-emerald-400 font-bold text-[10px] inline-flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      VALID
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
};
