import { Mic2, Library } from 'lucide-react';

interface SplashPageProps {
    onNavigate: (view: 'setup' | 'repertoire') => void;
}

export default function SplashPage({ onNavigate }: SplashPageProps) {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen text-white relative z-10 px-4">
            {/* Title Section */}
            <div className="text-center mb-16 animate-fade-in-up">
                <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight mb-4">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500">
                        Karaoke
                    </span>
                    <br />
                    Creator
                </h1>
                <p className="text-gray-400 text-lg md:text-xl max-w-lg mx-auto">
                    Separate vocals and instantly create pro-quality karaoke tracks from your favorite songs.
                </p>
            </div>

            {/* Actions */}
            <div className="flex flex-col md:flex-row gap-6 w-full max-w-2xl px-4 animate-fade-in-up" style={{ animationDelay: '150ms' }}>
                {/* Create Track Button */}
                <button
                    onClick={() => onNavigate('setup')}
                    className="group relative flex-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-8 transition-all duration-300 overflow-hidden"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-pink-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="relative z-10 flex flex-col items-center text-center">
                        <div className="w-16 h-16 rounded-full bg-pink-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                            <Mic2 className="w-8 h-8 text-pink-400" />
                        </div>
                        <h3 className="text-2xl font-bold mb-2">Create Track</h3>
                        <p className="text-gray-400">Upload a song to separate vocals and generate a karaoke video.</p>
                    </div>
                </button>

                {/* View Repertoire Button */}
                <button
                    onClick={() => onNavigate('repertoire')}
                    className="group relative flex-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl p-8 transition-all duration-300 overflow-hidden"
                >
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="relative z-10 flex flex-col items-center text-center">
                        <div className="w-16 h-16 rounded-full bg-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                            <Library className="w-8 h-8 text-indigo-400" />
                        </div>
                        <h3 className="text-2xl font-bold mb-2">Repertoire</h3>
                        <p className="text-gray-400">Browse and play previously created karaoke tracks.</p>
                    </div>
                </button>
            </div>
        </div>
    );
}
