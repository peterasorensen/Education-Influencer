import { useState, useEffect } from 'react';

interface Celebrity {
  id: string;
  name: string;
  imageUrl: string;
  hasAudio: boolean;
}

interface PresetCelebritiesProps {
  onSelect: (celebrity: string) => void;
  selected?: string;
}

export const PresetCelebrities = ({ onSelect, selected }: PresetCelebritiesProps) => {
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);
  const [celebrities, setCelebrities] = useState<Celebrity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch celebrities from API
  useEffect(() => {
    const fetchCelebrities = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/celebrities`);

        if (!response.ok) {
          throw new Error('Failed to fetch celebrities');
        }

        const data = await response.json();
        setCelebrities(data.celebrities);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching celebrities:', err);
        setError(err instanceof Error ? err.message : 'Failed to load celebrities');
        setLoading(false);
      }
    };

    fetchCelebrities();
  }, []);

  // Get full image URL
  const getImageUrl = (celebrity: Celebrity) => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return `${apiUrl}${celebrity.imageUrl}`;
  };

  if (loading) {
    return (
      <div className="preset-celebrities">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading celebrities...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preset-celebrities">
        <div className="error-state">
          <p>Error: {error}</p>
          <p className="error-help">Make sure the backend server is running</p>
        </div>
      </div>
    );
  }

  return (
    <div className="preset-celebrities">
      <p className="preset-description">
        Choose from our available celebrity narrators ({celebrities.length} total)
      </p>

      <div className="celebrity-grid">
        {celebrities.map((celebrity) => (
          <div
            key={celebrity.id}
            className={`celebrity-card ${selected === celebrity.id ? 'selected' : ''} ${
              hoveredCard === celebrity.id ? 'hovered' : ''
            }`}
            onMouseEnter={() => setHoveredCard(celebrity.id)}
            onMouseLeave={() => setHoveredCard(null)}
          >
            <div className="celebrity-thumbnail">
              <img
                src={getImageUrl(celebrity)}
                alt={celebrity.name}
                className="celebrity-image"
                loading="lazy"
                crossOrigin="anonymous"
                onLoad={(e) => {
                  console.log('Image loaded successfully:', celebrity.name);
                }}
                onError={(e) => {
                  console.error('Image failed to load:', celebrity.name, getImageUrl(celebrity));
                  // Fallback to placeholder if image fails to load
                  e.currentTarget.style.display = 'none';
                  const placeholder = e.currentTarget.nextElementSibling;
                  if (placeholder) {
                    (placeholder as HTMLElement).style.display = 'flex';
                  }
                }}
              />
              <div className="thumbnail-placeholder" style={{ display: 'none' }}>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              {selected === celebrity.id && (
                <div className="selected-badge">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              )}
            </div>

            <div className="celebrity-info">
              <h4 className="celebrity-name">{celebrity.name}</h4>

              {!celebrity.hasAudio && (
                <p className="no-audio-warning">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    width="14"
                    height="14"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  No voice sample available
                </p>
              )}

              <button
                className={`select-button ${selected === celebrity.id ? 'selected' : ''}`}
                onClick={() => onSelect(celebrity.id)}
              >
                {selected === celebrity.id ? (
                  <>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Selected
                  </>
                ) : (
                  'Select'
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
