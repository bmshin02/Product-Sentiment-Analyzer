type SentimentSummaryProps = {
  positive: number;
  neutral: number;
  negative: number;
};

function SentimentSummary({
  positive,
  neutral,
  negative,
}: SentimentSummaryProps) {
  return (
    <section className="sentiment-section">
      <h3>Overall Sentiment</h3>

      <div className="sentiment-grid">
        <div className="sentiment-card">
          <span>Positive</span>
          <strong>{Math.round(positive * 100)}%</strong>
        </div>

        <div className="sentiment-card">
          <span>Neutral</span>
          <strong>{Math.round(neutral * 100)}%</strong>
        </div>

        <div className="sentiment-card">
          <span>Negative</span>
          <strong>{Math.round(negative * 100)}%</strong>
        </div>
      </div>
    </section>
  );
}

export default SentimentSummary;
