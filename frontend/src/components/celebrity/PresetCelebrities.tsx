import { useState } from 'react';

type PresetCelebrity = 'drake' | 'sydney_sweeney';

interface PresetCelebritiesProps {
  onSelect: (celebrity: PresetCelebrity) => void;
  selected?: PresetCelebrity;
}

export const PresetCelebrities = ({ onSelect, selected }: PresetCelebritiesProps) => {
  const [hoveredCard, setHoveredCard] = useState<PresetCelebrity | null>(null);

  const celebrities = [
    {
      id: 'drake' as PresetCelebrity,
      name: 'Drake',
      description: 'Hip-hop icon with expressive delivery',
      thumbnail: '/assets/drake-thumb.jpg', // Placeholder - would be actual thumbnail
      features: ['Natural speech', 'Engaging presence', 'Expressive gestures'],
    },
    {
      id: 'sydney_sweeney' as PresetCelebrity,
      name: 'Sydney Sweeney',
      description: 'Charismatic actress with warm personality',
      thumbnail: '/assets/sydney-thumb.jpg', // Placeholder - would be actual thumbnail
      features: ['Clear articulation', 'Friendly demeanor', 'Authentic delivery'],
    },
  ];

  return (
    <div className="preset-celebrities">
      <p className="preset-description">
        Choose from our professionally trained celebrity narrators
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
              <div className="thumbnail-placeholder">
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
              <p className="celebrity-description">{celebrity.description}</p>

              <ul className="celebrity-features">
                {celebrity.features.map((feature, index) => (
                  <li key={index}>
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

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
