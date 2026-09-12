type PagePlaceholderProps = {
  title: string;
  description: string;
};

export function PagePlaceholder({ title, description }: PagePlaceholderProps) {
  return (
    <section className="page-panel">
      <p className="eyebrow">Phase 1 placeholder</p>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}
