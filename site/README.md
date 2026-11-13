# Question map: local preview

Next.js 15 (App Router) + Tailwind 4, the same stack as paper.shrit.in.

```
npm install
npm run dev
```
Open http://localhost:3000. It redirects to the CSS 2101 subject page with the question map under the paper list.
Use the **Theme** button to check light and dark.

- `features/question-map/`: **the feature**. This is the only folder that goes into the real site. See `../MERGE.md`.
- `app/browse/[...slug]/`: a rough stand-in for the real subject page (demo only).
- `app/globals.css`: stand-in shadcn tokens (demo only; the real site has its own).
