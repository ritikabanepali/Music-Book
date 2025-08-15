import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api';

function AlbumDetailPage() {
    // Get the spotifyId from the URL (e.g., /album/spotifyId)
    const { spotifyId } = useParams();

    const [albumDetails, setAlbumDetails] = useState(null);
    const [reviews, setReviews] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    // State for the new review form
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');

    // useEffect runs when the component mounts or spotifyId changes
    useEffect(() => {
        const fetchAlbumDetails = async () => {
            setIsLoading(true);
            try {
                const response = await apiClient.get(`/album-details/${spotifyId}/`);
                setAlbumDetails(response.data.spotify_details);
                setReviews(response.data.local_reviews);
            } catch (err) {
                setError('Failed to load album details.');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAlbumDetails();
    }, [spotifyId]); // Re-run this effect if the spotifyId in the URL changes

    const handleReviewSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await apiClient.post('/reviews/', {
                spotify_album_id: spotifyId,
                rating: rating,
                comment: comment,
            });
            // Add the new review to the top of the list to instantly update the UI
            setReviews([response.data, ...reviews]);
            // Clear the form
            setComment('');
            setRating(5);
        } catch (err) {
            console.error('Failed to submit review:', err);
            alert('Failed to submit review.');
        }
    };

    if (isLoading) return <p>Loading album...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;
    if (!albumDetails) return <p>Album not found.</p>;

    return (
        <div>
            {/* Album Details Section */}
            <img src={albumDetails.images[0]?.url} alt={albumDetails.name} width="200" />
            <h1>{albumDetails.name}</h1>
            <h2>{albumDetails.artists.map(artist => artist.name).join(', ')}</h2>
            
            <hr />

            {/* Review Submission Form */}
            <h3>Leave a Review</h3>
            <form onSubmit={handleReviewSubmit}>
                <div>
                    <label>Rating: </label>
                    <select value={rating} onChange={e => setRating(parseInt(e.target.value))}>
                        <option value={5}>5 Stars</option>
                        <option value={4}>4 Stars</option>
                        <option value={3}>3 Stars</option>
                        <option value={2}>2 Stars</option>
                        <option value={1}>1 Star</option>
                    </select>
                </div>
                <div>
                    <label>Comment: </label>
                    <textarea value={comment} onChange={e => setComment(e.target.value)} rows="4" cols="50"></textarea>
                </div>
                <button type="submit">Submit Review</button>
            </form>

            <hr />

            {/* Existing Reviews Section */}
            <h3>Reviews</h3>
            {reviews.length > 0 ? (
                reviews.map(review => (
                    <div key={review.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
                        <p><strong>User:</strong> {review.user}</p>
                        <p><strong>Rating:</strong> {review.rating} / 5</p>
                        <p>{review.comment}</p>
                    </div>
                ))
            ) : (
                <p>No reviews yet. Be the first!</p>
            )}
        </div>
    );
}

export default AlbumDetailPage;