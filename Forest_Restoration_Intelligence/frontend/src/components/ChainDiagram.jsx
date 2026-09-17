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

const STEP_MS = 260;

function NodeCard({ node, evidence, delay }) {
  const color = CONFIDENCE_COLOR[node.confidence] || "var(--border)";
  const onColor = CONFIDENCE_ON[node.confidence] || "var(--ink)";
  const sources = evidence?.[node.node] || [];

  return (
    <div
      className="chain-node"
      style={{ "--stripe-color": color, "--chain-delay": `${delay}ms` }}
    >
      <div className="chain-node-stripe" />
      <div className="chain-node-body">
        <div className="chain-node-top">
          <span className="chain-node-label">
            <span className="chain-node-dot" />
            {node.label}
          </span>
          <span className="chain-node-meta">
            <span
              className="confidence-pill"
              style={{ backgroundColor: color, color: onColor }}
            >
              {node.confidence}
            </span>
            <span className="evidence-count">
              {node.evidence_source_ids.length} source
              {node.evidence_source_ids.length === 1 ? "" : "s"}
            </span>
          </span>
        </div>
        {sources.length > 0 && (
          <ul className="chain-node-sources">
            {sources.map((s) => (
              <li key={s.source_id}>
                <a href={s.url} target="_blank" rel="noreferrer" title={s.publisher}>
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default function ChainDiagram({ chain, evidence, path }) {
  return (
    <div className="chain-diagram">
      <div className="chain-diagram-header">
        Causal chain
        <span className="path-badge">{path} path</span>
      </div>
      <div className="chain-flow">
        {chain.map((node, idx) => {
          const nodeDelay = idx * STEP_MS * 2;
          const connectorColor = CONFIDENCE_COLOR[node.confidence] || "var(--border)";
          return (
            <div className="chain-flow-step" key={node.node}>
              <NodeCard node={node} evidence={evidence} delay={nodeDelay} />
              {idx < chain.length - 1 && (
                <div className="chain-connector">
                  <div
                    className="chain-connector-line"
                    style={{
                      "--stripe-color": connectorColor,
                      "--chain-delay": `${nodeDelay + STEP_MS}ms`,
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
