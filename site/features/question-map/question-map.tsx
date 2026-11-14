"use client";

import { useMemo, useState } from "react";
import type { Difficulty, SubjectTags, TaggedPaper, TaggedQuestion } from "./types";

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

function paperLabel(p: { code: string; exam_type: string | null; date: string | null }, withCode = false) {
  const d = p.date ? new Date(p.date + "T00:00:00").toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "";
  return [withCode ? p.code : null, p.exam_type, d].filter(Boolean).join(" · ");
}

type Count = Record<Difficulty, number> & { n: number; marks: number };
const emptyCount = (): Count => ({ Easy: 0, Medium: 0, Hard: 0, n: 0, marks: 0 });

export function QuestionMap({ data, className = "" }: { data: SubjectTags; className?: string }) {
  const [topic, setTopic] = useState<string | null>(null);
  const [diff, setDiff] = useState<Difficulty | null>(null);
  const [paper, setPaper] = useState<string | null>(null);

  const mixedCodes = new Set(data.papers.map((p) => p.code)).size > 1;
  const label = (p: TaggedPaper) => paperLabel(p, mixedCodes);

  const rows: Row[] = useMemo(
    () =>
      data.papers.flatMap((p) =>
        p.questions.map((q) => ({ ...q, paperId: p.pdf_path, paperLabel: paperLabel(p, mixedCodes), pdf: p.pdf_path })),
      ),
    [data, mixedCodes],
  );

  // Every topic in the subject, most asked first; the order stays put while a paper is picked.
  const order = useMemo(() => {
    const m = new Map<string, number>();
    for (const r of rows) m.set(r.topic, (m.get(r.topic) ?? 0) + 1);
    return [...m.entries()].sort((a, b) => b[1] - a[1]).map(([t]) => t);
  }, [rows]);

  // Per-paper counts: grid[topic][paperId], each with its difficulty split and marks.
  const grid = useMemo(() => {
    const g = new Map<string, Map<string, Count>>();
    for (const r of rows) {
      const byPaper = g.get(r.topic) ?? new Map<string, Count>();
      const c = byPaper.get(r.paperId) ?? emptyCount();
      c[r.difficulty]++;
      c.n++;
      c.marks += r.marks ?? 0;
      byPaper.set(r.paperId, c);
      g.set(r.topic, byPaper);
    }
    return g;
  }, [rows]);

  // The bars follow the paper filter: all papers, or just the picked one.
  const topics = order
    .map((t) => {
      const total = emptyCount();
      for (const [pid, c] of grid.get(t) ?? []) {
        if (paper && pid !== paper) continue;
        for (const d of DIFFS) total[d] += c[d];
        total.n += c.n;
        total.marks += c.marks;
      }
      return [t, total] as const;
    })
    .filter(([, c]) => c.n > 0);
  const max = Math.max(1, ...topics.map(([, c]) => c.n));
  const cellMax = Math.max(1, ...[...grid.values()].flatMap((m) => [...m.values()].map((c) => c.n)));
  const picked = data.papers.find((p) => p.pdf_path === paper);

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
          <h2 className="text-base font-semibold">
            {picked ? `Topics in ${label(picked)}` : "How often each topic is asked"}
          </h2>
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
              <span className="text-right font-mono text-xs tabular-nums text-muted-foreground" title={`${c.marks} marks`}>
                {c.n} q
              </span>
            </button>
          ))}
        </div>
      </div>

      {data.papers.length > 1 && (
        <div className="rounded-xl border border-border bg-card p-4 sm:p-5">
          <h2 className="mb-1 text-base font-semibold">Per paper</h2>
          <p className="mb-3 text-xs text-muted-foreground">
            Questions on each topic in each paper. Pick a paper or a cell to filter.
          </p>
          <div className="-mx-1 overflow-x-auto px-1">
            <table className="w-full min-w-max border-separate border-spacing-1 text-sm">
              <thead>
                <tr>
                  <th className="sticky left-0 bg-card text-left text-xs font-medium text-muted-foreground">Topic</th>
                  {data.papers.map((p) => (
                    <th key={p.pdf_path} className="font-normal">
                      <button
                        type="button"
                        aria-pressed={paper === p.pdf_path}
                        onClick={() => setPaper(paper === p.pdf_path ? null : p.pdf_path)}
                        className={`w-full rounded-md px-2 py-1 text-xs leading-tight transition-colors ${
                          paper === p.pdf_path ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"
                        }`}
                      >
                        {label(p).split(" · ").map((part, k) => (
                          <span key={k} className="block whitespace-nowrap">
                            {part}
                          </span>
                        ))}
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {order.map((t) => (
                  <tr key={t}>
                    <th scope="row" className="sticky left-0 max-w-[10rem] truncate bg-card pr-2 text-left font-medium">
                      {t}
                    </th>
                    {data.papers.map((p) => {
                      const c = grid.get(t)?.get(p.pdf_path);
                      const on = topic === t && paper === p.pdf_path;
                      return (
                        <td key={p.pdf_path} className="p-0">
                          <button
                            type="button"
                            disabled={!c}
                            aria-pressed={on}
                            aria-label={`${t}, ${label(p)}: ${c?.n ?? 0} questions`}
                            title={
                              c
                                ? `${c.n} q · ${c.marks} marks · ${DIFFS.filter((d) => c[d]).map((d) => `${c[d]} ${d}`).join(", ")}`
                                : "none"
                            }
                            onClick={() => {
                              setTopic(on ? null : t);
                              setPaper(on ? null : p.pdf_path);
                            }}
                            className={`relative h-8 w-full min-w-12 rounded-md font-mono text-xs tabular-nums transition-shadow ${
                              c ? "text-foreground hover:ring-1 hover:ring-primary" : "text-muted-foreground/40"
                            } ${on ? "ring-2 ring-primary" : ""}`}
                          >
                            {c && (
                              <span
                                aria-hidden
                                className="absolute inset-0 rounded-md bg-primary"
                                style={{ opacity: 0.12 + (c.n / cellMax) * 0.5 }}
                              />
                            )}
                            <span className="relative">{c ? c.n : "·"}</span>
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
                <tr>
                  <th scope="row" className="sticky left-0 bg-card pr-2 text-left text-xs font-medium text-muted-foreground">
                    Total
                  </th>
                  {data.papers.map((p) => (
                    <td key={p.pdf_path} className="text-center font-mono text-xs tabular-nums text-muted-foreground">
                      {p.questions.length}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

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
            {label(p)}
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
