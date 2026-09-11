import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Compass,
  Search,
  ZoomIn,
  ZoomOut,
  Layers,
  MapPin,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Calculator,
  Camera,
  RotateCcw,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { LandParcel } from '../../types';

export const GisMap: React.FC = () => {
  const {
    landParcels,
    selectedParcelId,
    setSelectedParcelId,
    setCurrentView,
    setUserRole,
    showToast,
  } = useApp();

  const [searchSurvey, setSearchSurvey] = useState('');
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [activeLayer, setActiveLayer] = useState<'cadastral' | 'satellite' | 'alignment' | 'heatmap'>('cadastral');
  const [showLegend, setShowLegend] = useState(true);

  const selectedParcel =
    landParcels.find((p) => p.id === selectedParcelId) || landParcels[0];

  const filteredParcels = landParcels.filter(
    (p) =>
      p.surveyNumber.toLowerCase().includes(searchSurvey.toLowerCase()) ||
      p.id.toLowerCase().includes(searchSurvey.toLowerCase()) ||
      p.landownerName.toLowerCase().includes(searchSurvey.toLowerCase())
  );

  const getParcelColor = (status?: string) => {
    switch (status) {
      case 'Land Acquired':
      case 'Acquired':
      case 'Possession Completed':
        return {
          fill: 'rgba(16, 185, 129, 0.45)',
          stroke: '#10B981',
          name: 'Acquired (Green)',
        };
      case 'Proposed':
      case 'Notification Issued':
      case 'Pending':
        return {
          fill: 'rgba(245, 158, 11, 0.45)',
          stroke: '#F59E0B',
          name: 'Pending (Yellow)',
        };
      case 'Disputed':
      case 'Under Dispute':
        return {
          fill: 'rgba(239, 68, 68, 0.5)',
          stroke: '#EF4444',
          name: 'Under Dispute (Red)',
        };
      case 'Compensation Pending':
      case 'Compensation In Progress':
      case 'Under Verification':
      default:
        return {
          fill: 'rgba(34, 211, 238, 0.45)',
          stroke: '#22D3EE',
          name: 'Compensation In Progress (Cyan)',
        };
    }
  };

  return (
    <div className="space-y-4 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-cyan-400 font-semibold tracking-wider">
              National Cadastral Geodatabase & GIS Engine
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Interactive GIS Cadastral Map
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            High-precision polygon parcel visualization, satellite overlay, and alignment buffers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search by Survey Number */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchSurvey}
              onChange={(e) => setSearchSurvey(e.target.value)}
              placeholder="Search Survey No. (e.g. 145/2)..."
              className="pl-8 pr-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <button
            onClick={() => {
              setZoomLevel(1);
              showToast('GIS viewport centered to Telangana NH-65 Alignment', 'info');
            }}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white border border-slate-700"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Map Container */}
      <div className="relative w-full h-[620px] rounded-2xl overflow-hidden border border-cyan-500/30 bg-[#071524] shadow-2xl">
        {/* Dynamic Background depending on activeLayer */}
        {activeLayer === 'satellite' ? (
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-[#0a1829] to-[#040c17]">
            {/* Simulated Satellite Terrain Texture */}
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#22d3ee_1px,transparent_1px)] [background-size:16px_16px]" />
          </div>
        ) : (
          <div className="absolute inset-0 gis-grid-pattern opacity-40" />
        )}

        {/* Map Interactive SVG Stage */}
        <div
          className="w-full h-full flex items-center justify-center transition-transform duration-300 relative cursor-grab active:cursor-grabbing select-none"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          <svg
            viewBox="0 0 800 600"
            className="w-full h-full"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="alignmentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#22D3EE" stopOpacity="1" />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity="0.8" />
              </linearGradient>

              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(34, 211, 238, 0.05)" strokeWidth="1" />
              </pattern>
            </defs>

            <rect width="800" height="600" fill="url(#grid)" />

            {/* Background River / Geography */}
            <path
              d="M -50,120 Q 200,180 350,110 T 850,220"
              fill="none"
              stroke="rgba(37, 99, 235, 0.2)"
              strokeWidth="28"
              strokeLinecap="round"
            />
            <text x="50" y="160" fill="rgba(56, 189, 248, 0.3)" fontSize="11" fontFamily="sans-serif">
              Musi River Tributary / Drainage Canal
            </text>

            {/* Project Alignment Corridor Buffer (60m ROW) */}
            {(activeLayer === 'alignment' || activeLayer === 'cadastral' || activeLayer === 'satellite') && (
              <g>
                <path
                  d="M 50,450 C 220,410 380,280 580,230 S 760,120 820,100"
                  fill="none"
                  stroke="rgba(34, 211, 238, 0.15)"
                  strokeWidth="80"
                  strokeLinecap="round"
                />
                <path
                  d="M 50,450 C 220,410 380,280 580,230 S 760,120 820,100"
                  fill="none"
                  stroke="url(#alignmentGrad)"
                  strokeWidth="4"
                  strokeDasharray="8 4"
                />
                <text x="440" y="245" fill="#22D3EE" fontSize="11" fontWeight="bold" fontFamily="Rajdhani">
                  NH-65 EXPRESSWAY CENTERLINE (ROW: 60M)
                </text>
              </g>
            )}

            {/* Cadastral Land Parcel Polygons */}
            {filteredParcels.map((parcel) => {
              const parcelStatus = parcel.acquisitionStatus || parcel.status;
              const colors = getParcelColor(parcelStatus);
              const isSelected = selectedParcel.id === parcel.id;
              const pointsStr = parcel.polygonCoords
                ? parcel.polygonCoords.map(([x, y]) => `${x},${y}`).join(' ')
                : parcel.coordinates
                ? parcel.coordinates.map((pt) => `${pt.x},${pt.y}`).join(' ')
                : '100,100 200,100 200,200 100,200';

              // Calculate centroid approx
              const avgX = parcel.center
                ? parcel.center[0]
                : parcel.coordinates
                ? parcel.coordinates.reduce((sum, p) => sum + p.x, 0) / parcel.coordinates.length
                : 400;
              const avgY = parcel.center
                ? parcel.center[1]
                : parcel.coordinates
                ? parcel.coordinates.reduce((sum, p) => sum + p.y, 0) / parcel.coordinates.length
                : 300;

              return (
                <g
                  key={parcel.id}
                  onClick={() => {
                    setSelectedParcelId(parcel.id);
                    showToast(`Selected Survey No. ${parcel.surveyNumber} (${parcel.landownerName})`, 'info');
                  }}
                  className="cursor-pointer transition-all duration-200 group"
                >
                  <polygon
                    points={pointsStr}
                    fill={colors.fill}
                    stroke={isSelected ? '#FFFFFF' : colors.stroke}
                    strokeWidth={isSelected ? '3' : '1.5'}
                    className="hover:brightness-125 transition-all"
                  />
                  {isSelected && (
                    <polygon
                      points={pointsStr}
                      fill="none"
                      stroke="#22D3EE"
                      strokeWidth="6"
                      strokeOpacity="0.4"
                    />
                  )}

                  {/* Survey Label on Parcel */}
                  <text
                    x={avgX}
                    y={avgY - 4}
                    textAnchor="middle"
                    fill="#FFFFFF"
                    fontSize="10"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    Sy {parcel.surveyNumber}
                  </text>
                  <text
                    x={avgX}
                    y={avgY + 9}
                    textAnchor="middle"
                    fill="#CBD5E1"
                    fontSize="9"
                    fontFamily="sans-serif"
                  >
                    {parcel.areaAcres} Ac
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Top-Right Layer Switcher & Controls */}
        <div className="absolute top-4 right-4 flex flex-col gap-2 z-20">
          <div className="flex rounded-xl bg-slate-950/85 p-1 border border-cyan-500/30 backdrop-blur-md shadow-xl text-xs">
            <button
              onClick={() => setActiveLayer('cadastral')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeLayer === 'cadastral'
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Cadastral
            </button>
            <button
              onClick={() => setActiveLayer('satellite')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeLayer === 'satellite'
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Satellite
            </button>
            <button
              onClick={() => setActiveLayer('alignment')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeLayer === 'alignment'
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              Alignment
            </button>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center self-end bg-slate-950/85 border border-cyan-500/30 rounded-xl p-1 backdrop-blur-md">
            <button
              onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.25))}
              className="p-1.5 text-slate-300 hover:text-cyan-300"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <span className="text-[10px] font-mono px-2 text-slate-400">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.75, z - 0.25))}
              className="p-1.5 text-slate-300 hover:text-cyan-300"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Bottom-Left Color Legend */}
        {showLegend && (
          <div className="absolute bottom-4 left-4 p-3.5 rounded-xl bg-slate-950/90 border border-cyan-500/30 backdrop-blur-md shadow-2xl text-xs z-20 max-w-xs">
            <div className="flex items-center justify-between font-semibold text-white mb-2 border-b border-slate-800 pb-1.5">
              <span className="flex items-center gap-1.5 text-cyan-300 font-mono text-[11px] uppercase">
                <Layers className="w-3.5 h-3.5" />
                Cadastral Status Legend
              </span>
              <button
                onClick={() => setShowLegend(false)}
                className="text-[10px] text-slate-400 hover:text-white"
              >
                Hide
              </button>
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-emerald-500 border border-emerald-300" />
                <span className="text-slate-300 text-[11px]">Acquired (Green)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-amber-500 border border-amber-300" />
                <span className="text-slate-300 text-[11px]">Pending (Yellow)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-rose-500 border border-rose-300" />
                <span className="text-slate-300 text-[11px]">Under Dispute (Red)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-sm bg-cyan-400 border border-cyan-200" />
                <span className="text-slate-300 text-[11px]">Compensation In Progress (Cyan)</span>
              </div>
            </div>
          </div>
        )}

        {/* Floating Details Card for Selected Parcel (Prompt Requirement) */}
        {selectedParcel && (
          <div className="absolute bottom-4 right-4 w-80 sm:w-96 rounded-2xl glass-panel-glow p-5 border border-cyan-500/40 shadow-2xl z-20 animate-in fade-in slide-in-from-bottom-3 duration-200">
            <div className="flex items-start justify-between border-b border-slate-800 pb-3 mb-3">
              <div>
                <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase">
                  Survey Details
                </span>
                <h3 className="text-base font-bold text-white">
                  Sy No: {selectedParcel.surveyNumber}
                </h3>
                <p className="text-[11px] font-mono text-slate-400">{selectedParcel.id}</p>
              </div>
              <StatusBadge status={selectedParcel.acquisitionStatus || selectedParcel.status || 'Pending'} />
            </div>

            <div className="space-y-2 text-xs mb-4">
              <div className="flex justify-between text-slate-300">
                <span className="text-slate-400">Landowner Name:</span>
                <span className="font-semibold text-white">{selectedParcel.landownerName}</span>
              </div>

              <div className="flex justify-between text-slate-300">
                <span className="text-slate-400">Area Acquired:</span>
                <span className="font-mono text-white">{selectedParcel.areaAcres} Acres</span>
              </div>

              <div className="flex justify-between text-slate-300">
                <span className="text-slate-400">Land Classification:</span>
                <span className="text-slate-200">{selectedParcel.landType}</span>
              </div>

              <div className="flex justify-between text-slate-300">
                <span className="text-slate-400">Location:</span>
                <span className="text-slate-200">{selectedParcel.village}, {selectedParcel.district}</span>
              </div>

              <div className="p-2.5 rounded-xl bg-emerald-950/60 border border-emerald-500/30 flex justify-between items-center">
                <span className="text-emerald-300 text-[11px]">Calculated Award:</span>
                <span className="font-tech text-base font-bold text-emerald-400">
                  ₹{(selectedParcel.compensation?.totalCompensation || selectedParcel.totalCompensation || 0).toLocaleString('en-IN')}
                </span>
              </div>
            </div>

            {/* Direct Connected Action Buttons */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => {
                  setUserRole('officer');
                  setCurrentView('compensation');
                }}
                className="px-3 py-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
              >
                <Calculator className="w-3.5 h-3.5" />
                <span>Award Calc</span>
              </button>

              <button
                onClick={() => {
                  setUserRole('field_officer');
                  setCurrentView('field_upload');
                }}
                className="px-3 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
              >
                <Camera className="w-3.5 h-3.5" />
                <span>Field Evidence</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
