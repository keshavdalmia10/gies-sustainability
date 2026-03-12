import React, { useEffect, useState } from 'react';
import { Trophy, Medal } from 'lucide-react';
import api from '../../services/api';

interface LeaderboardEntry {
  name: string;
  major: string;
  points: number;
  avatar: string;
}

const Leaderboard: React.FC = () => {
  const [leaders, setLeaders] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch leaderboard data
    const fetchLeaderboard = async () => {
      try {
        const response = await api.get('/gamification/leaderboard?limit=5');
        setLeaders(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error("Failed to fetch leaderboard", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);

  return (
    <div className="card" style={{ padding: 'var(--spacing-lg)', backgroundColor: 'var(--color-surface)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-md)' }}>
        <Trophy size={24} color="#FFD700" />
        <h2 style={{ fontSize: 'var(--font-size-lg)', margin: 0 }}>Top Impact Detectives</h2>
      </div>

      {loading ? (
        <div className="text-center text-muted">Loading champions...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
          {leaders.map((user, index) => (
            <div key={index} style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 'var(--spacing-md)',
              padding: 'var(--spacing-sm)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: index === 0 ? 'rgba(255, 215, 0, 0.1)' : 'transparent',
              border: index === 0 ? '1px solid rgba(255, 215, 0, 0.3)' : 'none'
            }}>
              <div style={{ 
                width: '32px', 
                height: '32px', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontWeight: 'bold',
                color: index < 3 ? 'var(--color-primary)' : 'var(--color-text-light)'
              }}>
                {index + 1}
              </div>
              
              <img 
                src={user.avatar} 
                alt={user.name} 
                style={{ width: '40px', height: '40px', borderRadius: '50%' }} 
              />
              
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{user.name}</div>
                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)' }}>{user.major}</div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700, color: 'var(--color-primary)' }}>
                <Medal size={16} />
                {user.points} pts
              </div>
            </div>
          ))}
          
          {leaders.length === 0 && (
            <div className="text-center text-muted">No points awarded yet. Be the first!</div>
          )}
        </div>
      )}
    </div>
  );
};

export default Leaderboard;
