import { useState } from 'react';
import AbstractBackground from './components/AbstractBackground';
import SetupScreen from './components/SetupScreen';
import ProcessingScreen from './components/ProcessingScreen';
import KaraokeScreen from './components/KaraokeScreen';
import SplashPage from './components/SplashPage';
import Repertoire from './components/Repertoire';
import './karaoke.css';

// --- MAIN APP COMPONENT ---

export default function App() {
  const PROXY_SERVER_URL = import.meta.env.VITE_QUEUEING_PROXY_URL;
  const [appState, setAppState] = useState('setup'); // 'splash' | 'setup' | 'repertoire' | 'processing' | 'karaoke'
  const [songTitle, setSongTitle] = useState('');
  const [artist, setArtist] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [lyricsData, setLyricsData] = useState<{ time: number, text: string }[] | null>(null);
  const [lyricsText, setLyricsText] = useState<string | null>(null);

  const startProcessing = () => {
    setAppState('processing');
  };

  const finishProcessing = (data: any) => {
    if (data.lyrics_json) {
      const parsed = typeof data.lyrics_json === 'string' ? JSON.parse(data.lyrics_json) : data.lyrics_json;
      const mappedLyrics = parsed.map((item: any) => ({
        time: item.start !== undefined ? item.start : item.time,
        text: item.text
      }));
      setLyricsData(mappedLyrics);
    }
    if (data.lyrics_text) {
      setLyricsText(data.lyrics_text);
    }
    setAudioUrl(`${PROXY_SERVER_URL}/stream_audio?song_id=${data.song_id}&type=instrumental`);
    setFile(null); // Clear raw file, we will use the processed audioUrl!
    setAppState('karaoke');
  };

  const handleProcessingError = (err: string) => {
    alert("Error processing song: " + err);
    setAppState('setup');
  };

  const resetApp = () => {
    if (appState === 'karaoke' && !window.confirm("Exit session? Your progress will be lost.")) {
      return;
    }
    setFile(null);
    setAudioUrl(null);
    setLyricsData(null);
    setLyricsText(null);
    setSongTitle('');
    setIsRecording(false);
    setAppState('splash');
  };

  const handlePlayFromRepertoire = async (songId: number) => {
    try {
      const resp = await fetch(`${PROXY_SERVER_URL}/get_song_data?song_id=${songId}`);
      if (!resp.ok) throw new Error("Failed to load song data");
      const data = await resp.json();

      setSongTitle(data.song_title);
      setArtist(data.original_artist);
      setAudioUrl(`${PROXY_SERVER_URL}/stream_audio?song_id=${songId}&type=instrumental`);
      if (data.lyrics_json) {
        const parsed = typeof data.lyrics_json === 'string' ? JSON.parse(data.lyrics_json) : data.lyrics_json;
        const mappedLyrics = parsed.map((item: any) => ({
          time: item.start !== undefined ? item.start : item.time,
          text: item.text
        }));
        setLyricsData(mappedLyrics);
      } else {
        setLyricsData(null);
      }
      if (data.lyrics_text) {
        setLyricsText(data.lyrics_text);
      } else {
        setLyricsText(null);
      }
      setFile(null); // Clear file so it prefers audioUrl
      setAppState('karaoke');
    } catch (err) {
      alert("Could not load song for playback.");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 font-sans selection:bg-pink-500 selection:text-white overflow-hidden">
      {/* Global Background */}
      <AbstractBackground active={appState === 'karaoke'} />

      {/* View Switcher */}
      {appState === 'splash' && (
        <SplashPage onNavigate={(view) => setAppState(view)} />
      )}

      {appState === 'setup' && (
        <div className="relative z-10 p-4">
          <button
            onClick={() => setAppState('splash')}
            className="text-gray-400 hover:text-white mb-4 flex items-center gap-2 transition-colors"
          >
            ← Back to Home
          </button>
          <SetupScreen
            onStart={startProcessing}
            songTitle={songTitle}
            setSongTitle={setSongTitle}
            artist={artist}
            setArtist={setArtist}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
            file={file}
            setFile={setFile}
          />
        </div>
      )}

      {appState === 'repertoire' && (
        <Repertoire
          onBack={() => setAppState('splash')}
          onPlaySong={handlePlayFromRepertoire}
        />
      )}

      {appState === 'processing' && file && (
        <ProcessingScreen
          file={file}
          songTitle={songTitle}
          artist={artist}
          onComplete={finishProcessing}
          onError={handleProcessingError}
        />
      )}

      {appState === 'karaoke' && (
        <KaraokeScreen
          accompanymentFile={file}
          audioUrl={audioUrl}
          lyricsData={lyricsData}
          lyricsText={lyricsText}
          songTitle={songTitle || "Unknown Track"}
          artist={artist || "Unknown Artist"}
          isRecording={isRecording}
          onExit={resetApp}
        />
      )}
    </div>
  );
}