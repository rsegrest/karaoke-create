import { Disc } from "lucide-react";
import { useEffect } from "react";
import '../karaoke.css';

export const ProcessingScreen = ({
    file,
    songTitle,
    artist,
    onComplete,
    onError
}: {
    file: File;
    songTitle: string;
    artist: string;
    onComplete: (data: any) => void;
    onError: (err: string) => void;
}) => {
    useEffect(() => {
        if (!file) {
            onError("No file provided");
            return;
        }

        const formData = new FormData();
        formData.append('music_file', file);
        formData.append('song_title', songTitle || file.name);
        formData.append('original_artist', artist || "Unknown Artist");
        formData.append('performer_name', "Current User"); // No auth yet

        fetch('http://localhost:5001/queue_request', {
            method: 'POST',
            body: formData,
        })
            .then(res => {
                if (!res.ok) throw new Error("Processing failed");
                return res.json();
            })
            .then(data => {
                onComplete(data);
            })
            .catch(err => {
                onError(err.message);
            });
    }, [file, songTitle, artist, onComplete, onError]);

    return (
        <div className="relative z-10 flex flex-col items-center justify-center min-h-screen text-white">
            <div className="relative w-32 h-32 mb-8">
                <div className="absolute inset-0 border-4 border-slate-700 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-t-pink-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                    <Disc className="animate-pulse text-purple-400" size={48} />
                </div>
            </div>
            <h2 className="text-2xl font-bold animate-pulse mb-2">Separating Vocals...</h2>
            <p className="text-slate-400">Syncing lyrics with AI engine</p>
        </div>
    );
};
export default ProcessingScreen;