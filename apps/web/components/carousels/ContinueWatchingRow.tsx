type ContinueWatchingItem = {
  itemId: string;
  title: string;
  progressPercent: number;
};

type ContinueWatchingRowProps = {
  items: ContinueWatchingItem[];
};

export function ContinueWatchingRow({ items }: ContinueWatchingRowProps) {
  return (
    <section>
      <h2>Continue Watching</h2>
      <ul>
        {items.map((item) => (
          <li key={item.itemId}>
            {item.title} — {item.progressPercent}%
          </li>
        ))}
      </ul>
    </section>
  );
}
