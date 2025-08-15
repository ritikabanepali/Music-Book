import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api';

function HomePage() {
    const [query, setQuery] = useState('');
    const [albums, setAlbums] = useState([]); // State for storing album results

    const handleSearch = async (e) => {
        e.preventDefault();
        try {
            // We will now always search for the 'album' type
            const response = await apiClient.get(`/spotify/search/?q=${query}&type=album`);
            // The response from Spotify for an album search is under the 'albums' key
            setAlbums(response.data.albums.items);
        } catch (error) {
            console.error("Search failed:", error);
            alert("Search failed. Please check the console for details.");
        }
    };

    return (
        <div>
            <h1>Search for Albums on Spotify</h1>
            <form onSubmit={handleSearch}>
                <input 
                    type="text" 
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)} 
                    placeholder="Search for an album..." 
                />
                <button type="submit">Search</button>
            </form>

            <div style={{ marginTop: '20px' }}>
                {/* Map over the albums state to display results */}
                {albums.map((album) => (
                    <div key={album.id}>
                        {/* Each result links to the correct album detail page */}
                        <Link to={`/album/${album.id}`}>
                            <p>{album.name} by {album.artists.map(a => a.name).join(', ')}</p>
                        </Link>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default HomePage;