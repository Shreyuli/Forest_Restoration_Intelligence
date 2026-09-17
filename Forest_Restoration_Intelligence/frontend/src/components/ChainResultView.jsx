import ChainDiagram from "./ChainDiagram.jsx";
import RecommendationCard from "./RecommendationCard.jsx";

export default function ChainResultView({ result, evidence }) {
  const recSourceDetails = (rec) => {
    const detailMap = evidence?.recommendation_sources?.[rec.what_to_do];
    return detailMap || [];
  };

  return (
    <div className="chain-result">
      <ChainDiagram chain={result.chain} evidence={evidence?.chain_evidence} path={result.path} />

      <div className="recommendations">
        <div className="recommendations-header">Restoration recommendations</div>
        {result.recommendations.map((rec, i) => (
          <RecommendationCard key={i} rec={rec} sourceDetails={recSourceDetails(rec)} />
        ))}
      </div>

      {result.notes?.length > 0 && (
        <ul className="result-notes">
          {result.notes.map((n, i) => (
            <li key={i}>{n}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
