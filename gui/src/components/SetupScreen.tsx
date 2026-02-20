import { Mic, Music, Upload } from "lucide-react";
import { useState } from "react";
import '../karaoke.css';
// 2. SETUP SCREEN
export const SetupScreen = ({
    onStart,
    artist,
    setArtist,
    songTitle,
    setSongTitle,
    isRecording,
    setIsRecording,
    file,
    setFile
}: {
    onStart: () => void;
    songTitle: string;
    setSongTitle: (title: string) => void;
    artist: string;
    setArtist: (title: string) => void;
    isRecording: boolean;
    setIsRecording: (recording: boolean) => void;
    file: File | null;
    setFile: (file: any) => void;
}) => {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.type.startsWith('audio/')) {
                setFile(droppedFile);
                if (!songTitle) {
                    // Remove extension for title
                    setSongTitle(droppedFile.name.replace(/\.[^/.]+$/, ""));
                }
            } else {
                alert("Please upload an audio file.");
            }
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            if (!songTitle) {
                setSongTitle(selectedFile.name.replace(/\.[^/.]+$/, ""));
            }
        }
    };

    return (
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-6 text-white w-full max-w-4xl mx-auto">
            <div className="mb-8 text-center">
                <h1 className="text-5xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-pink-400 to-purple-400 mb-2">
                    KaraokeFlow
                </h1>
                <p className="text-slate-400 text-lg">AI-Powered Vocal Removal & Lyrics</p>
            </div>

            <div className="w-full bg-slate-800/50 backdrop-blur-xl border border-slate-700 rounded-3xl p-8 shadow-2xl">
                {/* Upload Area */}
                <div
                    className={`relative group border-4 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer
            ${isDragging ? 'border-pink-500 bg-slate-700/50' : 'border-slate-600 hover:border-slate-500 hover:bg-slate-700/30'}
            ${file ? 'border-green-500/50 bg-green-500/10' : ''}
          `}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('fileInput')?.click()}
                >
                    <input
                        id="fileInput"
                        type="file"
                        accept="audio/*"
                        className="hidden"
                        onChange={handleFileSelect}
                    />

                    <div className="flex flex-col items-center gap-4">
                        {file ? (
                            <>
                                <div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/30">
                                    <Music size={40} className="text-white" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-white">{file.name}</h3>
                                    <p className="text-green-400">Ready for processing</p>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="w-20 h-20 rounded-full bg-slate-700 group-hover:bg-slate-600 flex items-center justify-center transition-colors">
                                    <Upload size={32} className="text-slate-300" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-semibold text-slate-200">Drop your song here</h3>
                                    <p className="text-slate-400">or click to browse files</p>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Settings */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Song Title</label>
                        <input
                            type="text"
                            value={songTitle}
                            onChange={(e) => setSongTitle(e.target.value)}
                            placeholder={file ? "Enter song title..." : "Waiting for file..."}
                            className="bg-slate-900/80 border border-slate-700 rounded-xl px-4 py-3 text-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 transition-all placeholder-slate-600"
                        />
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Artist</label>
                        <input
                            type="text"
                            value={artist}
                            onChange={(e) => setArtist(e.target.value)}
                            placeholder={file ? "Enter original artist..." : "Waiting for file..."}
                            className="bg-slate-900/80 border border-slate-700 rounded-xl px-4 py-3 text-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500 transition-all placeholder-slate-600"
                        />
                    </div>
                </div>

                {/* Settings */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Options</label>
                        <div
                            className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${isRecording ? 'bg-red-500/20 border-red-500/50' : 'bg-slate-900/80 border-slate-700'}`}
                            onClick={() => setIsRecording(!isRecording)}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-full ${isRecording ? 'bg-red-500' : 'bg-slate-700'}`}>
                                    <Mic size={20} className="text-white" />
                                </div>
                                <span className={`font-medium ${isRecording ? 'text-red-400' : 'text-slate-300'}`}>
                                    Record Performance
                                </span>
                            </div>
                            <div className={`w-12 h-6 rounded-full p-1 transition-colors ${isRecording ? 'bg-red-500' : 'bg-slate-600'}`}>
                                <div className={`bg-white w-4 h-4 rounded-full shadow-sm transform transition-transform ${isRecording ? 'translate-x-6' : 'translate-x-0'}`} />
                            </div>
                        </div>
                    </div>

                    {/* <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-slate-400 uppercase tracking-wider">Options</label>
                        <div
                            className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${isRecording ? 'bg-red-500/20 border-red-500/50' : 'bg-slate-900/80 border-slate-700'}`}
                            onClick={() => setIsRecording(!isRecording)}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-full ${isRecording ? 'bg-red-500' : 'bg-slate-700'}`}>
                                    <Mic size={20} className="text-white" />
                                </div>
                                <span className={`font-medium ${isRecording ? 'text-red-400' : 'text-slate-300'}`}>
                                    Record Performance
                                </span>
                            </div>
                            <div className={`w-12 h-6 rounded-full p-1 transition-colors ${isRecording ? 'bg-red-500' : 'bg-slate-600'}`}>
                                <div className={`bg-white w-4 h-4 rounded-full shadow-sm transform transition-transform ${isRecording ? 'translate-x-6' : 'translate-x-0'}`} />
                            </div>
                        </div>
                    </div> */}
                </div>

                {/* Action Button */}
                <button
                    onClick={onStart}
                    disabled={!file}
                    className={`mt-8 w-full py-4 rounded-xl font-bold text-xl shadow-lg transition-all transform hover:scale-[1.02] active:scale-[0.98]
            ${file
                            ? 'bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-purple-500/25 hover:shadow-purple-500/40'
                            : 'bg-slate-700 text-slate-500 cursor-not-allowed'}
          `}
                >
                    {file ? 'Start Karaoke Session' : 'Upload a file to start'}
                </button>
            </div>
        </div>
    );
};
export default SetupScreen;