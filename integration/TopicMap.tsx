"use client";
// Drop-in topic map for a subject page. React only, no other dependencies, styles inline
// so it can't clash with the site's CSS. Usage:
//   import tags from "@/data/tags/css-2101.json";
//   <TopicMap data={tags as SubjectTags} />
import { useMemo, useState } from "react";
import type { Difficulty, SubjectTags, TaggedQuestion } from "./types";

const DIFF_COLOR: Record<Difficulty, string> = { Easy: "#138a5b", Medium: "#b8740a", Hard: "#c4343f" };
type Row = TaggedQuestion & { paper: string; pdf: string };

export default function TopicMap({ data }: { data: SubjectTags }) {
  const [topic, setTopic] = useState<string | null>(null);
  const [diff, setDiff] = useState<Difficulty | null>(null);

  const rows: Row[] = useMemo(
    () => data.papers.flatMap(p => p.questions.map(q => ({ ...q, paper: `${p.exam_type ?? ""} ${p.date ?? ""}`.trim(), pdf: p.pdf_path }))),
    [data],
  );
  const counts = useMemo(() => {
    const m = new Map<string, number>();
    rows.forEach(r => m.set(r.topic, (m.get(r.topic) ?? 0) + 1));
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  }, [rows]);
  const max = counts[0]?.[1] ?? 1;
  const shown = rows.filter(r => (!topic || r.topic === topic) && (!diff || r.difficulty === diff));

  return (
    <section style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "grid", gap: 4 }}>
        {counts.map(([t, n]) => (
          <button key={t} onClick={() => setTopic(topic === t ? null : t)} aria-pressed={topic === t}
            style={{ display: "grid", gridTemplateColumns: "160px 1fr 40px", gap: 10, alignItems: "center", background: topic === t ? "rgba(43,84,201,.12)" : "transparent", border: 0, padding: "4px 6px", borderRadius: 6, cursor: "pointer", color: "inherit", font: "inherit", textAlign: "left" }}>
            <span>{t}</span>
            <span style={{ height: 10, width: `${(n / max) * 100}%`, background: "#2b54c9", borderRadius: 3 }} />
            <span style={{ opacity: 0.7, textAlign: "right" }}>{n}</span>
          </button>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {(["Easy", "Medium", "Hard"] as Difficulty[]).map(d => (
          <button key={d} onClick={() => setDiff(diff === d ? null : d)} aria-pressed={diff === d}
            style={{ border: `1px solid ${DIFF_COLOR[d]}`, color: diff === d ? "#fff" : DIFF_COLOR[d], background: diff === d ? DIFF_COLOR[d] : "transparent", borderRadius: 999, padding: "4px 10px", cursor: "pointer" }}>{d}</button>
        ))}
        <span style={{ marginLeft: "auto", opacity: 0.7 }}>{shown.length} of {rows.length} questions</span>
      </div>
      {shown.map(q => (
        <details key={q.pdf + q.qno} style={{ border: "1px solid rgba(127,127,127,.3)", borderRadius: 8, padding: "10px 14px" }}>
          <summary style={{ cursor: "pointer", display: "flex", gap: 10, flexWrap: "wrap", alignItems: "baseline" }}>
            <b>Q{q.qno}</b><span>{q.subtopic}</span>
            <span style={{ color: DIFF_COLOR[q.difficulty], fontWeight: 600 }}>{q.difficulty}</span>
            <span style={{ opacity: 0.6, marginLeft: "auto" }}>{q.paper}{q.marks != null ? ` · ${q.marks} marks` : ""}</span>
          </summary>
          <p style={{ whiteSpace: "pre-wrap" }}>{q.text}</p>
          {q.leetcode.length > 0 && (
            <p>{q.leetcode.map(l => (
              <a key={l.id} href={`https://leetcode.com/problems/${l.slug}/`} target="_blank" rel="noopener noreferrer" style={{ marginRight: 12 }}>{l.id}. {l.title} ↗</a>
            ))}</p>
          )}
        </details>
      ))}
    </section>
  );
}
