// DEMO HOST PAGE: a rough stand-in for paper.shrit.in's subject page, so the feature can be
// previewed in context. Only the two marked lines need to go into the real site.
import { notFound } from "next/navigation";
import { QuestionMap, getSubjectTags } from "@/features/question-map";
import { ThemeToggle } from "./theme-toggle";

export default async function SubjectPage({ params }: { params: Promise<{ slug: string[] }> }) {
  const { slug } = await params;
  const parts = slug.map(decodeURIComponent);
  const i = parts.indexOf("subject");
  if (i === -1 || !parts[i + 1]) notFound();
  const subjectCode = parts[i + 1];

  const tags = getSubjectTags(subjectCode); // <-- line 1 for the real site

  return (
    <div className="min-h-screen flex-1 bg-background">
      <header className="sticky top-0 z-10 border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-3 sm:px-6">
          <nav className="truncate text-sm text-muted-foreground">{parts.slice(0, i).join(" / ")}</nav>
          <span className="ml-auto rounded bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground">local preview</span>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-8 sm:px-6">
        <div>
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">{subjectCode}</p>
          <h1 className="text-2xl font-semibold">{tags?.title ?? subjectCode}</h1>
          <p className="text-sm text-muted-foreground">{tags?.papers.length ?? 0} papers</p>
        </div>

        {/* Stand-in for the site's existing paper list */}
        <ul className="flex flex-col divide-y divide-border rounded-xl border border-border">
          {tags?.papers.map((p) => (
            <li key={p.pdf_path} className="flex items-center gap-3 px-4 py-3 text-sm">
              <span className="font-mono">{p.code}</span>
              <span className="text-muted-foreground">{p.date} · {p.exam_type}</span>
              <a className="ml-auto text-primary hover:underline" href={`https://paper.shrit.in${p.pdf_path}`} target="_blank" rel="noopener noreferrer">
                Open
              </a>
            </li>
          ))}
        </ul>

        {tags && <QuestionMap data={tags} />} {/* <-- line 2 for the real site */}
      </main>
    </div>
  );
}
