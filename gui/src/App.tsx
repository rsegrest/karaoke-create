import { useState } from 'react';
import AbstractBackground from './components/AbstractBackground';
import SetupScreen from './components/SetupScreen';
import ProcessingScreen from './components/ProcessingScreen';
import KaraokeScreen from './components/KaraokeScreen';
import './karaoke.css';

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
    <div className="min-h-screen bg-slate-950 font-sans selection:bg-pink-500 selection:text-white overflow-hidden">
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
    </div>
  );
}