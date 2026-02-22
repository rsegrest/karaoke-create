import { useEffect, useMemo, useRef, useState } from "react";
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
    const [activeLineIndex, setActiveLineIndex] = useState(0);

    const audioRef = useRef<HTMLAudioElement>(null);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const activeLineRef = useRef<HTMLDivElement>(null);

    const [micStream, setMicStream] = useState<MediaStream | null>(null);
    const micAudioRef = useRef<HTMLAudioElement>(null);

    // Microphone setup
    useEffect(() => {
        let activeStream: MediaStream | null = null;

        if (isRecording) {
            navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true, // Prevents crazy feedback when singing into speakers
                    noiseSuppression: true,
                    autoGainControl: true,
                }
            })
                .then(stream => {
                    activeStream = stream;
                    setMicStream(stream);
                })
                .catch(err => {
                    console.error("Microphone access denied or error:", err);
                });
        }

        return () => {
            if (activeStream) {
                activeStream.getTracks().forEach(track => track.stop());
            }
        };
    }, [isRecording]);

    // Attach stream to audio element
    useEffect(() => {
        if (micAudioRef.current && micStream) {
            micAudioRef.current.srcObject = micStream;
        }
    }, [micStream]);

    // Build display lines: use lyricsText phrases (if available) with timing from lyricsData
    // Each entry has { time, text, words: [{ text, time }] } for word-level highlighting
    const lyrics = useMemo(() => {
        const timingData = lyricsData || DEMO_LYRICS;

        if (!lyricsText) {
            // No phrase text — fall back to word-by-word timing data, each word as its own phrase
            return timingData.map(entry => ({
                time: entry.time,
                text: entry.text,
                words: [{ text: entry.text, time: entry.time }]
            }));
        }

        const phraseLines = lyricsText.split('\n').filter(line => line.trim());

        // Walk through the word-level timing data to assign timings to each phrase and its words
        let wordIdx = 0;
        return phraseLines.map(line => {
            const trimmedLine = line.trim();
            // Split line into display words (preserving punctuation attached to words)
            const displayWords = trimmedLine.split(/\s+/).filter(w => w);

            // Match each display word to its timing entry
            const words: { text: string; time: number }[] = [];
            let phraseTime = wordIdx < timingData.length ? timingData[wordIdx].time : 0;
            let foundFirst = false;

            for (const dw of displayWords) {
                const cleanDW = dw.replace(/[,.;?!]/g, '').toLowerCase();
                let matched = false;
                for (let i = wordIdx; i < timingData.length; i++) {
                    const entryWord = timingData[i].text.replace(/[,.;?!]/g, '').toLowerCase();
                    if (entryWord === cleanDW) {
                        if (!foundFirst) {
                            phraseTime = timingData[i].time;
                            foundFirst = true;
                        }
                        words.push({ text: dw, time: timingData[i].time });
                        wordIdx = i + 1;
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    // No timing match found — use last known time
                    words.push({ text: dw, time: words.length > 0 ? words[words.length - 1].time : phraseTime });
                }
            }

            return { time: phraseTime, text: trimmedLine, words };
        });
    }, [lyricsText, lyricsData]);

    // Determine the currently active word index within lyricsData based on currentTime
    const activeWordTime = useMemo(() => {
        const timingData = lyricsData || DEMO_LYRICS;
        // Find the last word whose time <= currentTime
        let lastTime = -1;
        for (let i = timingData.length - 1; i >= 0; i--) {
            if (currentTime >= timingData[i].time) {
                lastTime = timingData[i].time;
                break;
            }
        }
        return lastTime;
    }, [currentTime, lyricsData]);

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

            {/* Mic Playback Element (Hidden) */}
            {isRecording && (
                <audio
                    ref={micAudioRef}
                    autoPlay
                    muted={false} // Hear through speakers!
                />
            )}

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
                                    {isActive && line.words ? (
                                        line.words.map((word, wIdx) => {
                                            const isWordActive = activeWordTime >= word.time &&
                                                (wIdx === line.words.length - 1 || activeWordTime < line.words[wIdx + 1].time);
                                            const isWordPast = activeWordTime > word.time &&
                                                wIdx < line.words.length - 1 && activeWordTime >= line.words[wIdx + 1].time;
                                            return (
                                                <span
                                                    key={wIdx}
                                                    className={`transition-colors duration-150 ${isWordActive
                                                        ? 'text-sky-400 drop-shadow-[0_0_12px_rgba(56,189,248,0.8)]'
                                                        : isWordPast
                                                            ? 'text-slate-300'
                                                            : 'text-white'
                                                        }`}
                                                >
                                                    {word.text}{wIdx < line.words.length - 1 ? ' ' : ''}
                                                </span>
                                            );
                                        })
                                    ) : (
                                        line.text
                                    )}
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