type InsightListProps = {
  title: string;
  items: string[];
};

function InsightList({ title, items }: InsightListProps) {
  return (
    <section className="insight-card">
      <h3>{title}</h3>

      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export default InsightList;
