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
  ArrowLeft,
  Landmark,
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

  // Forgot Password state
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
      showToast('Please enter your username or email', 'warning');
      return;
    }
    if (!password.trim()) {
      showToast('Please enter your password', 'warning');
      return;
    }

    setIsLoading(true);
    loginAsSector(selectedSector, username);
    setIsLoading(false);
  };

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotContact.trim()) {
      showToast('Please enter your registered email or mobile number', 'warning');
      return;
    }
    setForgotStep('verify');
    setOtpCode('849201'); // Pre-fill demo helper
    showToast('Verification code sent. (Demo OTP: 849201)', 'info');
  };

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode !== '849201' && otpCode.length < 6) {
      showToast('Invalid verification code. Please enter 849201', 'danger');
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
    setForgotContact('');
    setOtpCode('');
    setNewPassword('');
    setConfirmPassword('');
    showToast('Password reset successfully. You can now sign in.', 'success');
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
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-6 px-4">
      {/* Return back button */}
      <div className="w-full max-w-xl mb-4 flex items-center justify-between">
        <button
          onClick={() => setCurrentView('landing')}
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to BhoomiSetu Homepage</span>
        </button>
        <span className="text-[11px] text-slate-500 font-medium">
          Official Government Portal
        </span>
      </div>

      {/* Main Login Card in Clean White & Slate-50 */}
      <div className="w-full max-w-xl bg-white border border-slate-200/90 rounded-2xl shadow-xs overflow-hidden">
        {/* Header bar */}
        <div className="p-6 sm:p-8 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-900 text-white flex items-center justify-center shadow-xs">
              <Landmark className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                Sector Official Sign In
              </h1>
              <p className="text-xs text-slate-500 mt-0.5 font-medium">
                BhoomiSetu National Land Acquisition & Management Portal
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 sm:p-8 space-y-6">
          {/* Step 1: Select Sector */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 block">
              1. Select Your Infrastructure / Administrative Sector
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {(['highways', 'railways', 'power', 'urban', 'revenue', 'citizen'] as SectorType[]).map((secKey) => {
                const sec = SECTORS_CONFIG[secKey];
                const Icon = getSectorIcon(secKey);
                const isSelected = selectedSector === secKey;

                return (
                  <button
                    key={secKey}
                    type="button"
                    onClick={() => {
                      setSelectedSector(secKey);
                      setActiveSector(secKey);
                    }}
                    className={`p-2.5 rounded-xl border text-left flex items-center gap-2.5 transition-all ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/70 text-blue-950 ring-1 ring-blue-600 font-bold shadow-2xs'
                        : 'border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                        isSelected ? 'bg-blue-700 text-white' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="min-w-0">
                      <span className="text-xs font-bold block truncate">{sec.shortName}</span>
                      <span className="text-[10px] text-slate-500 block truncate">{sec.badge}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Active Sector Summary Pill */}
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center gap-3 text-xs">
            <SectorIcon className="w-5 h-5 text-blue-700 shrink-0" />
            <div className="min-w-0 flex-1">
              <span className="font-bold text-slate-900 block">{currentSectorConfig.name}</span>
              <span className="text-[11px] text-slate-500 block truncate">
                {currentSectorConfig.department}
              </span>
            </div>
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-900 font-bold text-[10px] shrink-0 border border-blue-200">
              {currentSectorConfig.badge}
            </span>
          </div>

          {/* Step 2: Username & Password Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 block">
                Official Username or Email
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. officer.nhai@nic.in"
                  className="w-full pl-9 pr-3 py-2.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-700 block">
                  Password
                </label>
                {/* Forgot password button prominently highlighted */}
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  id="forgot-password-link"
                  className="text-xs font-bold text-blue-700 hover:text-blue-800 hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your security password"
                  className="w-full pl-9 pr-10 py-2.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Quick 1-Click Demo Credentials Pill */}
            <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs flex items-center justify-between gap-2">
              <span className="text-[11px] text-slate-500">
                Demo: <strong>{currentSectorConfig.demoUsername}</strong> / <strong>{currentSectorConfig.demoPassword}</strong>
              </span>
              <button
                type="button"
                onClick={() => {
                  setUsername(currentSectorConfig.demoUsername);
                  setPassword(currentSectorConfig.demoPassword);
                  showToast('Pre-filled test credentials', 'info');
                }}
                className="text-[11px] font-bold text-blue-700 hover:underline shrink-0"
              >
                Auto-fill
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              id="login-submit-btn"
              disabled={isLoading}
              className="w-full py-2.5 px-4 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs shadow-2xs transition-all flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span>Authenticating with BhoomiSetu...</span>
              ) : (
                <>
                  <Lock className="w-3.5 h-3.5" />
                  <span>Sign In to {currentSectorConfig.shortName} Dashboard</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Interactive Forgot Password Modal in Clean Light Theme */}
      {showForgotPassword && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 max-w-md w-full shadow-lg space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <KeyRound className="w-4 h-4 text-blue-700" />
                <h3 className="text-sm font-bold text-slate-900">
                  Password Recovery: {currentSectorConfig.shortName}
                </h3>
              </div>
              <button
                onClick={() => {
                  setShowForgotPassword(false);
                  setForgotStep('request');
                }}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {forgotStep === 'request' ? (
              <form onSubmit={handleSendOtp} className="space-y-3">
                <p className="text-xs text-slate-600 leading-relaxed">
                  Enter your registered official email or mobile number linked to the{' '}
                  <strong className="text-slate-900">{currentSectorConfig.name}</strong> portal.
                </p>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-700">
                    Official Email / Mobile
                  </label>
                  <input
                    type="text"
                    value={forgotContact}
                    onChange={(e) => setForgotContact(e.target.value)}
                    placeholder="e.g. officer.nhai@nic.in or 9876543210"
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600"
                    required
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(false)}
                    className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 hover:bg-slate-50 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs transition-colors shadow-2xs"
                  >
                    Send OTP Code
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-3">
                <div className="p-2.5 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-900">
                  OTP sent to <strong>{forgotContact}</strong>. Use demo OTP code: <strong>849201</strong>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-700">
                    Enter 6-Digit OTP Code
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value)}
                      placeholder="849201"
                      maxLength={6}
                      className="flex-1 px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs font-mono text-slate-900 focus:outline-none focus:border-blue-600"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setOtpCode('849201')}
                      className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs rounded-lg border border-slate-300 font-medium"
                    >
                      Fill Demo OTP
                    </button>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-700">
                    New Security Password
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-blue-600"
                    required
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-700">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-type new password"
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-blue-600"
                    required
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setForgotStep('request')}
                    className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-700 hover:bg-slate-50 font-medium"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-1.5 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-semibold text-xs transition-colors shadow-2xs"
                  >
                    Reset & Apply Password
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
