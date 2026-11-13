"use client";

import { useMemo, useState } from "react";
import type { Difficulty, SubjectTags, TaggedQuestion } from "./types";

const DIFFS: Difficulty[] = ["Easy", "Medium", "Hard"];

// Semantic difficulty colours (LeetCode convention). Everything else uses the site's shadcn tokens.
const DIFF_STYLE: Record<Difficulty, { bar: string; pill: string; chipOn: string }> = {
  Easy: {
    bar: "bg-emerald-500",
    pill: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400",
    chipOn: "border-emerald-500 bg-emerald-500 text-white",
  },
  Medium: {
    bar: "bg-amber-500",
    pill: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
    chipOn: "border-amber-500 bg-amber-500 text-white",
  },
  Hard: {
    bar: "bg-rose-500",
    pill: "bg-rose-500/15 text-rose-700 dark:text-rose-400",
    chipOn: "border-rose-500 bg-rose-500 text-white",
  },
};

type Row = TaggedQuestion & { paperId: string; paperLabel: string; pdf: string };

function paperLabel(p: { exam_type: string | null; date: string | null }) {
  const d = p.date ? new Date(p.date + "T00:00:00").toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "";
  return [p.exam_type, d].filter(Boolean).join(" · ");
}

export function QuestionMap({ data, className = "" }: { data: SubjectTags; className?: string }) {
  const [topic, setTopic] = useState<string | null>(null);
  const [diff, setDiff] = useState<Difficulty | null>(null);
  const [paper, setPaper] = useState<string | null>(null);

  const rows: Row[] = useMemo(
    () =>
      data.papers.flatMap((p) =>
        p.questions.map((q) => ({ ...q, paperId: p.pdf_path, paperLabel: paperLabel(p), pdf: p.pdf_path })),
      ),
    [data],
  );

  const topics = useMemo(() => {
    const m = new Map<string, Record<Difficulty, number> & { n: number }>();
    for (const r of rows) {
      const c = m.get(r.topic) ?? { Easy: 0, Medium: 0, Hard: 0, n: 0 };
      c[r.difficulty]++;
      c.n++;
      m.set(r.topic, c);
    }
    return [...m.entries()].sort((a, b) => b[1].n - a[1].n);
  }, [rows]);
  const max = topics[0]?.[1].n ?? 1;

  const shown = rows.filter(
    (r) => (!topic || r.topic === topic) && (!diff || r.difficulty === diff) && (!paper || r.paperId === paper),
  );
  const groups = topics.map(([t]) => [t, shown.filter((r) => r.topic === t)] as const).filter(([, qs]) => qs.length);

  const chip = "rounded-full border border-border px-3 py-1 text-sm transition-colors hover:bg-muted";
  const chipOff = "bg-card text-foreground";

  return (
    <section className={`flex flex-col gap-6 ${className}`} aria-label="Questions by topic">
      <div className="rounded-xl border border-border bg-card p-4 sm:p-5">
        <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="text-base font-semibold">How often each topic is asked</h2>
          <div className="flex gap-3 text-xs text-muted-foreground">
            {DIFFS.map((d) => (
              <span key={d} className="flex items-center gap-1.5">
                <span className={`size-2.5 rounded-sm ${DIFF_STYLE[d].bar}`} />
                {d}
              </span>
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-0.5">
          {topics.map(([t, c]) => (
            <button
              key={t}
              type="button"
              onClick={() => setTopic(topic === t ? null : t)}
              aria-pressed={topic === t}
              className={`grid grid-cols-[minmax(6rem,11rem)_1fr_3rem] items-center gap-3 rounded-md px-2 py-1.5 text-left text-sm transition-colors hover:bg-muted ${
                topic === t ? "bg-muted shadow-[inset_3px_0_0_var(--color-primary)]" : ""
              }`}
            >
              <span className="truncate font-medium">{t}</span>
              <span className="flex h-3 overflow-hidden rounded-sm bg-muted" style={{ width: `${(c.n / max) * 100}%` }}>
                {DIFFS.map((d) =>
                  c[d] ? <span key={d} className={DIFF_STYLE[d].bar} style={{ width: `${(c[d] / c.n) * 100}%` }} title={`${c[d]} ${d}`} /> : null,
                )}
              </span>
              <span className="text-right font-mono text-xs tabular-nums text-muted-foreground">{c.n} q</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {DIFFS.map((d) => (
          <button key={d} type="button" aria-pressed={diff === d} onClick={() => setDiff(diff === d ? null : d)}
            className={`${chip} ${diff === d ? DIFF_STYLE[d].chipOn : chipOff}`}>
            {d}
          </button>
        ))}
        <span className="mx-1 h-5 w-px bg-border" />
        {data.papers.map((p) => (
          <button key={p.pdf_path} type="button" aria-pressed={paper === p.pdf_path} onClick={() => setPaper(paper === p.pdf_path ? null : p.pdf_path)}
            className={`${chip} ${paper === p.pdf_path ? "border-primary bg-primary text-primary-foreground" : chipOff}`}>
            {paperLabel(p)}
          </button>
        ))}
        <span className="ml-auto font-mono text-xs text-muted-foreground">
          {shown.length} of {rows.length} questions
        </span>
      </div>

      {groups.length === 0 && (
        <p className="py-10 text-center text-sm text-muted-foreground">No questions match these filters. Clear one to see more.</p>
      )}

      {groups.map(([t, qs]) => (
        <div key={t} className="flex flex-col gap-2">
          <h3 className="text-sm font-semibold">
            {t} <span className="font-mono font-normal text-muted-foreground">{qs.length}</span>
          </h3>
          {qs.map((q) => (
            <details key={q.pdf + q.qno} className="group rounded-lg border border-border bg-card">
              <summary className="grid cursor-pointer list-none grid-cols-[auto_1fr_auto] items-start gap-3 p-3 sm:p-4 [&::-webkit-details-marker]:hidden">
                <span className="font-mono text-sm text-primary">
                  Q{q.qno}
                  <span className="block text-[11px] text-muted-foreground">{q.paperLabel}</span>
                </span>
                <span className="min-w-0">
                  <span className="text-sm font-medium">{q.subtopic || q.topic}</span>
                  <span className="mt-0.5 line-clamp-2 text-sm text-muted-foreground group-open:hidden">{q.text}</span>
                </span>
                <span className="flex flex-col items-end gap-1">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${DIFF_STYLE[q.difficulty].pill}`}>{q.difficulty}</span>
                  {q.marks != null && <span className="font-mono text-xs text-muted-foreground">{q.marks} marks</span>}
                </span>
              </summary>
              <div className="flex flex-col gap-3 border-t border-dashed border-border px-3 pb-4 pt-3 sm:px-4">
                <p className="max-w-prose whitespace-pre-wrap break-words text-sm leading-relaxed">{q.text}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-xs text-muted-foreground">
                  {q.co && <span>{q.co}</span>}
                  {q.cognitive_level && <span>{q.cognitive_level}</span>}
                  <a href={encodeURI(q.pdf)} target="_blank" rel="noopener noreferrer" className="underline-offset-2 hover:underline">
                    Open paper ↗
                  </a>
                </div>
                {q.reason && (
                  <p className="text-xs text-muted-foreground">
                    Why {q.difficulty}: {q.reason}
                  </p>
                )}
                {q.leetcode.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {q.leetcode.map((l) => (
                      <a key={l.id} href={`https://leetcode.com/problems/${l.slug}/`} target="_blank" rel="noopener noreferrer"
                        className="rounded-md border border-primary/40 px-2.5 py-1 text-xs font-medium text-primary hover:bg-primary/10">
                        {l.id}. {l.title} ↗
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </details>
          ))}
        </div>
      ))}
    </section>
  );
}
