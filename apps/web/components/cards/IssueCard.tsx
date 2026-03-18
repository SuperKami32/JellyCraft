type IssueCardProps = {
  issue: string;
  severity?: "low" | "medium" | "high";
};

export function IssueCard({ issue, severity = "medium" }: IssueCardProps) {
  return (
    <article>
      <strong>{severity.toUpperCase()}</strong>
      <p>{issue}</p>
    </article>
  );
}
