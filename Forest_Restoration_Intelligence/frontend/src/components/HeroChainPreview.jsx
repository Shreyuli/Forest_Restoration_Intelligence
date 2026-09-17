const IDLE_NODES = [
  "Deforestation + climate",
  "Water stress",
  "Vegetation stress",
  "Habitat degradation",
  "Biodiversity decline",
];

export default function HeroChainPreview() {
  return (
    <div className="hero-preview" aria-hidden="true">
      <div className="hero-chain">
        {IDLE_NODES.map((label, i) => (
          <div key={label}>
            <div className="hero-chain-node">{label}</div>
            {i < IDLE_NODES.length - 1 && <div className="hero-chain-connector" />}
          </div>
        ))}
      </div>
    </div>
  );
}
