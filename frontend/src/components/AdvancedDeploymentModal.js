import React, { useState } from 'react';

const AdvancedDeploymentModal = ({ isOpen, onClose, projectId, githubRepoUrl }) => {
  const [platform, setPlatform] = useState('vercel');
  const [projectName, setProjectName] = useState('');
  const [envVars, setEnvVars] = useState('');
  const [framework, setFramework] = useState('');
  const [buildCommand, setBuildCommand] = useState('');
  const [startCommand, setStartCommand] = useState('');
  const [publishDir, setPublishDir] = useState('');
  const [deploying, setDeploying] = useState(false);
  const [deploymentResult, setDeploymentResult] = useState(null);
  const [error, setError] = useState(null);

  const platformConfigs = {
    vercel: {
      name: 'Vercel',
      icon: '▲',
      color: '#000000',
      description: 'Best for Next.js, React, Vue applications',
      frameworks: ['nextjs', 'react', 'vue', 'svelte', 'angular'],
      features: ['Automatic HTTPS', 'Global CDN', 'Serverless Functions']
    },
    netlify: {
      name: 'Netlify',
      icon: '🌊',
      color: '#00C7B7',
      description: 'Perfect for static sites and JAMstack apps',
      frameworks: ['react', 'vue', 'angular', 'gatsby', 'hugo'],
      features: ['Instant rollbacks', 'Split testing', 'Forms & Identity']
    },
    render: {
      name: 'Render',
      icon: '🎯',
      color: '#46E3B7',
      description: 'Full-stack hosting for web services',
      frameworks: ['express', 'fastapi', 'django', 'flask', 'rails'],
      features: ['Auto-deploy from Git', 'Private services', 'Managed databases']
    }
  };

  const handleDeploy = async () => {
    if (!projectName) {
      setError('Project name is required');
      return;
    }

    if (!githubRepoUrl) {
      setError('GitHub repository URL is required');
      return;
    }

    setDeploying(true);
    setError(null);
    setDeploymentResult(null);

    try {
      const token = localStorage.getItem('token');
      
      // Parse environment variables if provided
      let parsedEnvVars = {};
      if (envVars.trim()) {
        try {
          envVars.split('\n').forEach(line => {
            const [key, ...valueParts] = line.split('=');
            if (key && valueParts.length > 0) {
              parsedEnvVars[key.trim()] = valueParts.join('=').trim();
            }
          });
        } catch (e) {
          setError('Invalid environment variables format. Use KEY=VALUE format, one per line.');
          setDeploying(false);
          return;
        }
      }

      const deploymentRequest = {
        platform,
        github_repo_url: githubRepoUrl,
        project_name: projectName,
        env_vars: Object.keys(parsedEnvVars).length > 0 ? parsedEnvVars : null,
        framework: framework || null,
        build_command: buildCommand || null,
        start_command: startCommand || null,
        publish_dir: publishDir || null
      };

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/projects/${projectId}/deploy`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(deploymentRequest)
        }
      );

      const data = await response.json();

      if (response.ok && data.success) {
        setDeploymentResult(data);
      } else {
        setError(data.error || data.detail || 'Deployment failed');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setDeploying(false);
    }
  };

  if (!isOpen) return null;

  const currentPlatform = platformConfigs[platform];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        maxWidth: '700px',
        width: '90%',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '24px', fontSize: '28px', fontWeight: '700' }}>
          🚀 Deploy to Cloud
        </h2>

        {/* Platform Selection */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '12px', fontWeight: '600', fontSize: '14px', color: '#333' }}>
            Choose Platform
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {Object.entries(platformConfigs).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setPlatform(key)}
                style={{
                  padding: '16px',
                  border: platform === key ? `2px solid ${config.color}` : '2px solid #e5e5e5',
                  borderRadius: '12px',
                  backgroundColor: platform === key ? `${config.color}10` : 'white',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.2s',
                  fontWeight: platform === key ? '600' : '400'
                }}
              >
                <div style={{ fontSize: '32px', marginBottom: '8px' }}>{config.icon}</div>
                <div style={{ fontSize: '14px' }}>{config.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Platform Info */}
        <div style={{
          backgroundColor: '#f8f9fa',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          <div style={{ fontWeight: '600', marginBottom: '8px' }}>
            {currentPlatform.icon} {currentPlatform.name}
          </div>
          <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
            {currentPlatform.description}
          </div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            ✨ {currentPlatform.features.join(' • ')}
          </div>
        </div>

        {/* Project Name */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
            Project Name *
          </label>
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="my-awesome-project"
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #ddd',
              fontSize: '14px'
            }}
          />
        </div>

        {/* Framework (Vercel specific) */}
        {platform === 'vercel' && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
              Framework (Optional)
            </label>
            <select
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '14px'
              }}
            >
              <option value="">Auto-detect</option>
              {currentPlatform.frameworks.map(fw => (
                <option key={fw} value={fw}>{fw}</option>
              ))}
            </select>
          </div>
        )}

        {/* Build Command (Netlify/Render) */}
        {(platform === 'netlify' || platform === 'render') && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
              Build Command (Optional)
            </label>
            <input
              type="text"
              value={buildCommand}
              onChange={(e) => setBuildCommand(e.target.value)}
              placeholder="npm run build"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '14px'
              }}
            />
          </div>
        )}

        {/* Publish Directory (Netlify) */}
        {platform === 'netlify' && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
              Publish Directory (Optional)
            </label>
            <input
              type="text"
              value={publishDir}
              onChange={(e) => setPublishDir(e.target.value)}
              placeholder="build or dist"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '14px'
              }}
            />
          </div>
        )}

        {/* Start Command (Render) */}
        {platform === 'render' && (
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
              Start Command (Optional)
            </label>
            <input
              type="text"
              value={startCommand}
              onChange={(e) => setStartCommand(e.target.value)}
              placeholder="npm start"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid #ddd',
                fontSize: '14px'
              }}
            />
          </div>
        )}

        {/* Environment Variables */}
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', fontSize: '14px' }}>
            Environment Variables (Optional)
          </label>
          <textarea
            value={envVars}
            onChange={(e) => setEnvVars(e.target.value)}
            placeholder={'API_KEY=your_key\nDATABASE_URL=your_url'}
            rows={4}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '1px solid #ddd',
              fontSize: '13px',
              fontFamily: 'monospace',
              resize: 'vertical'
            }}
          />
          <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
            Format: KEY=VALUE, one per line
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fee',
            color: '#c33',
            borderRadius: '8px',
            marginBottom: '16px',
            fontSize: '14px'
          }}>
            ❌ {error}
          </div>
        )}

        {/* Success Message */}
        {deploymentResult && deploymentResult.success && (
          <div style={{
            padding: '16px',
            backgroundColor: '#e8f5e9',
            borderRadius: '8px',
            marginBottom: '16px'
          }}>
            <div style={{ color: '#2e7d32', fontWeight: '600', marginBottom: '8px' }}>
              ✅ Deployment Initiated Successfully!
            </div>
            <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
              Status: {deploymentResult.status}
            </div>
            {deploymentResult.deployment_url && (
              <a
                href={deploymentResult.deployment_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#1976d2',
                  textDecoration: 'none',
                  fontSize: '14px',
                  display: 'inline-block',
                  padding: '8px 16px',
                  backgroundColor: 'white',
                  borderRadius: '6px',
                  marginTop: '8px'
                }}
              >
                🔗 View Deployment →
              </a>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            disabled={deploying}
            style={{
              padding: '12px 24px',
              borderRadius: '8px',
              border: '1px solid #ddd',
              backgroundColor: 'white',
              cursor: deploying ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              opacity: deploying ? 0.5 : 1
            }}
          >
            {deploymentResult ? 'Close' : 'Cancel'}
          </button>
          {!deploymentResult && (
            <button
              onClick={handleDeploy}
              disabled={deploying || !projectName}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: currentPlatform.color,
                color: 'white',
                cursor: (deploying || !projectName) ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                opacity: (deploying || !projectName) ? 0.5 : 1
              }}
            >
              {deploying ? '⏳ Deploying...' : `🚀 Deploy to ${currentPlatform.name}`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedDeploymentModal;
