import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api';

function MyReviewsPage() {
    const [reviews, setReviews] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchMyReviews = async () => {
            try {
                // This endpoint gets reviews only for the logged-in user
                const response = await apiClient.get("/reviews/?user=me");
                setReviews(response.data);
            } catch (err) {
                setError('Failed to load your reviews.');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchMyReviews();
    }, []); // Empty array means this runs only once when the component mounts

    if (isLoading) return <p>Loading your reviews...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div>
            <h1>My Reviews</h1>
            {reviews.length > 0 ? (
                reviews.map(review => (
                    <div key={review.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
                        {/* Since the album data is nested, we can display it here */}
                        <h3>
                            <Link to={`/album/${review.album.spotify_id}`}>
                                {review.album.title}
                            </Link>
                        </h3>
                        <p><strong>My Rating:</strong> {review.rating} / 5</p>
                        <p><strong>My Comment:</strong> {review.comment}</p>
                    </div>
                ))
            ) : (
                <p>You haven't written any reviews yet.</p>
            )}
        </div>
    );
}

export default MyReviewsPage;