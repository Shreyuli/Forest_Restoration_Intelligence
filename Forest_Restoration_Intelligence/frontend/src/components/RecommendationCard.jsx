const CONFIDENCE_COLOR = {
  high: "var(--confidence-high)",
  medium: "var(--confidence-medium)",
  low: "var(--confidence-low)",
};

const CONFIDENCE_ON = {
  high: "var(--confidence-high-on)",
  medium: "var(--confidence-medium-on)",
  low: "var(--confidence-low-on)",
};

export default function RecommendationCard({ rec, sourceDetails }) {
  const color = CONFIDENCE_COLOR[rec.confidence] || "var(--border)";
  const onColor = CONFIDENCE_ON[rec.confidence] || "var(--ink)";
  const details = sourceDetails || [];
  const linkParts = rec.addresses_link.split("->");

  return (
    <div className="rec-card" style={{ "--stripe-color": color }}>
      <div className="rec-card-header">
        <h4>{rec.what_to_do}</h4>
        <span className="confidence-pill" style={{ backgroundColor: color, color: onColor }}>
          {rec.confidence}
        </span>
      </div>

      <span className="rec-chain-tag">
        &#8618; {linkParts.join(" → ")}
      </span>

      <p className="rec-why">{rec.why_it_works}</p>

      <div className="rec-meta-row">
        <span className="rec-tag">time horizon: {rec.time_horizon}</span>
      </div>

      <table className="rec-metrics">
        <tbody>
          {rec.impacted_metrics.map((m, i) => (
            <tr key={i}>
              <td className="metric-name">{m.metric.replaceAll("_", " ")}</td>
              <td className="metric-effect">{m.effect}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="rec-sources">
        <strong>Sources:</strong>{" "}
        {details.length > 0
          ? details.map((s, i) => (
              <span key={s.source_id}>
                <a href={s.url} target="_blank" rel="noreferrer">
                  {s.title} ({s.year})
                </a>
                {i < details.length - 1 ? "; " : ""}
              </span>
            ))
          : rec.sources.join(", ")}
      </div>
    </div>
  );
}
