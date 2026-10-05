import type { WordCount } from "../types/product";

type InsightListProps = {
  title: string;
  items: WordCount[];
};

function InsightList({ title, items }: InsightListProps) {
  return (
    <section className="insight-card">
      <h3>{title}</h3>

      <ul>
        {items.map((item) => (
          <li key={item.word}>
            {item.word} ({item.count})
          </li>
        ))}
      </ul>
    </section>
  );
}

export default InsightList;
