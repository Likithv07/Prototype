/**
 * BhoomiSetu – National Land Acquisition & Management System
 * Digital Platform for Transparent and Efficient Land Acquisition
 */

import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { Navbar } from './components/navigation/Navbar';
import { Sidebar } from './components/navigation/Sidebar';
import { WorkflowStepper } from './components/common/WorkflowStepper';
import { ToastContainer } from './components/common/ToastContainer';

// Page Views
import { LandingPage } from './components/landing/LandingPage';
import { RoleSelector } from './components/auth/RoleSelector';
import { LoginPage } from './components/auth/LoginPage';
import { CentralDashboard } from './components/dashboards/CentralDashboard';
import { StateDashboard } from './components/dashboards/StateDashboard';
import { OfficerDashboard } from './components/dashboards/OfficerDashboard';
import { CitizenDashboard } from './components/citizen/CitizenDashboard';
import { ProjectsList } from './components/projects/ProjectsList';
import { ProjectDetails } from './components/projects/ProjectDetails';
import { GisMap } from './components/gis/GisMap';
import { CompensationApproval } from './components/compensation/CompensationApproval';
import { CitizenCompensation } from './components/citizen/CitizenCompensation';
import { FieldEvidenceUpload } from './components/field/FieldEvidenceUpload';
import { GrievancePortal } from './components/citizen/GrievancePortal';
import { DocumentsRepository } from './components/documents/DocumentsRepository';
import { AuditTrail } from './components/audit/AuditTrail';
import { ScopeOfStudy } from './components/scope/ScopeOfStudy';
import { RrDashboard } from './components/rr/RrDashboard';
import { TimelineMonitoring } from './components/timeline/TimelineMonitoring';
import { AiAnalytics } from './components/analytics/AiAnalytics';
import { SectorDashboard } from './components/dashboards/SectorDashboard';
import { AccessRestricted } from './components/common/AccessRestricted';

const AppContent: React.FC = () => {
  const { currentView, userRole } = useApp();
  const [dashboardMode, setDashboardMode] = React.useState<'authority' | 'sector'>('authority');

  // Render view based on state
  const renderView = () => {
    switch (currentView) {
      case 'landing':
        return <LandingPage />;

      case 'portal_select':
        return <RoleSelector />;

      case 'login':
        return <LoginPage />;

      case 'dashboard': {
        if (userRole === 'citizen') {
          return <CitizenDashboard />;
        }

        const renderActiveDashboard = () => {
          if (dashboardMode === 'sector') {
            return <SectorDashboard />;
          }
          switch (userRole) {
            case 'central':
              return <CentralDashboard />;
            case 'state':
              return <StateDashboard />;
            case 'officer':
            case 'field_officer':
              return <OfficerDashboard />;
            case 'admin':
            default:
              return <CentralDashboard />;
          }
        };

        return (
          <div className="space-y-4">
            {/* View Mode Switcher for Administrative Roles */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200/90 p-2.5 rounded-2xl shadow-2xs">
              <div className="flex items-center gap-1.5 bg-slate-100/90 p-1 rounded-xl border border-slate-200 text-xs">
                <button
                  onClick={() => setDashboardMode('authority')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    dashboardMode === 'authority'
                      ? 'bg-white text-blue-950 shadow-2xs border border-slate-200/80 font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {userRole === 'central'
                    ? 'National Strategic Apex (PRAGATI)'
                    : userRole === 'state'
                    ? 'State Directorate Overview'
                    : userRole === 'officer'
                    ? 'District LAO Administration'
                    : 'Strategic Authority View'}
                </button>
                <button
                  onClick={() => setDashboardMode('sector')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                    dashboardMode === 'sector'
                      ? 'bg-white text-blue-950 shadow-2xs border border-slate-200/80 font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Sector Operations (MoRTH / Railways / Power)
                </button>
              </div>
              <div className="text-[11px] text-slate-500 font-medium px-2">
                Active Console: <span className="text-slate-900 font-semibold">{dashboardMode === 'authority' ? 'Statutory Revenue Authority' : 'Line Ministry Operations'}</span>
              </div>
            </div>

            {renderActiveDashboard()}
          </div>
        );
      }

      case 'projects':
        if (userRole === 'citizen') {
          return <AccessRestricted moduleName="National Infrastructure Projects Registry" />;
        }
        return <ProjectsList />;

      case 'project_details':
        if (userRole === 'citizen') {
          return <AccessRestricted moduleName="Project Details & Engineering Alignments" />;
        }
        return <ProjectDetails />;

      case 'gis_map':
        if (userRole === 'citizen') {
          return <AccessRestricted moduleName="GIS Cadastral Geodatabase & Spatial Mapping" />;
        }
        return <GisMap />;

      case 'compensation':
        if (userRole === 'citizen') {
          return <CitizenCompensation />;
        }
        return <CompensationApproval />;

      case 'citizen_compensation':
        return <CitizenCompensation />;

      case 'citizen_land':
        return <CitizenDashboard />;

      case 'field_upload':
        return <FieldEvidenceUpload />;

      case 'consent':
        if (userRole === 'field_officer') {
          return <FieldEvidenceUpload />;
        }
        return <CitizenDashboard />;

      case 'grievance':
        return <GrievancePortal />;

      case 'documents':
        return <DocumentsRepository />;

      case 'audit':
        return <AuditTrail />;

      case 'scope':
        return <ScopeOfStudy />;

      case 'rr_dashboard':
        return <RrDashboard />;

      case 'timeline_monitoring':
        return <TimelineMonitoring />;

      case 'ai_analytics':
        if (userRole === 'citizen') {
          return <AccessRestricted moduleName="AI Predictive Risk & Anomaly Engine" />;
        }
        return <AiAnalytics />;

      default:
        return <LandingPage />;
    }
  };

  const isFullscreenLanding = currentView === 'landing' || currentView === 'portal_select' || currentView === 'login';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans selection:bg-emerald-200 selection:text-emerald-900">
      {/* Top Navbar */}
      <Navbar />

      {/* Interactive National 10-Stage Workflow Stepper shown only on project detail & lifecycle views for administrative users */}
      {!isFullscreenLanding && currentView !== 'dashboard' && userRole !== 'citizen' && (
        <WorkflowStepper />
      )}

      {/* Main Body Area */}
      {isFullscreenLanding ? (
        <main className="flex-1 w-full px-4 sm:px-6 lg:px-8 py-6">
          {renderView()}
        </main>
      ) : (
        <div className="flex-1 flex w-full overflow-hidden">
          {/* Collapsible Role-Specific Light Sidebar */}
          <Sidebar />

          {/* Core Content Area */}
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-50 relative">
            <div className="max-w-7xl mx-auto">
              {renderView()}
            </div>
          </main>
        </div>
      )}

      {/* Global Toast Notification System */}
      <ToastContainer />
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
