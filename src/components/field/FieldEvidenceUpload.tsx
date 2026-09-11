import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { GlassCard } from '../common/GlassCard';
import { StatusBadge } from '../common/StatusBadge';
import {
  Camera,
  UploadCloud,
  MapPin,
  Clock,
  UserCheck,
  CheckCircle2,
  AlertCircle,
  FileImage,
  Sparkles,
  Compass,
  Check,
  RefreshCw,
} from 'lucide-react';
import { FieldPhoto } from '../../types';

export const FieldEvidenceUpload: React.FC = () => {
  const {
    landParcels,
    fieldPhotos,
    selectedParcelId,
    setSelectedParcelId,
    addFieldPhoto,
    verifyFieldPhoto,
    showToast,
  } = useApp();

  const [parcelId, setParcelId] = useState(selectedParcelId || landParcels[0]?.id || 'TS-HYD-2026-001245');
  const [photoType, setPhotoType] = useState<'Boundary Marker' | 'Agricultural Crop' | 'Residential Structure' | 'Commercial Shed'>('Boundary Marker');
  const [notes, setNotes] = useState('');
  const [officerId, setOfficerId] = useState('FO-TEL-7842 (V. Naresh)');

  // GPS Simulation state
  const [gpsCoord, setGpsCoord] = useState<{ lat: number; lng: number }>({
    lat: 17.4485,
    lng: 78.6812,
  });
  const [gpsAccuracy, setGpsAccuracy] = useState<number>(0.8);
  const [isCapturingGps, setIsCapturingGps] = useState(false);

  // Selected sample image
  const sampleImages = [
    {
      label: 'Survey Peg & Boundary Stone',
      url: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80',
    },
    {
      label: 'Standing Paddy Crop Survey',
      url: 'https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=800&q=80',
    },
    {
      label: 'Residential Boundary Wall',
      url: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
    },
    {
      label: 'Tube Well & Electric Transformer',
      url: 'https://images.unsplash.com/photo-1589802829985-817e51171b92?auto=format&fit=crop&w=800&q=80',
    },
  ];
  const [selectedSampleUrl, setSelectedSampleUrl] = useState(sampleImages[0].url);

  const handleSimulateGPS = () => {
    setIsCapturingGps(true);
    setTimeout(() => {
      const lat = 17.4400 + Math.random() * 0.02;
      const lng = 78.6700 + Math.random() * 0.02;
      setGpsCoord({ lat: parseFloat(lat.toFixed(5)), lng: parseFloat(lng.toFixed(5)) });
      setGpsAccuracy(parseFloat((0.4 + Math.random() * 0.5).toFixed(1)));
      setIsCapturingGps(false);
      showToast('Differential GPS RTK fix locked with sub-meter accuracy', 'success');
    }, 600);
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!notes.trim()) {
      showToast('Please enter brief field inspection notes', 'warning');
      return;
    }

    addFieldPhoto({
      parcelId,
      photoUrl: selectedSampleUrl,
      thumbnailUrl: selectedSampleUrl,
      caption: `${photoType}: ${notes.slice(0, 40)}`,
      gpsCoords: {
        latitude: gpsCoord.lat,
        longitude: gpsCoord.lng,
        accuracyMeters: gpsAccuracy,
      },
      officerName: officerId,
    });
    setNotes('');
  };

  const filteredPhotos = fieldPhotos.filter(
    (p) => !parcelId || p.parcelId === parcelId
  );

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs uppercase font-mono text-emerald-400 font-semibold tracking-wider">
              Mobile Field Survey & Verification Suite
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Field Evidence Upload & Geo-Tagging
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time on-ground photographic evidence with sub-meter RTK GPS timestamps.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Target Parcel:</span>
          <select
            value={parcelId}
            onChange={(e) => {
              setParcelId(e.target.value);
              setSelectedParcelId(e.target.value);
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

      {/* Upload Interface Form + GPS Satellite Lock */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upload Form */}
        <GlassCard className="lg:col-span-7 p-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div className="flex items-center gap-2">
              <Camera className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">
                Upload Field Inspection Photo
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-300 bg-emerald-950/70 border border-emerald-500/40 px-2 py-0.5 rounded">
              Ready for Capture
            </span>
          </div>

          <form onSubmit={handleUploadSubmit} className="space-y-4">
            {/* Parcel & Photo Type */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Target Land Parcel
                </label>
                <select
                  value={parcelId}
                  onChange={(e) => setParcelId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white font-mono focus:border-cyan-400 focus:outline-none"
                >
                  {landParcels.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id} - Sy {p.surveyNumber}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Evidence Category
                </label>
                <select
                  value={photoType}
                  onChange={(e: any) => setPhotoType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:border-cyan-400 focus:outline-none"
                >
                  <option value="Boundary Marker">Boundary Marker / Pillar</option>
                  <option value="Agricultural Crop">Standing Agricultural Crop</option>
                  <option value="Residential Structure">Residential Structure / House</option>
                  <option value="Commercial Shed">Commercial / Industrial Shed</option>
                </select>
              </div>
            </div>

            {/* Photo Selection / Simulated Drag & Drop */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Select or Capture Inspection Photograph
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
                {sampleImages.map((img) => (
                  <div
                    key={img.label}
                    onClick={() => setSelectedSampleUrl(img.url)}
                    className={`relative rounded-xl overflow-hidden border-2 cursor-pointer transition-all aspect-video group ${
                      selectedSampleUrl === img.url
                        ? 'border-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.5)]'
                        : 'border-slate-800 opacity-60 hover:opacity-100'
                    }`}
                  >
                    <img
                      src={img.url}
                      alt={img.label}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                    {selectedSampleUrl === img.url && (
                      <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                    <span className="absolute bottom-0 inset-x-0 bg-slate-950/80 text-[9px] text-slate-200 p-1 truncate">
                      {img.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Inspection Notes */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Inspection Notes & Joint Survey Remarks
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                placeholder="e.g. Concrete survey pillar verified in presence of revenue patwari and landowner. No structural encroachment."
                className="w-full p-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:brightness-110 text-white font-bold text-xs sm:text-sm shadow-[0_0_20px_rgba(16,185,129,0.3)] flex items-center justify-center gap-2 transition-all active:scale-95"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Sign & Geo-Tag Evidence to Cadastral Database</span>
            </button>
          </form>
        </GlassCard>

        {/* GPS Satellite Lock Simulator Card */}
        <GlassCard glow className="lg:col-span-5 p-6 flex flex-col justify-between border-cyan-500/30">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-cyan-400" />
                <h2 className="text-base font-bold text-white">
                  NavIC / GPS Hardware Sync
                </h2>
              </div>
              <button
                onClick={handleSimulateGPS}
                disabled={isCapturingGps}
                className="px-2.5 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-mono flex items-center gap-1.5 transition-all"
              >
                <RefreshCw className={`w-3 h-3 ${isCapturingGps ? 'animate-spin' : ''}`} />
                <span>Re-Acquire RTK</span>
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-[#0B1E36] border border-cyan-500/30">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-slate-400">Current GPS Fix:</span>
                  <span className="text-[10px] font-mono text-emerald-400 font-bold bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/40">
                    RTK FIXED (3D)
                  </span>
                </div>
                <p className="font-tech text-xl font-bold text-white tracking-wider">
                  {gpsCoord.lat}° N, {gpsCoord.lng}° E
                </p>
                <p className="text-[11px] text-cyan-300 mt-0.5 font-mono">
                  Horizontal Accuracy: ±{gpsAccuracy}m • Satellites Locked: 14 NavIC/GLONASS
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                <div className="flex justify-between text-slate-400">
                  <span>Authorized Field Officer:</span>
                  <span className="text-white font-medium">{officerId}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Survey Equipment:</span>
                  <span className="text-white font-medium">Trimble R12i GNSS Rover</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Cryptographic Nonce:</span>
                  <span className="text-cyan-400 font-mono text-[10px]">SHA256: 9b2d...f4a1</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2 mt-4">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              All field evidence uploads undergo automated timestamp anti-tamper checking
              before inclusion in statutory award files.
            </span>
          </div>
        </GlassCard>
      </div>

      {/* Evidence Gallery (Prompt requirement) */}
      <GlassCard className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <FileImage className="w-4 h-4 text-cyan-400" />
              <span>Inspection Evidence Gallery</span>
            </h2>
            <p className="text-xs text-slate-400">
              Field evidence logs tagged to Cadastral Survey records
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-300">
            {filteredPhotos.length} Geo-tagged Records
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPhotos.map((photo) => {
            const isVerified = photo.status === 'Verified';
            return (
              <div
                key={photo.id}
                className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden flex flex-col justify-between hover:border-cyan-500/40 transition-all group"
              >
                {/* Image display */}
                <div className="relative aspect-video w-full overflow-hidden bg-slate-950">
                  <img
                    src={photo.photoUrl || photo.url || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80'}
                    alt={photo.caption}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    referrerPolicy="no-referrer"
                  />
                  <div className="absolute top-2 left-2">
                    <span className="font-mono text-[10px] font-bold text-cyan-300 bg-slate-950/80 px-2 py-0.5 rounded border border-cyan-500/30">
                      {photo.parcelId}
                    </span>
                  </div>
                  <div className="absolute top-2 right-2">
                    <StatusBadge status={photo.status || 'Verified'} />
                  </div>
                </div>

                {/* Card Details */}
                <div className="p-4 space-y-2.5 text-xs flex-1 flex flex-col justify-between">
                  <div>
                    <p className="font-semibold text-white line-clamp-2 mb-2">
                      {photo.caption}
                    </p>

                    <div className="space-y-1 text-slate-300 font-mono text-[11px]">
                      <div className="flex items-center gap-1.5 text-cyan-400">
                        <MapPin className="w-3.5 h-3.5 shrink-0" />
                        <span className="truncate">
                          {photo.gpsCoords
                            ? `${photo.gpsCoords.latitude}°N, ${photo.gpsCoords.longitude}°E`
                            : photo.gpsCoordinates || '17.4485°N, 78.6812°E'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <Clock className="w-3.5 h-3.5 shrink-0" />
                        <span>{photo.timestamp}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-400">
                        <UserCheck className="w-3.5 h-3.5 shrink-0" />
                        <span>{photo.officerName}</span>
                      </div>
                    </div>
                  </div>

                  {/* Verification action */}
                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                    {isVerified ? (
                      <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Verified by Revenue Inspector</span>
                      </span>
                    ) : (
                      <button
                        onClick={() => verifyFieldPhoto(photo.id)}
                        className="w-full py-1.5 px-3 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-[0_0_12px_rgba(16,185,129,0.2)]"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Confirm Revenue Verification</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </GlassCard>
    </div>
  );
};
