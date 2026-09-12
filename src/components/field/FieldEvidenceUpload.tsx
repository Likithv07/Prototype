import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { StatusBadge } from '../common/StatusBadge';
import {
  Camera,
  UploadCloud,
  MapPin,
  Clock,
  UserCheck,
  CheckCircle2,
  FileImage,
  Sparkles,
  Compass,
  Check,
  RefreshCw,
} from 'lucide-react';

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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-700" />
            <span className="text-xs uppercase font-mono text-blue-900 font-bold tracking-wider">
              Mobile Field Survey & Verification Suite
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Field Evidence Upload & Geo-Tagging
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Real-time on-ground photographic evidence with sub-meter RTK GPS timestamps.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Target Parcel:</span>
          <select
            value={parcelId}
            onChange={(e) => {
              setParcelId(e.target.value);
              setSelectedParcelId(e.target.value);
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

      {/* Upload Interface Form + GPS Satellite Lock */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upload Form */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
            <div className="flex items-center gap-2">
              <Camera className="w-5 h-5 text-blue-700" />
              <h2 className="text-base font-bold text-slate-900">
                Upload Field Inspection Photo
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-800 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded font-semibold">
              Ready for Capture
            </span>
          </div>

          <form onSubmit={handleUploadSubmit} className="space-y-4">
            {/* Parcel & Photo Type */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Land Parcel
                </label>
                <select
                  value={parcelId}
                  onChange={(e) => setParcelId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 font-mono focus:border-blue-700 focus:bg-white focus:outline-none"
                >
                  {landParcels.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.id} - Sy {p.surveyNumber}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Evidence Category
                </label>
                <select
                  value={photoType}
                  onChange={(e: any) => setPhotoType(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 font-medium focus:border-blue-700 focus:bg-white focus:outline-none"
                >
                  <option value="Boundary Marker">Boundary Marker / Pillar</option>
                  <option value="Agricultural Crop">Standing Agricultural Crop</option>
                  <option value="Residential Structure">Residential Structure / House</option>
                  <option value="Commercial Shed">Commercial / Industrial Shed</option>
                </select>
              </div>
            </div>

            {/* Photo Selection */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Select or Capture Inspection Photograph
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-2">
                {sampleImages.map((img) => (
                  <div
                    key={img.label}
                    onClick={() => setSelectedSampleUrl(img.url)}
                    className={`relative rounded-xl overflow-hidden border-2 cursor-pointer transition-all aspect-video group ${
                      selectedSampleUrl === img.url
                        ? 'border-blue-700 ring-2 ring-blue-100'
                        : 'border-slate-200 opacity-80 hover:opacity-100'
                    }`}
                  >
                    <img
                      src={img.url}
                      alt={img.label}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                    {selectedSampleUrl === img.url && (
                      <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-blue-700 text-white flex items-center justify-center">
                        <Check className="w-3 h-3 stroke-[3]" />
                      </div>
                    )}
                    <span className="absolute bottom-0 inset-x-0 bg-slate-900/80 text-[9.5px] text-white p-1 truncate font-medium">
                      {img.label}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Inspection Notes */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Inspection Notes & Joint Survey Remarks
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                placeholder="e.g. Concrete survey pillar verified in presence of revenue patwari and landowner. No structural encroachment."
                className="w-full p-2.5 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:bg-white"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-2xs flex items-center justify-center gap-2 transition-colors"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Sign & Geo-Tag Evidence to Cadastral Database</span>
            </button>
          </form>
        </div>

        {/* GPS Satellite Lock Simulator Card */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-blue-700" />
                <h2 className="text-base font-bold text-slate-900">
                  NavIC / GPS Hardware Sync
                </h2>
              </div>
              <button
                onClick={handleSimulateGPS}
                disabled={isCapturingGps}
                className="px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 text-xs font-mono flex items-center gap-1.5 transition-colors font-semibold"
              >
                <RefreshCw className={`w-3 h-3 ${isCapturingGps ? 'animate-spin' : ''}`} />
                <span>Re-Acquire RTK</span>
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-slate-600 font-medium">Current GPS Fix:</span>
                  <span className="text-[10px] font-mono text-emerald-800 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    RTK FIXED (3D)
                  </span>
                </div>
                <p className="font-mono text-xl font-bold text-slate-900 tracking-wider">
                  {gpsCoord.lat}° N, {gpsCoord.lng}° E
                </p>
                <p className="text-[11px] text-blue-900 mt-0.5 font-mono font-medium">
                  Horizontal Accuracy: ±{gpsAccuracy}m • Satellites Locked: 14 NavIC/GLONASS
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                <div className="flex justify-between text-slate-600">
                  <span>Authorized Field Officer:</span>
                  <span className="text-slate-900 font-semibold">{officerId}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Survey Equipment:</span>
                  <span className="text-slate-900 font-medium">Trimble R12i GNSS Rover</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Cryptographic Nonce:</span>
                  <span className="text-blue-900 font-mono text-[10.5px] font-semibold">SHA256: 9b2d...f4a1</span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 flex items-start gap-2 mt-4">
            <Sparkles className="w-4 h-4 text-blue-700 shrink-0 mt-0.5" />
            <span>
              All field evidence uploads undergo automated timestamp anti-tamper checking
              before inclusion in statutory award files.
            </span>
          </div>
        </div>
      </div>

      {/* Evidence Gallery */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FileImage className="w-4 h-4 text-blue-700" />
              <span>Inspection Evidence Gallery</span>
            </h2>
            <p className="text-xs text-slate-600 mt-0.5">
              Field evidence logs tagged to Cadastral Survey records
            </p>
          </div>
          <span className="text-xs font-mono text-slate-600 font-bold">
            {filteredPhotos.length} Geo-tagged Records
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPhotos.map((photo) => {
            const isVerified = photo.status === 'Verified';
            return (
              <div
                key={photo.id}
                className="rounded-2xl border border-slate-200 bg-white overflow-hidden flex flex-col justify-between hover:border-blue-300 transition-all shadow-2xs group"
              >
                {/* Image display */}
                <div className="relative aspect-video w-full overflow-hidden bg-slate-100">
                  <img
                    src={photo.photoUrl || photo.url || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80'}
                    alt={photo.caption}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    referrerPolicy="no-referrer"
                  />
                  <div className="absolute top-2 left-2">
                    <span className="font-mono text-[10px] font-bold text-slate-900 bg-white/95 px-2 py-0.5 rounded shadow-xs border border-slate-200">
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
                    <p className="font-semibold text-slate-900 line-clamp-2 mb-2">
                      {photo.caption}
                    </p>

                    <div className="space-y-1 text-slate-600 font-mono text-[11px]">
                      <div className="flex items-center gap-1.5 text-blue-900 font-semibold">
                        <MapPin className="w-3.5 h-3.5 shrink-0 text-blue-700" />
                        <span className="truncate">
                          {photo.gpsCoords
                            ? `${photo.gpsCoords.latitude}°N, ${photo.gpsCoords.longitude}°E`
                            : photo.gpsCoordinates || '17.4485°N, 78.6812°E'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <Clock className="w-3.5 h-3.5 shrink-0" />
                        <span>{photo.timestamp}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-slate-500">
                        <UserCheck className="w-3.5 h-3.5 shrink-0" />
                        <span>{photo.officerName}</span>
                      </div>
                    </div>
                  </div>

                  {/* Verification action */}
                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                    {isVerified ? (
                      <span className="text-[11px] text-emerald-800 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Verified by Revenue Inspector</span>
                      </span>
                    ) : (
                      <button
                        onClick={() => verifyFieldPhoto(photo.id)}
                        className="w-full py-1.5 px-3 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-2xs"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Confirm Revenue Verification</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
