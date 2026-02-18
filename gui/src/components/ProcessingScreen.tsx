import { Disc } from "lucide-react";
import { useEffect } from "react";
// 4. LOADING/PROCESSING SCREEN
export const ProcessingScreen = ({ onComplete }: { onComplete: () => void }) => {
    useEffect(() => {
        // Simulate AI processing time
        const timer = setTimeout(() => {
            onComplete();
        }, 2500);
        return () => clearTimeout(timer);
    }, [onComplete]);

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