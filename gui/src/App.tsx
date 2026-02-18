import React, { useState } from 'react';
import AbstractBackground from './components/AbstractBackground';
import SetupScreen from './components/SetupScreen';
import ProcessingScreen from './components/ProcessingScreen';
import KaraokeScreen from './components/KaraokeScreen';

// --- MAIN APP COMPONENT ---

export default function App() {
  const [appState, setAppState] = useState('setup'); // 'setup' | 'processing' | 'karaoke'
  const [songTitle, setSongTitle] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [file, setFile] = useState(null);

  const startProcessing = () => {
    setAppState('processing');
  };

  const finishProcessing = () => {
    setAppState('karaoke');
  };

  const resetApp = () => {
    if (window.confirm("Exit session? Your settings will be lost.")) {
      setFile(null);
      setSongTitle('');
      setIsRecording(false);
      setAppState('setup');
    }
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 font-sans selection:bg-pink-500 selection:text-white overflow-hidden">
      {/* Global Background */}
      <AbstractBackground active={appState === 'karaoke'} />

      {/* View Switcher */}
      {appState === 'setup' && (
        <SetupScreen
          onStart={startProcessing}
          songTitle={songTitle}
          setSongTitle={setSongTitle}
          isRecording={isRecording}
          setIsRecording={setIsRecording}
          file={file}
          setFile={setFile}
        />
      )}

      {appState === 'processing' && (
        <ProcessingScreen onComplete={finishProcessing} />
      )}

      {appState === 'karaoke' && (
        <KaraokeScreen
          file={file}
          songTitle={songTitle || "Unknown Track"}
          isRecording={isRecording}
          onExit={resetApp}
        />
      )}

      {/* CSS Globals for specific animations */}
      <style>{`
        @keyframes gradient-xy {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-gradient-xy {
          background-size: 200% 200%;
          animation: gradient-xy 15s ease infinite;
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animate-pulse-slow {
            animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        /* Hide scrollbar for lyrics but keep functionality */
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}