import { Disc } from "lucide-react";
import { useEffect, useState, useRef } from "react";
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
    const [statusText, setStatusText] = useState("Uploading...");
    const hasStarted = useRef(false);

    useEffect(() => {
        let isCancelled = false;
        let pollInterval: any = null;

        if (hasStarted.current) return;
        hasStarted.current = true;

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
            .then(async res => {
                if (!res.ok) {
                    let errText = "Processing failed";
                    try {
                        const errObj = await res.json();
                        if (errObj && errObj.error) errText = errObj.error;
                    } catch (e) {
                        // ignore JSON parse error on non-JSON 500 errors
                    }
                    throw new Error(errText);
                }
                return res.json();
            })
            .then(data => {
                if (isCancelled) return;
                const songId = data.song_id;

                pollInterval = setInterval(() => {
                    fetch(`http://localhost:5001/get_song_data?song_id=${songId}`)
                        .then(res => res.json())
                        .then(songData => {
                            if (isCancelled) return;

                            if (songData.status === 'done') {
                                clearInterval(pollInterval);
                                onComplete(songData);
                            } else if (songData.status === 'separating') {
                                setStatusText("Separating Vocals...");
                            } else if (songData.status === 'transcribing') {
                                setStatusText("Transcribing Lyrics...");
                            } else if (songData.status.startsWith('error')) {
                                clearInterval(pollInterval);
                                onError(`Backend failed: ${songData.status}`);
                            }
                        })
                        .catch(err => {
                            clearInterval(pollInterval);
                            onError("Polling error: " + err.message);
                        });
                }, 3000);
            })
            .catch(err => {
                if (!isCancelled) {
                    onError(err.message);
                }
            });

        return () => {
            isCancelled = true;
            if (pollInterval) clearInterval(pollInterval);
        };
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
            <h2 className="text-2xl font-bold animate-pulse mb-2">{statusText}</h2>
            <p className="text-slate-400">Syncing with AI engine</p>
        </div>
    );
};
export default ProcessingScreen;