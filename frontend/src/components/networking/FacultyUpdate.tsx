import React, { useState, useEffect } from 'react';
import { Save, Check } from 'lucide-react';
import api from '../../services/api';

interface Faculty {
  person_uuid: string;
  name: string;
  department: string;
  current_work?: string;
}

const FacultyUpdate: React.FC = () => {
  const [facultyList, setFacultyList] = useState<Faculty[]>([]);
  const [selectedFaculty, setSelectedFaculty] = useState<string>('');
  const [currentWork, setCurrentWork] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchFaculty();
  }, []);

  const fetchFaculty = async () => {
    setLoading(true);
    try {
      const response = await api.get('/faculty/?limit=100');
      setFacultyList(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching faculty:', error);
      setFacultyList([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFacultySelect = (uuid: string) => {
    setSelectedFaculty(uuid);
    const faculty = facultyList.find(f => f.person_uuid === uuid);
    if (faculty) {
      setCurrentWork(faculty.current_work || '');
      setMessage('');
    }
  };

  const handleSave = async () => {
    if (!selectedFaculty) return;
    
    setSaving(true);
    try {
      await api.patch(`/faculty/${selectedFaculty}`, { current_work: currentWork });
      setMessage('Status updated successfully!');
      // Update local list
      setFacultyList(prev => prev.map(f => 
        f.person_uuid === selectedFaculty ? { ...f, current_work: currentWork } : f
      ));
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error updating faculty:', error);
      setMessage('Error connecting to server.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div className="card-header">
        <h2 className="card-title">Faculty Status Update</h2>
        <p className="card-subtitle">Keep your profile current so donors can find your latest work.</p>
      </div>
      
      <div style={{ padding: '1.5rem' }}>
        <div className="form-group">
          <label className="form-label">Select Your Profile</label>
          <select 
            className="form-control"
            value={selectedFaculty}
            onChange={(e) => handleFacultySelect(e.target.value)}
            disabled={loading}
          >
            <option value="">-- Select Faculty Member --</option>
            {facultyList.map(f => (
              <option key={f.person_uuid} value={f.person_uuid}>
                {f.name} ({f.department})
              </option>
            ))}
          </select>
        </div>

        {selectedFaculty && (
          <div className="form-group" style={{ marginTop: '1.5rem' }}>
            <label className="form-label">What are you working on right now?</label>
            <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>
              Describe your current research focus, funding needs, or new project ideas. This helps the AI match you with relevant donors.
            </p>
            <textarea
              className="form-control"
              rows={5}
              value={currentWork}
              onChange={(e) => setCurrentWork(e.target.value)}
              placeholder="e.g., I am currently seeking funding for a pilot study on urban vertical farming..."
            />
            
            <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button 
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                {saving ? 'Saving...' : <><Save size={18} /> Update Status</>}
              </button>
              
              {message && (
                <span style={{ color: message.includes('Failed') || message.includes('Error') ? 'var(--color-error)' : 'var(--color-success)', display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 500 }}>
                  {message.includes('success') && <Check size={18} />} {message}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FacultyUpdate;
