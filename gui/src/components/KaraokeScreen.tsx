import { useEffect, useRef, useState } from "react";
import DEMO_LYRICS from "../assets/demoLyrics";
import { ChevronLeft, Pause, Play } from "lucide-react";
import '../karaoke.css';

// 3. KARAOKE SCREEN
export const KaraokeScreen = ({
    accompanymentFile,
    songTitle,
    artist,
    isRecording,
    audioUrl,
    lyricsData,
    lyricsText,
    onExit
}: {
    accompanymentFile: File | null;
    songTitle: string | null;
    artist: string | null;
    isRecording: boolean;
    audioUrl?: string | null;
    lyricsData?: { time: number, text: string }[] | null;
    lyricsText?: string | null;
    onExit: () => void;
}) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const lyrics = lyricsData || DEMO_LYRICS;
    const [activeLineIndex, setActiveLineIndex] = useState(0);

    const audioRef = useRef(null);
    const scrollContainerRef = useRef(null);
    const activeLineRef = useRef(null);

    // Load audio on mount
    useEffect(() => {
        if (accompanymentFile && audioRef.current as any) {
            const url = URL.createObjectURL(accompanymentFile);
            (audioRef.current as any).src = url;
            return () => URL.revokeObjectURL(url);
        } else if (audioUrl && audioRef.current as any) {
            (audioRef.current as any).src = audioUrl;
        }
    }, [accompanymentFile, audioUrl]);

    // Sync active line index
    useEffect(() => {
        // Find the last line where time <= currentTime
        const index = lyrics.reduce((acc: number, line: { time: number; text: string }, idx: number) => {
            return currentTime >= line.time ? idx : acc;
        }, 0);
        setActiveLineIndex(index);
    }, [currentTime, lyrics]);

    // Auto-scroll logic
    useEffect(() => {
        if (activeLineRef.current) {
            (activeLineRef.current as any).scrollIntoView({
                behavior: 'smooth',
                block: 'center',
            });
        }
    }, [activeLineIndex]);

    const togglePlay = () => {
        if (audioRef.current) {
            if (isPlaying) {
                (audioRef.current as any).pause();
            } else {
                (audioRef.current as any).play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime((audioRef.current as any).currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setDuration((audioRef.current as any).duration);
            // Auto-play when ready
            (audioRef.current as any).play().then(() => setIsPlaying(true)).catch(() => { });
        }
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        const time = parseFloat(e.target.value);
        if (audioRef.current) {
            (audioRef.current as any).currentTime = time;
            setCurrentTime(time);
        }
    };

    const formatTime = (time: number) => {
        const min = Math.floor(time / 60);
        const sec = Math.floor(time % 60);
        return `${min}:${sec < 10 ? '0' : ''}${sec}`;
    };

    return (
        <div className="relative z-10 flex flex-col h-screen w-full">
            {/* Audio Element (Hidden) */}
            <audio
                ref={audioRef}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={() => setIsPlaying(false)}
            />

            {/* Header */}
            <div className="flex items-center justify-between p-6 bg-gradient-to-b from-black/80 to-transparent">
                <button
                    onClick={onExit}
                    className="p-3 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors backdrop-blur-md"
                >
                    <ChevronLeft size={28} />
                </button>
                <div className="text-center">
                    <h2 className="text-2xl md:text-3xl font-bold text-white tracking-wide shadow-black drop-shadow-md">{songTitle}</h2>
                    <p className="text-sm font-medium text-slate-300 tracking-wider shadow-black drop-shadow-sm mb-1">{artist}</p>
                    {isRecording && (
                        <div className="flex items-center justify-center gap-2 mt-1">
                            <span className="animate-pulse w-3 h-3 rounded-full bg-red-500"></span>
                            <span className="text-xs font-medium text-red-400 uppercase tracking-widest">Recording</span>
                        </div>
                    )}
                </div>
                <div className="w-12"></div> {/* Spacer for alignment */}
            </div>

            {/* Lyrics Area */}
            <div className="flex-1 overflow-hidden relative group">
                <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-slate-900 to-transparent z-10 pointer-events-none"></div>
                <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-slate-900 to-transparent z-10 pointer-events-none"></div>

                <div
                    ref={scrollContainerRef}
                    className="h-full overflow-y-auto px-4 py-[50vh] scroll-smooth no-scrollbar flex flex-col gap-8 text-center"
                    style={{ scrollBehavior: 'smooth' }}
                >
                    {lyrics.map((line, idx) => {
                        const isActive = idx === activeLineIndex;
                        const isPast = idx < activeLineIndex;

                        return (
                            <div
                                key={idx}
                                ref={isActive ? activeLineRef : null}
                                className={`transition-all duration-500 ease-out transform
                  ${isActive ? 'scale-110 opacity-100 blur-none' : 'scale-95 opacity-30 blur-[1px]'}
                  ${isPast ? 'opacity-20' : ''}
                `}
                            >
                                <p className={`font-bold font-sans tracking-tight leading-tight transition-colors duration-300
                    ${isActive ? 'text-4xl md:text-6xl text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.5)]' : 'text-2xl md:text-4xl text-slate-400'}
                `}>
                                    {line.text}
                                </p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Controls */}
            <div className="p-8 pb-12 bg-gradient-to-t from-slate-950 via-slate-900 to-transparent">
                <div className="max-w-4xl mx-auto w-full">
                    {/* Progress Bar */}
                    <div className="flex items-center gap-4 mb-6 text-slate-400 font-mono text-sm">
                        <span>{formatTime(currentTime)}</span>
                        <input
                            type="range"
                            min="0"
                            max={duration || 100}
                            value={currentTime}
                            onChange={handleSeek}
                            className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-pink-500"
                        />
                        <span>{formatTime(duration)}</span>
                    </div>

                    {/* Main Controls */}
                    <div className="flex items-center justify-center gap-10">
                        {/* Rewind 10s */}
                        <button
                            onClick={() => {
                                if (audioRef.current) (audioRef.current as any).currentTime -= 10;
                            }}
                            className="text-slate-400 hover:text-white transition-colors"
                        >
                            <span className="text-xs font-bold">-10s</span>
                        </button>

                        <button
                            onClick={togglePlay}
                            className={`w-24 h-24 rounded-full flex items-center justify-center shadow-2xl transition-all transform hover:scale-105 active:scale-95
                ${isPlaying
                                    ? 'bg-slate-800 text-white border border-slate-600 shadow-slate-900/50'
                                    : 'bg-gradient-to-tr from-pink-500 to-purple-600 text-white shadow-purple-500/40 border border-white/10 animate-pulse-slow'}
              `}
                        >
                            {isPlaying ? (
                                <Pause size={40} fill="currentColor" />
                            ) : (
                                <Play size={40} fill="currentColor" className="ml-2" />
                            )}
                        </button>

                        {/* Skip 10s */}
                        <button
                            onClick={() => {
                                if (audioRef.current) (audioRef.current as any).currentTime += 10;
                            }}
                            className="text-slate-400 hover:text-white transition-colors"
                        >
                            <span className="text-xs font-bold">+10s</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default KaraokeScreen;