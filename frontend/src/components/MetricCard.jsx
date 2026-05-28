const MetricCard = ({ label, value, hint }) => {
  return (
    <div className="card metric-card">
      <span className="eyebrow">{label}</span>
      <div className="metric-value">{value}</div>
      {hint && <p className="metric-hint">{hint}</p>}
    </div>
  );
};

export default MetricCard;