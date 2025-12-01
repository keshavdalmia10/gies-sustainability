import React, { useState } from 'react';
import { Send, User, BookOpen, Search } from 'lucide-react';

interface SuggestedNode {
  id: string;
  label: string;
  type: string;
  group: number;
}

interface NetworkChatbotProps {
  onGraphUpdate?: (data: any) => void;
}

const NetworkChatbot: React.FC<NetworkChatbotProps> = ({ onGraphUpdate }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [suggestions, setSuggestions] = useState<SuggestedNode[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/networking/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (res.ok) {
        const data = await res.json();
        setResponse(data.response);
        setSuggestions(data.suggested_connections);
        if (data.graph_data && onGraphUpdate) {
          onGraphUpdate(data.graph_data);
        }
      } else {
        setResponse('Error analyzing network.');
      }
    } catch (error) {
      setResponse('Error connecting to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="card-header">
        <h2 className="card-title" style={{ fontSize: '1.25rem' }}>Network Assistant</h2>
        <p className="card-subtitle">Ask about skills, people, or topics.</p>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', padding: '1rem', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)' }}>
        {response ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{response}</div>
        ) : (
          <div className="text-center text-muted" style={{ marginTop: '2rem' }}>
            <Search size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
            <p>Try asking: "Who knows about Python?" or "Find sustainability experts"</p>
          </div>
        )}
        
        {suggestions.length > 0 && (
          <div className="mt-4">
            <h3 className="form-label">Suggested Connections:</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {suggestions.map((node) => (
                <div key={node.id} style={{ padding: '0.75rem', backgroundColor: 'white', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {node.type === 'student' || node.type === 'faculty' ? <User size={16} /> : <BookOpen size={16} />}
                    <span style={{ fontWeight: 500 }}>{node.label}</span>
                    <span className="badge" style={{ fontSize: '0.7rem', backgroundColor: 'var(--color-surface)' }}>{node.type}</span>
                  </div>
                  <button className="btn btn-outline" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>Connect</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
          className="form-control"
          placeholder="Ask a question..."
          style={{ flex: 1 }}
        />
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="btn btn-primary"
          style={{ padding: '0.5rem 1rem' }}
        >
          {loading ? '...' : <Send size={18} />}
        </button>
      </div>
    </div>
  );
};

export default NetworkChatbot;
