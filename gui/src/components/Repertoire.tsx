import { useState, useEffect } from 'react';
import { Search, ChevronLeft, Play, AlertCircle, Loader2, Library } from 'lucide-react';

interface Song {
    song_id: number;
    song_title: string;
    original_artist: string;
    status: string;
    owner_id: number | null;
}

interface RepertoireProps {
    onBack: () => void;
    onPlaySong: (songId: number) => void;
}

const CURRENT_USER_ID = 1; // Hardcoded for now until Auth is implemented

export default function Repertoire({ onBack, onPlaySong }: RepertoireProps) {
    const [songs, setSongs] = useState<Song[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [mySongsOnly, setMySongsOnly] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSongs();
    }, []);

    const fetchSongs = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await fetch('http://localhost:5001/list_available_songs');
            if (!response.ok) {
                throw new Error(`Error fetching songs: ${response.statusText}`);
            }
            const data = await response.json();
            setSongs(data || []);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch repertoire');
        } finally {
            setLoading(false);
        }
    };

    const filteredSongs = songs.filter((song) => {
        // Search filter
        const matchesSearch =
            song.song_title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
            song.original_artist?.toLowerCase().includes(searchQuery.toLowerCase());

        // Owner filter
        const matchesOwner = mySongsOnly ? song.owner_id === CURRENT_USER_ID : true;

        return matchesSearch && matchesOwner;
    });

    return (
        <div className="flex flex-col min-h-screen text-white relative z-10 px-4 py-8">
            {/* Header bar */}
            <div className="w-full max-w-5xl mx-auto mb-8 flex items-center justify-between animate-fade-in-up">
                <button
                    onClick={onBack}
                    className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                    <ChevronLeft className="w-5 h-5" />
                    <span>Back</span>
                </button>
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
                    Repertoire
                </h2>
                <div className="w-16" /> {/* Spacer for centering */}
            </div>

            {/* Main Content Area */}
            <div className="w-full max-w-5xl mx-auto flex-1 flex flex-col min-h-0 bg-white/5 border border-white/10 rounded-2xl overflow-hidden backdrop-blur-md animate-fade-in-up" style={{ animationDelay: '100ms' }}>

                {/* Controls Bar */}
                <div className="flex flex-col sm:flex-row gap-4 justify-between items-center p-6 border-b border-white/10 bg-black/20">

                    {/* Search Box */}
                    <div className="relative w-full sm:w-96">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search by artist or song..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="block w-full pl-10 pr-3 py-2 border border-white/10 rounded-lg bg-white/5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                        />
                    </div>

                    {/* Toggle "My Songs" */}
                    <div className="flex items-center gap-3">
                        <label htmlFor="my-songs-toggle" className="text-sm text-gray-300 font-medium cursor-pointer">
                            My Songs Only
                        </label>
                        <button
                            id="my-songs-toggle"
                            onClick={() => setMySongsOnly(!mySongsOnly)}
                            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${mySongsOnly ? 'bg-indigo-500' : 'bg-gray-700'
                                }`}
                        >
                            <span className="sr-only">Toggle My Songs Only</span>
                            <span
                                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${mySongsOnly ? 'translate-x-5' : 'translate-x-0'
                                    }`}
                            />
                        </button>
                    </div>
                </div>

                {/* Table Area */}
                <div className="flex-1 overflow-auto p-0">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-full p-12 text-gray-400">
                            <Loader2 className="w-8 h-8 animate-spin mb-4 text-indigo-500" />
                            <p>Loading repertoire...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center h-full p-12 text-red-400">
                            <AlertCircle className="w-8 h-8 mb-4" />
                            <p>{error}</p>
                        </div>
                    ) : filteredSongs.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full p-12 text-gray-400">
                            <Library className="w-12 h-12 mb-4 opacity-50" />
                            <p className="text-lg">No songs found.</p>
                            <p className="text-sm mt-2 opacity-70">
                                {searchQuery || mySongsOnly ? "Adjust your filters to see more results." : "Create your first karaoke track to see it here!"}
                            </p>
                        </div>
                    ) : (
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-black/30 border-b border-white/10 text-sm uppercase tracking-wider text-gray-400">
                                    <th className="p-4 font-semibold">Title</th>
                                    <th className="p-4 font-semibold">Artist</th>
                                    <th className="p-4 font-semibold">Status</th>
                                    <th className="p-4 font-semibold text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {filteredSongs.map((song) => (
                                    <tr key={song.song_id} className="hover:bg-white/5 transition-colors group">
                                        <td className="p-4 font-medium">{song.song_title}</td>
                                        <td className="p-4 text-gray-300">{song.original_artist}</td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${song.status === 'done' ? 'bg-green-500/20 text-green-400' :
                                                song.status.startsWith('error') ? 'bg-red-500/20 text-red-400' :
                                                    'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {song.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-right">
                                            {song.status === 'done' ? (
                                                <button
                                                    onClick={() => onPlaySong(song.song_id)}
                                                    className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white/10 hover:bg-indigo-500 text-white transition-all transform hover:scale-110 active:scale-95"
                                                    title="Play Karaoke Track"
                                                >
                                                    <Play className="w-4 h-4 ml-0.5" />
                                                </button>
                                            ) : (
                                                <span className="text-gray-500 text-sm italic">Processing...</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
