interface ConfidenceBadgeProps {
  score: number; // 0.0 to 1.0
  label?: string;
  size?: 'sm' | 'md';
}

export default function ConfidenceBadge({ score, label, size = 'md' }: ConfidenceBadgeProps) {
  let badgeClass = 'badge';
  let text = 'Unknown';

  if (score >= 0.85) {
    badgeClass += ' badge-success';
    text = 'High Confidence';
  } else if (score >= 0.7) {
    badgeClass += ' badge-warning';
    text = 'Medium Confidence';
  } else {
    // Fallback for low confidence
    badgeClass += ' badge-error'; // We might need to add this class to index.css or use inline style
    text = 'Low Confidence';
  }

  const displayText = label || text;
  const percentage = Math.round(score * 100);
  
  // Inline styles for specific overrides if needed, or rely on index.css
  const style: React.CSSProperties = {
    fontSize: size === 'sm' ? 'var(--font-size-xs)' : 'var(--font-size-sm)',
    padding: size === 'sm' ? '2px 6px' : '4px 8px',
  };
  
  if (score < 0.7) {
      style.backgroundColor = 'rgba(231, 76, 60, 0.1)';
      style.color = 'var(--color-error)';
  }

  return (
    <div className={badgeClass} style={style}>
      <span style={{
        marginRight: '6px',
        height: size === 'sm' ? '6px' : '8px',
        width: size === 'sm' ? '6px' : '8px',
        borderRadius: '50%',
        backgroundColor: 'currentColor',
        opacity: 0.75,
        display: 'inline-block'
      }}></span>
      {displayText} ({percentage}%)
    </div>
  );
}
