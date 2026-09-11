import React from 'react';
import { AcquisitionStatus, LifecycleStageStatus, ProjectStatus } from '../../types';

interface StatusBadgeProps {
  status: string;
  type?: 'acquisition' | 'lifecycle' | 'project' | 'general';
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  type = 'general',
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3.5 py-1.5',
  }[size];

  // Specific color logic for Land Parcels according to prompt specs:
  // BLUE: Proposed Land
  // YELLOW: Notification Issued
  // ORANGE: Under Verification
  // PURPLE: Compensation Pending
  // GREEN: Land Acquired
  // RED: Disputed Land
  // DARK GREEN: Possession Completed
  const getBadgeStyle = () => {
    switch (status) {
      case 'Proposed':
      case 'Proposed Land':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40 shadow-[0_0_12px_rgba(59,130,246,0.3)]';
      case 'Notification Issued':
        return 'bg-amber-500/20 text-yellow-300 border-yellow-500/40 shadow-[0_0_12px_rgba(234,179,8,0.3)]';
      case 'Under Verification':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40 shadow-[0_0_12px_rgba(249,115,22,0.3)]';
      case 'Compensation Pending':
      case 'Pending':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/40 shadow-[0_0_12px_rgba(168,85,247,0.3)]';
      case 'Land Acquired':
      case 'Approved':
      case 'Completed':
      case 'Rehabilitated':
      case 'Disbursed':
      case 'Verified':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.3)]';
      case 'Disputed':
      case 'Delayed':
      case 'Rejected':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-[0_0_12px_rgba(244,63,94,0.3)]';
      case 'Possession Completed':
        return 'bg-emerald-800/30 text-emerald-200 border-emerald-600/50 shadow-[0_0_12px_rgba(5,150,105,0.4)]';
      case 'In Progress':
      case 'Active':
      case 'Payment Processing':
      case 'Under Review':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-[0_0_12px_rgba(34,211,238,0.3)]';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border whitespace-nowrap ${sizeClasses} ${getBadgeStyle()}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {status}
    </span>
  );
};
