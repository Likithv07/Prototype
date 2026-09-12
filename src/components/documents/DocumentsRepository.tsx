import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import {
  FileText,
  Search,
  UploadCloud,
  Download,
  Eye,
  ShieldCheck,
} from 'lucide-react';

export const DocumentsRepository: React.FC = () => {
  const { showToast } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const documents = [
    {
      id: 'DOC-2026-0814',
      title: 'Gazette Notification Section 3D (Declaration of Acquisition)',
      category: 'Gazette',
      parcelOrProject: 'NLA-TS-2026-001 (NH-65 Corridor)',
      date: '02 Mar 2026',
      size: '3.8 MB',
      verified: true,
      hash: 'sha256: 7f8a192bc93214589dfbe76a1004cd821a81...',
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
    },
  ];

  const filteredDocs = documents.filter((doc) => {
    const matchSearch =
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.parcelOrProject.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = selectedCategory === 'ALL' || doc.category === selectedCategory;
    return matchSearch && matchCat;
  });

  return (
    <div className="space-y-6 pb-16">
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
          onClick={() => showToast('Opened Document Upload & DigiLocker Gateway', 'info')}
          className="px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-xs font-semibold flex items-center gap-2 shadow-2xs transition-colors"
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
                    ? 'bg-blue-700 text-white font-semibold'
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
        {filteredDocs.map((doc) => (
          <div key={doc.id} className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-2xs hover:border-blue-300 transition-colors">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="p-3 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-xs text-blue-950 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                      {doc.id}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-[11px] text-slate-700 font-medium border border-slate-200">
                      {doc.category}
                    </span>
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
                  <p className="text-[10px] font-mono text-slate-400 mt-1">{doc.hash}</p>
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
                    onClick={() => showToast(`Opening certified viewer for ${doc.id}`, 'info')}
                    className="p-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 transition-colors shadow-2xs"
                    title="Preview Document"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => showToast(`Downloaded certified copy of ${doc.title}`, 'success')}
                    className="px-3 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-200 text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-2xs"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
