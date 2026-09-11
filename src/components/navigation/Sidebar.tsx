import React, { useState } from 'react';
import { useApp, AppView } from '../../context/AppContext';
import {
  LayoutDashboard,
  FolderKanban,
  MapPin,
  Compass,
  Calculator,
  FileText,
  Camera,
  Users,
  HeartHandshake,
  Clock,
  Sparkles,
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  CreditCard,
  MessageSquarePlus,
  FileCheck,
  Settings,
  Bell,
  Building2,
  Landmark,
} from 'lucide-react';
import { UserRole } from '../../types';

export const Sidebar: React.FC = () => {
  const { currentView, setCurrentView, userRole, notifications } = useApp();
  const [collapsed, setCollapsed] = useState(false);

  const unreadCount = notifications.filter((n) => !n.read).length;

  interface SidebarItem {
    id: AppView;
    label: string;
    icon: any;
    badge?: string | number;
  }

  const getRoleMenuItems = (): SidebarItem[] => {
    switch (userRole) {
      case 'central':
        return [
          { id: 'dashboard', label: 'National Dashboard', icon: Landmark },
          { id: 'projects', label: 'National Projects', icon: FolderKanban },
          { id: 'gis_map', label: 'GIS Command Center', icon: Compass },
          { id: 'ai_analytics', label: 'AI Risk Analytics', icon: Sparkles, badge: 'AI' },
          { id: 'timeline_monitoring', label: 'Timeline & Delays', icon: Clock },
          { id: 'rr_dashboard', label: 'R&R Resettlement', icon: HeartHandshake },
          { id: 'documents', label: 'Central Repository', icon: FileText },
          { id: 'audit', label: 'Audit Trail', icon: ShieldAlert },
          { id: 'scope', label: 'Scope of Study', icon: BookOpen },
        ];

      case 'state':
        return [
          { id: 'dashboard', label: 'State Dashboard', icon: Building2 },
          { id: 'projects', label: 'State Projects', icon: FolderKanban },
          { id: 'gis_map', label: 'GIS Cadastral Map', icon: Compass },
          { id: 'compensation', label: 'Compensation Approvals', icon: Calculator },
          { id: 'timeline_monitoring', label: 'District Milestones', icon: Clock },
          { id: 'rr_dashboard', label: 'Affected Families (R&R)', icon: Users },
          { id: 'documents', label: 'State Records', icon: FileText },
          { id: 'audit', label: 'Audit Logs', icon: ShieldAlert },
        ];

      case 'officer':
        return [
          { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
          { id: 'projects', label: 'Projects', icon: FolderKanban },
          { id: 'gis_map', label: 'GIS Map', icon: Compass },
          { id: 'compensation', label: 'Compensation', icon: Calculator, badge: 'Priority' },
          { id: 'documents', label: 'Documents', icon: FileText },
          { id: 'field_upload', label: 'Field Verification', icon: Camera },
          { id: 'consent', label: 'Consent Verification', icon: FileCheck },
          { id: 'rr_dashboard', label: 'Affected Families & R&R', icon: Users },
          { id: 'timeline_monitoring', label: 'Timeline Monitoring', icon: Clock },
          { id: 'ai_analytics', label: 'AI Risk Analysis', icon: Sparkles },
          { id: 'audit', label: 'Audit Trail', icon: ShieldAlert },
        ];

      case 'field_officer':
        return [
          { id: 'dashboard', label: 'Field Dashboard', icon: LayoutDashboard },
          { id: 'field_upload', label: 'Field Evidence Upload', icon: Camera, badge: 'Active' },
          { id: 'consent', label: 'Landowner Consent', icon: FileCheck },
          { id: 'gis_map', label: 'Field GIS Navigation', icon: Compass },
          { id: 'documents', label: 'Survey Documents', icon: FileText },
          { id: 'timeline_monitoring', label: 'Field Schedule', icon: Clock },
        ];

      case 'citizen':
        return [
          { id: 'dashboard', label: 'My Land Acquisition', icon: LayoutDashboard },
          { id: 'citizen_compensation', label: 'My Compensation', icon: CreditCard, badge: '₹72.25L' },
          { id: 'citizen_land', label: 'My Land & GIS Map', icon: MapPin },
          { id: 'consent', label: 'Digital Consent eSign', icon: FileCheck },
          { id: 'grievance', label: 'Raise a Grievance', icon: MessageSquarePlus },
          { id: 'documents', label: 'My Documents', icon: FileText },
        ];

      case 'admin':
        return [
          { id: 'dashboard', label: 'System Overview', icon: LayoutDashboard },
          { id: 'projects', label: 'All Projects', icon: FolderKanban },
          { id: 'gis_map', label: 'GIS Geodatabase', icon: Compass },
          { id: 'compensation', label: 'Compensation Engine', icon: Calculator },
          { id: 'audit', label: 'System Audit Logs', icon: ShieldAlert, badge: 'Live' },
          { id: 'documents', label: 'Repository Security', icon: FileText },
          { id: 'scope', label: 'Scope Matrix', icon: BookOpen },
        ];

      default:
        return [];
    }
  };

  const menuItems = getRoleMenuItems();

  const roleTitleMap: Record<UserRole, string> = {
    central: 'Central Authority',
    state: 'State Authority',
    officer: 'District LAO Portal',
    field_officer: 'Field Mobile Unit',
    citizen: 'Citizen Portal',
    admin: 'Command Console',
  };

  return (
    <aside
      className={`relative shrink-0 border-r border-cyan-500/20 bg-[#071A2D]/95 backdrop-blur-2xl transition-all duration-300 flex flex-col z-30 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        {!collapsed && (
          <div>
            <span className="text-[10px] uppercase font-mono tracking-widest text-cyan-400 font-bold block">
              Active Portal
            </span>
            <span className="text-sm font-semibold text-white tracking-tight">
              {roleTitleMap[userRole]}
            </span>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={`p-1.5 rounded-lg border border-slate-700/60 text-slate-400 hover:text-white hover:border-cyan-500/40 transition-colors ${
            collapsed ? 'mx-auto' : ''
          }`}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group relative ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600/30 via-indigo-600/20 to-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_20px_rgba(34,211,238,0.2)]'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/50 border border-transparent'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon
                className={`w-5 h-5 shrink-0 transition-transform group-hover:scale-110 ${
                  isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
                }`}
              />

              {!collapsed && (
                <span className="truncate flex-1 text-left tracking-tight">{item.label}</span>
              )}

              {!collapsed && item.badge && (
                <span className="px-1.5 py-0.5 text-[10px] font-bold rounded-md bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {item.badge}
                </span>
              )}

              {isActive && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-cyan-400 rounded-r-full shadow-[0_0_8px_#22D3EE]" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer / Quick Status */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
        {!collapsed ? (
          <div className="flex items-center gap-3 px-2 py-1.5 rounded-xl bg-[#0B1E36] border border-cyan-500/20 text-xs">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#10B981]" />
            <div className="flex-1 min-w-0">
              <p className="text-[11px] font-medium text-slate-200 truncate">NIC GIS Gateway</p>
              <p className="text-[9px] text-slate-400 font-mono">Live Sync • 99.98% SLA</p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center" title="NIC GIS Gateway Online">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
};
