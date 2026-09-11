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
import { FieldEvidenceUpload } from './components/field/FieldEvidenceUpload';
import { GrievancePortal } from './components/citizen/GrievancePortal';
import { DocumentsRepository } from './components/documents/DocumentsRepository';
import { AuditTrail } from './components/audit/AuditTrail';
import { ScopeOfStudy } from './components/scope/ScopeOfStudy';
import { RrDashboard } from './components/rr/RrDashboard';
import { TimelineMonitoring } from './components/timeline/TimelineMonitoring';
import { AiAnalytics } from './components/analytics/AiAnalytics';
import { SectorDashboard } from './components/dashboards/SectorDashboard';

const AppContent: React.FC = () => {
  const { currentView, userRole } = useApp();

  // Render view based on state
  const renderView = () => {
    switch (currentView) {
      case 'landing':
        return <LandingPage />;

      case 'portal_select':
        return <RoleSelector />;

      case 'login':
        return <LoginPage />;

      case 'dashboard':
        return <SectorDashboard />;

      case 'projects':
        return <ProjectsList />;

      case 'project_details':
        return <ProjectDetails />;

      case 'gis_map':
        return <GisMap />;

      case 'compensation':
        return <CompensationApproval />;

      case 'citizen_compensation':
        return <CitizenDashboard />;

      case 'citizen_land':
        return <GisMap />;

      case 'field_upload':
        return <FieldEvidenceUpload />;

      case 'consent':
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
        return <AiAnalytics />;

      default:
        return <LandingPage />;
    }
  };

  const isFullscreenLanding = currentView === 'landing' || currentView === 'portal_select' || currentView === 'login';

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      {/* Top Navbar */}
      <Navbar />

      {/* Interactive National 10-Stage Workflow Stepper shown only on project detail & lifecycle views */}
      {!isFullscreenLanding && currentView !== 'dashboard' && (
        <WorkflowStepper />
      )}

      {/* Main Body Area */}
      {isFullscreenLanding ? (
        <main className="flex-1 w-full px-4 sm:px-6 lg:px-8">
          {renderView()}
        </main>
      ) : (
        <div className="flex-1 flex w-full overflow-hidden">
          {/* Collapsible Role-Specific Glassmorphism Sidebar */}
          <Sidebar />

          {/* Core Content Area */}
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-[#0B1120] relative">
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
