import React, { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';
import { GlassCard } from './GlassCard';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  color?: 'blue' | 'cyan' | 'purple' | 'emerald' | 'amber' | 'rose';
  id?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'cyan',
  id,
}) => {
  const colorMap = {
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/30 shadow-[0_0_20px_rgba(37,99,235,0.2)]',
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30 shadow-[0_0_20px_rgba(34,211,238,0.2)]',
    purple: 'text-purple-400 bg-purple-500/10 border-purple-500/30 shadow-[0_0_20px_rgba(139,92,246,0.2)]',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.2)]',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.2)]',
    rose: 'text-rose-400 bg-rose-500/10 border-rose-500/30 shadow-[0_0_20px_rgba(239,68,68,0.2)]',
  };

  const iconColor = {
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    purple: 'text-purple-400',
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    rose: 'text-rose-400',
  }[color];

  return (
    <GlassCard id={id} className="p-5 relative overflow-hidden group hover:border-cyan-500/40">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-wider text-slate-400 font-medium">{title}</p>
          <div className="text-2xl lg:text-3xl font-bold font-tech text-white tracking-tight flex items-baseline gap-1.5">
            {value}
          </div>
          {subtitle && <p className="text-xs text-slate-400 font-normal mt-1">{subtitle}</p>}
          {trend && (
            <div className="flex items-center gap-1 text-xs pt-1">
              <span className={trend.isPositive ? 'text-emerald-400' : 'text-rose-400'}>
                {trend.isPositive ? '↑' : '↓'} {trend.value}
              </span>
              <span className="text-slate-500">vs target</span>
            </div>
          )}
        </div>

        <div className={`p-3 rounded-xl border ${colorMap[color]} transition-transform duration-300 group-hover:scale-110`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>
      </div>

      <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-cyan-500/5 rounded-full blur-xl pointer-events-none group-hover:bg-cyan-500/10 transition-colors" />
    </GlassCard>
  );
};
