type MediaCardProps = {
  title: string;
  subtitle?: string;
};

export function MediaCard({ title, subtitle }: MediaCardProps) {
  return (
    <article>
      <h3>{title}</h3>
      {subtitle ? <p>{subtitle}</p> : null}
    </article>
  );
}
