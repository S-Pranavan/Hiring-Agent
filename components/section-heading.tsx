type Props = {
  eyebrow?: string;
  title: string;
  text: string;
};

export function SectionHeading({ eyebrow, title, text }: Props) {
  return (
    <div className="max-w-2xl">
      {eyebrow ? <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-primary">{eyebrow}</p> : null}
      <h2 className="text-3xl font-semibold tracking-tight text-ink sm:text-4xl">{title}</h2>
      <p className="mt-4 text-base leading-7 text-muted sm:text-lg">{text}</p>
    </div>
  );
}