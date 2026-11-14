import type { SubjectTags } from "./types";
import css2101 from "./data/css-2101.json";
import css1001 from "./data/css-1001.json";
import cse1071 from "./data/cse-1071.json";

const ds = css2101 as SubjectTags;
const pps = css1001 as SubjectTags;
const psuc = cse1071 as SubjectTags;

// paper.shrit.in lists first-year PPS and PSUC together on /browse/Year 1/subject/programming.
const programming: SubjectTags = {
  schema: 1,
  subject: "Programming",
  title: "PPS (CSS 1001) and PSUC (CSE 1071)",
  papers: [...pps.papers, ...psuc.papers].sort((a, b) => (b.date ?? "").localeCompare(a.date ?? "")),
};

// Register each tagged subject here, by course code or by the site's subject slug.
// Old course codes point at the same data.
const SUBJECTS: Record<string, SubjectTags> = {
  "CSS 2101": ds,
  "CSE 2122": ds,
  "CSS 1001": pps,
  "CSE 1071": psuc,
  PROGRAMMING: programming,
};

const norm = (code: string) =>
  decodeURIComponent(code).replace(/[_\s-]+/g, " ").trim().toUpperCase();

/** Tag data for a subject code like "CSS 2101" or a slug like "programming" (also accepts "CSS_2101" / URL-encoded). Null if untagged. */
export function getSubjectTags(code: string): SubjectTags | null {
  return SUBJECTS[norm(code)] ?? null;
}
