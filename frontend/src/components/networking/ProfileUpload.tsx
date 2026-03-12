import React, { useState } from 'react';
import api from '../../services/api';

const ProfileUpload: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [major, setMajor] = useState('');
  const [year, setYear] = useState('');
  const [bio, setBio] = useState('');
  const [skills, setSkills] = useState('');
  const [interests, setInterests] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/networking/student', {
          name,
          email,
          major,
          year,
          bio,
          skills: skills.split(',').map(s => s.trim()).filter(s => s),
          interests: interests.split(',').map(i => i.trim()).filter(i => i),
      });
      setMessage('Profile created successfully!');
      // Clear form
      setName('');
      setEmail('');
      setMajor('');
      setYear('');
      setBio('');
      setSkills('');
      setInterests('');
    } catch (error: any) {
      setMessage(`Error: ${error?.response?.data?.detail || 'Failed to create profile'}`);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Create Student Profile</h2>
        <p className="card-subtitle">Join the network to connect with faculty and peers.</p>
      </div>
      
      {message && (
        <div className={`mb-4 p-3 rounded ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`} style={{ backgroundColor: message.includes('Error') ? 'rgba(231, 76, 60, 0.1)' : 'rgba(46, 204, 113, 0.1)', color: message.includes('Error') ? 'var(--color-error)' : 'var(--color-success)' }}>
          {message}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-2">
          <div className="form-group">
            <label className="form-label">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="form-control"
              required
              placeholder="Jane Doe"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-control"
              required
              placeholder="jane.doe@illinois.edu"
            />
          </div>
        </div>
        
        <div className="grid grid-2">
          <div className="form-group">
            <label className="form-label">Major</label>
            <input
              type="text"
              value={major}
              onChange={(e) => setMajor(e.target.value)}
              className="form-control"
              placeholder="Business Administration"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Year</label>
            <input
              type="text"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="form-control"
              placeholder="e.g. Freshman, Sophomore"
            />
          </div>
        </div>
        
        <div className="form-group">
          <label className="form-label">Bio</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            className="form-control"
            rows={3}
            placeholder="Tell us about your sustainability interests..."
          />
        </div>
        
        <div className="form-group">
          <label className="form-label">Skills (comma separated)</label>
          <input
            type="text"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            className="form-control"
            placeholder="Python, Data Analysis, Public Speaking"
          />
        </div>
        
        <div className="form-group">
          <label className="form-label">Interests (comma separated)</label>
          <input
            type="text"
            value={interests}
            onChange={(e) => setInterests(e.target.value)}
            className="form-control"
            placeholder="Sustainability, AI, Social Impact"
          />
        </div>
        
        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', justifyContent: 'center' }}
        >
          Create Profile
        </button>
      </form>
    </div>
  );
};

export default ProfileUpload;
