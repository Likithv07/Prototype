import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { FieldDocument } from '../../types';
import {
  FileText,
  Search,
  UploadCloud,
  Download,
  Eye,
  ShieldCheck,
  X,
  CheckCircle2,
  Calendar,
  Layers,
  Lock,
  FileCheck,
} from 'lucide-react';

interface RepoDocument {
  id: string;
  title: string;
  category: string;
  parcelOrProject: string;
  date: string;
  size: string;
  verified: boolean;
  hash: string;
  source: 'statutory' | 'field';
  fileType?: string;
}

export const DocumentsRepository: React.FC = () => {
  const { fieldDocuments, addFieldDocument, landParcels, showToast } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  // Modal states
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [previewDoc, setPreviewDoc] = useState<RepoDocument | null>(null);

  // Upload form state
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState<FieldDocument['category']>('Title Deed');
  const [uploadParcelId, setUploadParcelId] = useState(landParcels[0]?.id || 'TS-HYD-2026-001245');
  const [uploadFileName, setUploadFileName] = useState('');

  const statutoryDocuments: RepoDocument[] = [
    {
      id: 'DOC-2026-0814',
      title: 'Gazette Notification Section 3D (Declaration of Acquisition)',
      category: 'Gazette',
      parcelOrProject: 'NLA-TS-2026-001 (NH-65 Corridor)',
      date: '02 Mar 2026',
      size: '3.8 MB',
      verified: true,
      hash: 'sha256: 7f8a192bc93214589dfbe76a1004cd821a81...',
      source: 'statutory',
      fileType: 'pdf',
    },
    {
      id: 'DOC-2026-0792',
      title: 'Form 16-B Field Joint Measurement & Horticultural Tree Valuation',
      category: 'Valuation',
      parcelOrProject: 'TS-HYD-2026-001245 (Sy 145/2)',
      date: '28 Feb 2026',
      size: '5.2 MB',
      verified: true,
      hash: 'sha256: 419208aefd882194bbce10992381fca99021...',
      source: 'statutory',
      fileType: 'pdf',
    },
    {
      id: 'DOC-2026-0610',
      title: 'Gram Sabha Public Consultation Resolution & SIA Approval',
      category: 'SIA & Consent',
      parcelOrProject: 'Ghatkesar Revenue Mandal',
      date: '15 Feb 2026',
      size: '2.1 MB',
      verified: true,
      hash: 'sha256: b892019488a01fe8399120bc7102948192a8...',
      source: 'statutory',
      fileType: 'pdf',
    },
    {
      id: 'DOC-2026-0544',
      title: 'Certified Record of Rights (Pahani / 1-B Extract)',
      category: 'Title Deed',
      parcelOrProject: 'TS-HYD-2026-001246 (Sy 145/3)',
      date: '04 Feb 2026',
      size: '1.4 MB',
      verified: true,
      hash: 'sha256: ea91823901ba8892ca8817263bba01928371...',
      source: 'statutory',
      fileType: 'pdf',
    },
    {
      id: 'DOC-2026-0418',
      title: 'Aadhaar eSign Verified Consent Undertaking (Form 8-A)',
      category: 'Consent Form',
      parcelOrProject: 'TS-HYD-2026-001245 (Rajesh Kumar)',
      date: '08 Mar 2026',
      size: '890 KB',
      verified: true,
      hash: 'sha256: 18294719bbac902194881726a88201924719...',
      source: 'statutory',
      fileType: 'pdf',
    },
  ];

  // Convert fieldDocuments from AppContext into RepoDocument format
  const dynamicFieldDocs: RepoDocument[] = fieldDocuments.map((fd) => ({
    id: fd.id,
    title: fd.title,
    category: fd.category,
    parcelOrProject: fd.parcelId,
    date: fd.uploadDate,
    size: fd.fileSize,
    verified: fd.status === 'Verified',
    hash: fd.documentHash ? `sha256: ${fd.documentHash}` : 'sha256: 3c9148...',
    source: 'field',
    fileType: fd.fileType,
  }));

  const allDocuments: RepoDocument[] = [...dynamicFieldDocs, ...statutoryDocuments];

  const filteredDocs = allDocuments.filter((doc) => {
    const matchSearch =
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.parcelOrProject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = selectedCategory === 'ALL' || doc.category === selectedCategory;
    return matchSearch && matchCat;
  });

  const handleDownload = (doc: RepoDocument) => {
    const content = `==================================================================
GOVERNMENT OF INDIA - BHOOMISETU STATUTORY REPOSITORY
CERTIFIED NATIONAL LAND RECORD & GAZETTE COPY
==================================================================
DOCUMENT IDENTIFIER : ${doc.id}
DOCUMENT TITLE      : ${doc.title}
STATUTORY CATEGORY  : ${doc.category}
ASSOCIATED ENTITY   : ${doc.parcelOrProject}
RECORDING DATE      : ${doc.date}
FILE SPECIFICATION  : ${doc.size} (${doc.fileType?.toUpperCase() || 'PDF'})
INTEGRITY VERIFIED  : ${doc.verified ? 'YES - CRYPTOGRAPHICALLY VALID' : 'PENDING OFFICIAL COUNTERSIGN'}
SHA-256 CHECKSUM    : ${doc.hash}
TIME OF DISPATCH    : ${new Date().toISOString()} IST
ISSUING AUTHORITY   : Competent Authority for Land Acquisition (CALA)
==================================================================
Notice: This document is an electronically generated and certified record 
recognized under Section 4 of the Information Technology Act 2000 and 
RFCTLARR Act 2013.
==================================================================`;

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${doc.id}_${doc.title.substring(0, 20).replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast(`Downloaded certified record: ${doc.title}`, 'success');
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadTitle.trim()) {
      showToast('Please enter a document title', 'warning');
      return;
    }

    addFieldDocument({
      parcelId: uploadParcelId,
      title: uploadTitle,
      category: uploadCategory,
      uploadedBy: 'LAO District Secretariat',
      fileSize: uploadFileName ? '2.4 MB' : '1.8 MB',
      fileType: 'pdf',
    });

    setUploadTitle('');
    setUploadFileName('');
    setShowUploadModal(false);
  };

  return (
    <div className="space-y-6 pb-16 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-700" />
            <span className="text-xs uppercase font-mono text-blue-900 font-bold tracking-wider">
              Cryptographically Signed National Document Vault
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight mt-1">
            Statutory Document Repository
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
            Immutable SHA-256 hashed gazettes, valuation records, title deeds, and digital consent forms.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold flex items-center gap-2 shadow-2xs btn-hover transition-colors cursor-pointer"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Certified Record</span>
        </button>
      </div>

      {/* Filter toolbar */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200/90 shadow-2xs">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search document, survey or gazette..."
              className="w-full pl-9 pr-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-700 focus:bg-white"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
            {['ALL', 'Gazette', 'Valuation', 'Title Deed', 'Consent Form', 'SIA & Consent'].map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedCategory === cat
                    ? 'bg-blue-700 text-white font-semibold shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Documents List */}
      <div className="space-y-3">
        {filteredDocs.length === 0 ? (
          <div className="p-10 rounded-2xl bg-white border border-slate-200 text-center text-slate-500">
            No matching documents found in repository.
          </div>
        ) : (
          filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-2xs hover:border-blue-300 card-hover transition-colors"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="font-mono text-xs text-blue-950 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {doc.id}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-[11px] text-slate-700 font-medium border border-slate-200">
                        {doc.category}
                      </span>
                      {doc.source === 'field' && (
                        <span className="px-2 py-0.5 rounded bg-emerald-50 text-[10px] text-emerald-800 font-bold border border-emerald-200">
                          Field Uploaded
                        </span>
                      )}
                      <span className="flex items-center gap-1 text-[11px] text-emerald-800 font-semibold">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                        SHA-256 Sealed
                      </span>
                    </div>
                    <h3 className="text-sm sm:text-base font-bold text-slate-900 mb-1">
                      {doc.title}
                    </h3>
                    <p className="text-xs text-slate-600">
                      Associated Entity: <span className="text-slate-900 font-medium">{doc.parcelOrProject}</span>
                    </p>
                    <p className="text-[10px] font-mono text-slate-400 mt-1 truncate max-w-md">{doc.hash}</p>
                  </div>
                </div>

                {/* Actions & Metadata */}
                <div className="flex items-center justify-between md:justify-end gap-3 pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
                  <div className="text-left md:text-right text-xs">
                    <span className="text-slate-500 block">{doc.date}</span>
                    <span className="font-mono text-slate-400 text-[11px]">{doc.size}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewDoc(doc)}
                      className="p-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 transition-colors shadow-2xs btn-hover cursor-pointer"
                      title="Preview Document"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDownload(doc)}
                      className="px-3 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-2xs btn-hover cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Upload Certified Record Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/50 backdrop-blur-xs animate-fade-in">
          <div className="max-w-lg w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-blue-50 text-blue-700">
                  <UploadCloud className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Upload Certified Statutory Record</h3>
                  <p className="text-xs text-slate-500">Document will be cryptographically hashed and sealed</p>
                </div>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Document Title / Description *
                </label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g., Certified 1-B Extract & Revenue Mutation Certificate"
                  required
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-blue-700 focus:bg-white"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-700 font-semibold mb-1">
                    Statutory Category *
                  </label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value as any)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-blue-700"
                  >
                    <option value="Title Deed">Title Deed / Pahani</option>
                    <option value="Valuation Report">Valuation Report</option>
                    <option value="Consent Form">Consent Form</option>
                    <option value="Identity Proof">Identity Proof</option>
                    <option value="Gazette Notification">Gazette Notification</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-700 font-semibold mb-1">
                    Target Land Parcel *
                  </label>
                  <select
                    value={uploadParcelId}
                    onChange={(e) => setUploadParcelId(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-blue-700"
                  >
                    {landParcels.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.surveyNumber} ({p.landownerName})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Mock File Selector */}
              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Attach Certified PDF / Scan (Up to 25 MB)
                </label>
                <label className="border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-50/50">
                  <FileText className="w-8 h-8 text-blue-600 mb-1" />
                  <span className="text-xs font-semibold text-slate-800">
                    {uploadFileName || 'Click to select certified PDF or drag and drop'}
                  </span>
                  <span className="text-[10px] text-slate-400 mt-0.5">
                    Supports PDF, DOCX, JPG, PNG with digital signature
                  </span>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.png,.jpg"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadFileName(e.target.files[0].name);
                      }
                    }}
                  />
                </label>
              </div>

              <div className="flex items-center gap-2 p-3 rounded-xl bg-blue-50/70 border border-blue-200 text-blue-900 text-[11px]">
                <ShieldCheck className="w-4 h-4 text-blue-700 shrink-0" />
                <span>Uploaded documents receive an automated SHA-256 ledger stamp and are backed up to NIC DigiLocker.</span>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-2xs btn-hover"
                >
                  Upload &amp; Seal Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/50 backdrop-blur-xs animate-fade-in">
          <div className="max-w-2xl w-full p-6 rounded-2xl bg-white border border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-emerald-50 text-emerald-700">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Certified Statutory Inspection</h3>
                  <span className="text-[10px] font-mono text-emerald-800 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    INTEGRITY SEAL VERIFIED
                  </span>
                </div>
              </div>
              <button
                onClick={() => setPreviewDoc(null)}
                className="text-slate-400 hover:text-slate-600 p-1 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 font-mono text-xs space-y-2">
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Document ID:</span>
                <span className="font-bold text-blue-900">{previewDoc.id}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Title:</span>
                <span className="font-bold text-slate-800 text-right max-w-sm">{previewDoc.title}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Category:</span>
                <span className="text-slate-900">{previewDoc.category}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Associated Parcel / Project:</span>
                <span className="text-blue-900 font-bold">{previewDoc.parcelOrProject}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Filing Date:</span>
                <span className="text-slate-700">{previewDoc.date}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-1.5">
                <span className="text-slate-500 font-sans">Cryptographic Checksum:</span>
                <span className="text-slate-600 text-[10px] break-all">{previewDoc.hash}</span>
              </div>
            </div>

            {/* Document Preview Certificate Box */}
            <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/40 text-xs space-y-2">
              <div className="flex items-center gap-2 font-bold text-emerald-900">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Statutory Authority Certification</span>
              </div>
              <p className="text-slate-700 leading-relaxed">
                This record has been officially gazetted and digitally counter-signed by the Competent Authority for Land Acquisition (CALA). It holds full evidentiary value under the Right to Fair Compensation and Transparency in Land Acquisition (RFCTLARR) Act, 2013 and Section 65B of the Indian Evidence Act.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                onClick={() => setPreviewDoc(null)}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 font-semibold text-xs cursor-pointer"
              >
                Close Preview
              </button>
              <button
                onClick={() => {
                  handleDownload(previewDoc);
                  setPreviewDoc(null);
                }}
                className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white font-bold text-xs shadow-2xs flex items-center gap-1.5 btn-hover cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Certified Copy</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
