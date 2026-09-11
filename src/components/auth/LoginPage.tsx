import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { SectorType } from '../../types';
import { SECTORS_CONFIG } from '../../data/sectorData';
import {
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  Building,
  Zap,
  Train,
  Truck,
  UserCheck,
  Layers,
  KeyRound,
  CheckCircle2,
  X,
  AlertCircle,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';

export const LoginPage: React.FC = () => {
  const {
    activeSector,
    setActiveSector,
    loginAsSector,
    setCurrentView,
    showToast,
  } = useApp();

  const [selectedSector, setSelectedSector] = useState<SectorType>(activeSector || 'highways');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Forgot Password modal state
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotStep, setForgotStep] = useState<'request' | 'verify'>('request');
  const [forgotContact, setForgotContact] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const currentSectorConfig = SECTORS_CONFIG[selectedSector];

  // Sync inputs when sector changes
  useEffect(() => {
    if (currentSectorConfig) {
      setUsername(currentSectorConfig.demoUsername);
      setPassword(currentSectorConfig.demoPassword);
    }
  }, [selectedSector]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      showToast('Please enter your username or official email', 'warning');
      return;
    }
    if (!password.trim()) {
      showToast('Please enter your password', 'warning');
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      loginAsSector(selectedSector, username);
    }, 450);
  };

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotContact.trim()) {
      showToast('Please enter your registered email or mobile number', 'warning');
      return;
    }
    setForgotStep('verify');
    setOtpCode('849201'); // Pre-fill or demo helper
    showToast('Verification code dispatched. (Demo Code: 849201)', 'info');
  };

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode !== '849201' && otpCode.length < 6) {
      showToast('Invalid verification code', 'danger');
      return;
    }
    if (!newPassword || newPassword.length < 6) {
      showToast('Password must be at least 6 characters', 'warning');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('Passwords do not match', 'warning');
      return;
    }

    setPassword(newPassword);
    setShowForgotPassword(false);
    setForgotStep('request');
    showToast('Password reset successfully! Logging you in...', 'success');
    loginAsSector(selectedSector, username || forgotContact);
  };

  const getSectorIcon = (sec: SectorType) => {
    switch (sec) {
      case 'highways':
        return Truck;
      case 'railways':
        return Train;
      case 'power':
        return Zap;
      case 'urban':
        return Building;
      case 'revenue':
        return ShieldCheck;
      case 'citizen':
        return UserCheck;
      default:
        return Layers;
    }
  };

  const SectorIcon = getSectorIcon(selectedSector);

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 py-8 max-w-2xl mx-auto">
      {/* Back to Home Link */}
      <div className="w-full mb-4 flex items-center justify-between">
        <button
          onClick={() => setCurrentView('landing')}
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to BhoomiSetu Home</span>
        </button>
        <span className="text-[11px] text-slate-400 font-mono">
          BhoomiSetu v2.6 • RFCTLARR 2013
        </span>
      </div>

      {/* Main Minimal Login Card */}
      <div className="w-full bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-sm backdrop-blur-sm">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
              <SectorIcon className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">
                Sector Portal Login
              </h1>
              <p className="text-xs text-slate-400">
                Authenticate to access your sector-specific land acquisition console
              </p>
            </div>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-400 border border-slate-700">
            {currentSectorConfig.badge}
          </span>
        </div>

        {/* 1. Sector Selector */}
        <div className="mb-6 space-y-2">
          <label className="text-xs font-semibold text-slate-300 block">
            Select Infrastructure / Administrative Sector
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {(['highways', 'railways', 'power', 'urban', 'revenue', 'citizen'] as SectorType[]).map((secKey) => {
              const item = SECTORS_CONFIG[secKey];
              const isSelected = selectedSector === secKey;
              const IconComp = getSectorIcon(secKey);
              return (
                <button
                  key={secKey}
                  type="button"
                  id={`login-select-sector-${secKey}`}
                  onClick={() => setSelectedSector(secKey)}
                  className={`p-2.5 rounded-lg text-left transition-all border flex items-center gap-2 ${
                    isSelected
                      ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <IconComp className="w-4 h-4 shrink-0" />
                  <span className="text-xs font-medium truncate">{item.shortName}</span>
                </button>
              );
            })}
          </div>
          <p className="text-[11px] text-slate-400 pt-0.5">
            {currentSectorConfig.department}
          </p>
        </div>

        {/* 2. Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          {/* Username */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">
              Official Username / Email ID
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type="text"
                id="login-username-input"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="officer.id@gov.in"
                className="w-full pl-9 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-slate-300 block">
                Password
              </label>
              {/* Highlighted Forgot Password Button */}
              <button
                type="button"
                id="forgot-password-btn"
                onClick={() => {
                  setForgotContact(username);
                  setShowForgotPassword(true);
                }}
                className="text-xs font-medium text-emerald-400 hover:text-emerald-300 hover:underline transition-colors"
              >
                Forgot Password?
              </button>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                id="login-password-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-9 pr-10 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Quick 1-Click Demo Helper Bar */}
          <div className="pt-2">
            <span className="text-[11px] text-slate-400 block mb-1.5 font-medium">
              Quick demo authentication:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {(['highways', 'railways', 'power', 'urban', 'revenue', 'citizen'] as SectorType[]).map((secKey) => (
                <button
                  key={secKey}
                  type="button"
                  onClick={() => {
                    setSelectedSector(secKey);
                    loginAsSector(secKey, SECTORS_CONFIG[secKey].demoUsername);
                  }}
                  className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-[10px] font-medium border border-slate-700 transition-colors"
                >
                  {SECTORS_CONFIG[secKey].shortName}
                </button>
              ))}
            </div>
          </div>

          {/* Primary Submit Button */}
          <button
            type="submit"
            id="login-submit-btn"
            disabled={isLoading}
            className="mt-4 w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs shadow-sm transition-all flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <span>Authenticating Session...</span>
            ) : (
              <>
                <span>Log In to {currentSectorConfig.shortName} Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm font-bold text-white">
                  Reset Sector Account Password
                </h2>
              </div>
              <button
                onClick={() => setShowForgotPassword(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {forgotStep === 'request' ? (
              <form onSubmit={handleSendOtp} className="space-y-3 text-xs">
                <p className="text-slate-300">
                  Enter your registered official email or mobile number for{' '}
                  <strong className="text-emerald-400">{currentSectorConfig.name}</strong> to receive a statutory verification code.
                </p>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Registered Email / Mobile</label>
                  <input
                    type="text"
                    value={forgotContact}
                    onChange={(e) => setForgotContact(e.target.value)}
                    placeholder="officer.nhai@morth.gov.in"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-xs text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(false)}
                    className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                  >
                    Send Verification Code
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-3 text-xs">
                <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[11px]">
                  Verification code sent to <strong>{forgotContact}</strong>.
                  <span className="block mt-0.5 text-slate-400">Demo Code: <strong>849201</strong></span>
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">6-Digit Verification Code</label>
                  <input
                    type="text"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    placeholder="849201"
                    maxLength={6}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded font-mono text-center tracking-widest text-sm text-emerald-400 focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">New Password</label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Min. 6 characters"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-xs text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="font-semibold text-slate-300">Confirm New Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat password"
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-xs text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setForgotStep('request')}
                    className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium"
                  >
                    Reset & Sign In
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
