# Data Structures question tagging rubric

For MIT Manipal CSS 2101 and legacy CSE 2122, third semester. Classify the question actually asked, including its constraints. This is an exam-task difficulty estimate in LeetCode-style categories, not an official LeetCode rating or a prediction of marks.

## Output contract and tagging procedure

Preserve every extracted question field. Add `topic`, `subtopic`, `difficulty`, `leetcode`, and `reason`, as required by SPEC.md. Use the exact topic names below and one listed subtopic where possible. `difficulty` must be `Easy`, `Medium`, or `Hard`. `leetcode` is an array of zero to three objects with integer `id`, exact `title`, and exact `slug` from the catalog. Prefer one strong match. Use `[]` when no useful match exists.

1. Identify the requested deliverable: definition, trace, implementation, design, optimization, or proof. Read the whole question before using keyword cues.
2. Select the structure or algorithm whose behavior is being assessed. A stack implemented with linked nodes is normally Stack; pointer rewiring in a linked list is Singly LL. BFS is Graphs even though it uses a queue.
3. Choose a specific subtopic. For a question with several inseparable tasks, choose the dominant assessed topic and mention secondary topics in `reason`. For equally weighted tasks, choose the first substantive topic. Do not split or invent question IDs in the tagging stage.
4. Rate the hardest required substantive task. Do not inflate difficulty for incidental terminology, repeated steps, marks, course outcomes, or the supplied cognitive-level label.
5. Select catalog problems by operation and constraints, then representation. Explain any partial analogy. Never use a catalog problem's official difficulty as the exam question's difficulty.
6. Write a short reason naming the actual task and the decisive difficulty factor. If extraction lost a diagram, code, or constraints, explicitly say so. Use the best supported provisional tag; do not invent missing content. If even the topic cannot be inferred, use `topic: "Unclear"`, `subtopic: "Insufficient text"`, provisional `difficulty: "Medium"`, `leetcode: []`, and a reason beginning `Needs review:`. This fallback is not a difficulty judgment and should be reviewed before display.

Example shape:

```json
{"topic":"Singly LL","subtopic":"Reversal","difficulty":"Easy","leetcode":[{"id":206,"title":"Reverse Linked List","slug":"reverse-linked-list"}],"reason":"Implement the standard iterative reversal using three pointers; no additional constraints."}
```

## Topic taxonomy

Keyword cues nominate candidates; they do not establish a tag by themselves. Match abbreviations and common spelling variants without case sensitivity. Interpret short cues such as LL, O, and Q only in context.

| Canonical topic | Subtopics | Keyword and task cues |
|---|---|---|
| Arrays/Strings | Indexing and address calculation; Traversal; Insertion/deletion; Two pointers; Sliding window; Prefix sums; String operations; Dense matrices | array, contiguous, base address, row-major, column-major, substring, palindrome, character, rotate, subarray; distinguish subsequence from contiguous substring |
| Recursion | Base case and call tracing; Recursive implementation; Divide and conquer; Backtracking | recursive, activation record, call stack, factorial, Fibonacci, Tower of Hanoi, permutations, subsets, backtrack; choose Complexity when only recurrence growth is requested |
| Sorting | Bubble sort; Selection sort; Insertion sort; Merge sort; Quick sort; Heap sort; Counting/radix/bucket sort; Stability and comparison | passes, partition, pivot, merge, sorted runs, stable, in-place, radix, counting; heap sort belongs here when sorting is the deliverable |
| Searching | Linear search; Binary search; Bounds and duplicates; Search in rotated arrays | sequential search, binary search, low/mid/high, first occurrence, lower bound, sorted array; searching a BST belongs to Trees |
| Stack | Push/pop/peek; Array/list implementation; Expression conversion; Expression evaluation; Balanced delimiters; Monotonic stack | LIFO, stack top, overflow, underflow, postfix, prefix, infix, parentheses, next greater; recursion stack alone is not enough |
| Queue | Linear queue; Circular queue; Deque; Priority queue; Implementation using stacks | FIFO, enqueue, dequeue, front, rear, wraparound, circular buffer, double-ended, input/output-restricted deque, priority scheduling; select Trees/Heap when heap mechanics are the assessed task |
| Singly LL | Traversal and search; Insertion/deletion; Reversal; Merge; Cycle detection; Intersection; Special pointer copying | singly, SLL, next pointer, head, tail, node, linked list without a stated subtype, slow/fast pointer; do not assume a cycle means an intentionally circular list |
| Doubly LL | Insertion/deletion; Bidirectional traversal; Reversal; Multilevel flattening; Cache integration | DLL, prev/previous and next, two links, predecessor pointer, bidirectional list; an LRU cache may require Hashing as a secondary topic |
| Circular LL | Traversal termination; Insertion/deletion; Split and concatenate; Josephus elimination | CLL, last node points to head, circular singly/doubly linked list, round robin, Josephus; circular array queues belong to Queue |
| Trees | Binary tree properties; Binary tree traversal; Binary tree construction; BST search; BST insertion/deletion; BST validation; AVL rotations; AVL insertion/deletion; Threaded tree traversal; Threaded tree insertion/deletion; Heap construction; Heap insertion/deletion; Heap order statistics | root, leaf, height, inorder/preorder/postorder, level order, BST, successor, AVL, balance factor, LL/RR/LR/RL rotation, thread/tag bit, min/max heap, sift/percolate, heapify; LL rotation is not linked list |
| Graphs | Representation; BFS; DFS; Components and reachability; Cycle detection; Topological sorting; Shortest paths; Minimum spanning tree; Disjoint sets | vertex, edge, adjacency list/matrix, directed, weighted, BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Prim, Kruskal, indegree, union-find; distinguish a graph adjacency matrix from sparse-matrix arithmetic |
| Hashing | Hash functions; Separate chaining; Linear/quadratic probing; Double hashing; Load factor and rehashing; Frequency lookup | hash table, collision, bucket, probe, load factor, open addressing, chaining, dictionary, frequency map; linked chains used to resolve collisions remain Hashing |
| Sparse matrix/Polynomial | Triplet representation; Sparse transpose; Sparse addition/multiplication; Polynomial representation; Polynomial addition/multiplication | sparse, nonzero, triplet/3-tuple, fast transpose, coefficient, exponent, polynomial linked list; dense matrix indexing remains Arrays/Strings |
| Complexity | Asymptotic notation; Loop analysis; Recurrence analysis; Best/average/worst case; Space and auxiliary space; Amortized analysis; Lower bounds | Big O, Omega, Theta, running time, count operations, recurrence, master theorem, amortized, aggregate, tight bound; use as primary only when analysis is the main deliverable |
| Data structure fundamentals | ADTs and interfaces; Representation tradeoffs; Static/dynamic allocation; Pointer and memory basics | abstract data type, primitive/nonprimitive, linear/nonlinear, malloc/free, allocation, pointer, representation choice; prefer a specific structure whenever stated |

Threaded trees, AVL trees, circular lists, and sparse/polynomial operations remain distinct subtopics even where the catalog has no direct match. Do not relabel them to force a LeetCode recommendation.

## Difficulty rubric

Assess the minimum correct solution demanded by the wording. Assume standard third-semester algorithms have been taught. Lengthy arithmetic or many input elements adds work, not algorithmic difficulty.

| Requested work | Default | Raise or lower only for these reasons |
|---|---|---|
| Define, compare basic properties, identify a structure | Easy | A required design justification across competing constraints may be Medium |
| Trace or hand-simulate a named algorithm on supplied data | Easy | Includes sorting passes, AVL rotations, hash probing, BFS/DFS, and expression evaluation. A separate required derivation or implementation is rated separately |
| Write a familiar single operation | Easy | Traversal, ordinary search, stack push/pop, queue enqueue/dequeue, singly-list insertion/reversal, basic recursive traversal |
| Write a standard algorithm with several invariants or cases | Medium | BST deletion, circular deque implementation, expression conversion with precedence, linked-list mergesort, cycle-entry detection, AVL insertion implementation |
| Combine familiar structures or adapt a known algorithm | Medium | Two-stack queue, hash plus DLL cache, bounded-memory processing with a known approach; the word “design” alone does not imply Hard |
| Derive an efficient algorithm under interacting constraints | Medium or Hard | Medium if a common pattern directly solves it. Hard if substantial new reasoning, several coupled invariants, or a difficult proof is required |
| Implement advanced optimization or complex balancing | Hard when warranted | Examples include a full AVL deletion implementation with rebalancing cases, or deriving an optimal monotonic-deque window algorithm and proving its bound without a supplied approach |
| Analyze runtime or space | Easy to Hard | Easy for direct loop counting or standard bounds; Medium for nontrivial recurrences/amortization; Hard for a substantial original lower-bound or amortized proof |

Decision rules:

- A pure trace is Easy even if the analogous coding problem is officially Hard.
- “Write an algorithm” requires implementation-level reasoning, not necessarily source code. Rate pseudocode and code equally.
- Explicit time/space requirements matter only when they change the necessary method. “O(n) reversal” is still a standard operation.
- Standard queue/deque implementations may be Medium because full/empty states and wraparound interact. One supplied enqueue operation is usually Easy.
- Choosing an appropriate known structure is usually Medium. Hard requires an identifiable obstacle, not an impressive topic name.
- For a boundary case, prefer the lower supported rating and explain the uncertainty. Do not manufacture constraints to justify Hard.

### Six worked examples

1. **AVL trace.** “Insert 30, 20, 10, 25, 28 into an empty AVL tree and show rotations.” Topic `Trees`, subtopic `AVL rotations`, difficulty `Easy`. The task supplies the operation and keys, so it is hand simulation. After the first three keys, a right rotation makes 20 the root; insertion of 28 produces a left-right adjustment inside the right subtree. `leetcode: []`: balanced BST construction from a sorted array is not AVL insertion.

2. **Standard list operation.** “Write an iterative algorithm to reverse a singly linked list using constant auxiliary space.” Topic `Singly LL`, subtopic `Reversal`, difficulty `Easy`. Maintain previous/current/next pointers; the standard algorithm is O(n) time and O(1) auxiliary space. Match #206 Reverse Linked List.

3. **Standard operation with cases.** “Write BST deletion handling a leaf, a node with one child, and a node with two children.” Topic `Trees`, subtopic `BST insertion/deletion`, difficulty `Medium`. Correctly reconnect the subtree and use a successor or predecessor for the two-child case; cost is O(h). Match #450 Delete Node in a BST.

4. **Combine structures.** “Design an LRU cache with get and put in O(1) average time.” Topic `Doubly LL`, subtopic `Cache integration`, difficulty `Medium`. A hash map locates nodes and a doubly linked list maintains recency; both must stay consistent during eviction. Mention Hashing in the reason. Match #146 LRU Cache. The word design does not alone justify Hard.

5. **Derive and justify optimization.** “Given an array and k, derive an O(n) algorithm for every window maximum using O(k) space; prove the bound.” Topic `Queue`, subtopic `Deque`, difficulty `Hard`. A naive scan costs O(nk); the required solution maintains a monotonic deque of indices, expires old indices, and proves that each index enters and leaves at most once. Match #239 Sliding Window Maximum. If the question supplies the deque algorithm and asks only to trace it, rate Easy; a familiar implementation without derivation may be Medium.

6. **Representation-specific operation.** “Write an algorithm to add two polynomials stored as exponent-sorted singly linked lists, omitting zero terms.” Topic `Sparse matrix/Polynomial`, subtopic `Polynomial addition/multiplication`, difficulty `Medium`. Merge terms by exponent, combine equal exponents, skip cancellation, and preserve remaining terms in O(m+n). `leetcode: []`: #21 merges nodes without coefficient combination, and #2 adds positional digits, so neither is a direct match. Keep a secondary Singly LL mention in the reason if useful.

## LeetCode selection policy

The following catalog contains exactly 60 distinct real problems. IDs are frontend problem numbers. Build links as `https://leetcode.com/problems/<slug>/`. The title links are primary-source references. Official LeetCode difficulties are intentionally omitted because the exam-task rating must be independent.

Rank matches in this order:

1. Same operation, representation, and important constraints. Recommend this first.
2. Same algorithmic pattern with a different representation. Include only if the analogy teaches the assessed skill; identify the difference in `reason`.
3. Same broad topic only. Return no match instead.

Do not invent generic problems called “AVL insertion”, “Threaded binary tree”, “Sparse polynomial addition”, or “Circular linked list deletion”. Catalog gaps are deliberate. A heap problem is not an AVL match; a circular deque is not a circular linked list. Complexity and sorting-property questions often need no coding recommendation. Backtracking catalog entries belong to Recursion when that is what the exam assesses.

### Arrays/Strings: 8

| Number | Title | Slug |
|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | `two-sum` |
| 26 | [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | `remove-duplicates-from-sorted-array` |
| 53 | [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | `maximum-subarray` |
| 88 | [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | `merge-sorted-array` |
| 125 | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | `valid-palindrome` |
| 189 | [Rotate Array](https://leetcode.com/problems/rotate-array/) | `rotate-array` |
| 344 | [Reverse String](https://leetcode.com/problems/reverse-string/) | `reverse-string` |
| 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | `longest-substring-without-repeating-characters` |

### Recursion: 4

| Number | Title | Slug |
|---|---|---|
| 509 | [Fibonacci Number](https://leetcode.com/problems/fibonacci-number/) | `fibonacci-number` |
| 70 | [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | `climbing-stairs` |
| 78 | [Subsets](https://leetcode.com/problems/subsets/) | `subsets` |
| 46 | [Permutations](https://leetcode.com/problems/permutations/) | `permutations` |

Climbing Stairs also supports recurrence/dynamic-programming practice. Do not recommend it for every recursive function.

### Sorting: 4

| Number | Title | Slug |
|---|---|---|
| 912 | [Sort an Array](https://leetcode.com/problems/sort-an-array/) | `sort-an-array` |
| 75 | [Sort Colors](https://leetcode.com/problems/sort-colors/) | `sort-colors` |
| 148 | [Sort List](https://leetcode.com/problems/sort-list/) | `sort-list` |
| 21 | [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | `merge-two-sorted-lists` |

#21 is a merge operation, not a complete sort. #912's efficiency requirement makes it a poor direct match for implementing quadratic bubble sort.

### Searching: 4

| Number | Title | Slug |
|---|---|---|
| 704 | [Binary Search](https://leetcode.com/problems/binary-search/) | `binary-search` |
| 35 | [Search Insert Position](https://leetcode.com/problems/search-insert-position/) | `search-insert-position` |
| 33 | [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | `search-in-rotated-sorted-array` |
| 34 | [Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | `find-first-and-last-position-of-element-in-sorted-array` |

### Stack: 5

| Number | Title | Slug |
|---|---|---|
| 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | `valid-parentheses` |
| 155 | [Min Stack](https://leetcode.com/problems/min-stack/) | `min-stack` |
| 150 | [Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | `evaluate-reverse-polish-notation` |
| 739 | [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | `daily-temperatures` |
| 84 | [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | `largest-rectangle-in-histogram` |

#150 matches postfix evaluation, not infix-to-postfix conversion.

### Queue, circular queue, deque, and priority queue: 6

| Number | Title | Slug |
|---|---|---|
| 232 | [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | `implement-queue-using-stacks` |
| 225 | [Implement Stack using Queues](https://leetcode.com/problems/implement-stack-using-queues/) | `implement-stack-using-queues` |
| 622 | [Design Circular Queue](https://leetcode.com/problems/design-circular-queue/) | `design-circular-queue` |
| 641 | [Design Circular Deque](https://leetcode.com/problems/design-circular-deque/) | `design-circular-deque` |
| 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | `sliding-window-maximum` |
| 23 | [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | `merge-k-sorted-lists` |

#225 is tagged Stack when stack behavior is the assessed deliverable. #23 can use a priority queue or divide-and-conquer merging; only claim a heap match when the question assesses that method.

### Singly LL: 7

| Number | Title | Slug |
|---|---|---|
| 206 | [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | `reverse-linked-list` |
| 141 | [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | `linked-list-cycle` |
| 142 | [Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/) | `linked-list-cycle-ii` |
| 19 | [Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | `remove-nth-node-from-end-of-list` |
| 160 | [Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/) | `intersection-of-two-linked-lists` |
| 234 | [Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | `palindrome-linked-list` |
| 138 | [Copy List with Random Pointer](https://leetcode.com/problems/copy-list-with-random-pointer/) | `copy-list-with-random-pointer` |

#141 and #142 detect a cycle; neither directly implements a circular-list ADT. A random pointer in #138 is not a DLL previous pointer.

### Doubly LL and list design: 3

| Number | Title | Slug |
|---|---|---|
| 707 | [Design Linked List](https://leetcode.com/problems/design-linked-list/) | `design-linked-list` |
| 430 | [Flatten a Multilevel Doubly Linked List](https://leetcode.com/problems/flatten-a-multilevel-doubly-linked-list/) | `flatten-a-multilevel-doubly-linked-list` |
| 146 | [LRU Cache](https://leetcode.com/problems/lru-cache/) | `lru-cache` |

#707 allows singly or doubly linked representation; specify the relevant representation in the reason. #146 is a combined hashing/list design problem, not a direct match for ordinary DLL insertion.

### Trees, BST, and heap: 12

| Number | Title | Slug |
|---|---|---|
| 94 | [Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/) | `binary-tree-inorder-traversal` |
| 144 | [Binary Tree Preorder Traversal](https://leetcode.com/problems/binary-tree-preorder-traversal/) | `binary-tree-preorder-traversal` |
| 145 | [Binary Tree Postorder Traversal](https://leetcode.com/problems/binary-tree-postorder-traversal/) | `binary-tree-postorder-traversal` |
| 102 | [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) | `binary-tree-level-order-traversal` |
| 104 | [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | `maximum-depth-of-binary-tree` |
| 98 | [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) | `validate-binary-search-tree` |
| 700 | [Search in a Binary Search Tree](https://leetcode.com/problems/search-in-a-binary-search-tree/) | `search-in-a-binary-search-tree` |
| 701 | [Insert into a Binary Search Tree](https://leetcode.com/problems/insert-into-a-binary-search-tree/) | `insert-into-a-binary-search-tree` |
| 450 | [Delete Node in a BST](https://leetcode.com/problems/delete-node-in-a-bst/) | `delete-node-in-a-bst` |
| 108 | [Convert Sorted Array to Binary Search Tree](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/) | `convert-sorted-array-to-binary-search-tree` |
| 215 | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | `kth-largest-element-in-an-array` |
| 703 | [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | `kth-largest-element-in-a-stream` |

#108 constructs a height-balanced BST; it does not implement AVL maintenance. #94 can teach inorder traversal but does not require a permanently threaded tree. #215 permits selection algorithms as well as heaps. Do not imply that any of these problems requires the course-specific representation unless the prompt says so.

### Graphs: 5

| Number | Title | Slug |
|---|---|---|
| 133 | [Clone Graph](https://leetcode.com/problems/clone-graph/) | `clone-graph` |
| 200 | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | `number-of-islands` |
| 207 | [Course Schedule](https://leetcode.com/problems/course-schedule/) | `course-schedule` |
| 547 | [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | `number-of-provinces` |
| 1971 | [Find if Path Exists in Graph](https://leetcode.com/problems/find-if-path-exists-in-graph/) | `find-if-path-exists-in-graph` |

#200 is grid connectivity. #207 covers directed-cycle detection/topological feasibility, not weighted shortest paths. This catalog has no direct MST or weighted shortest-path exercise; return `[]` for those tasks unless a genuine listed analogy exists.

### Hashing: 2

| Number | Title | Slug |
|---|---|---|
| 217 | [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | `contains-duplicate` |
| 242 | [Valid Anagram](https://leetcode.com/problems/valid-anagram/) | `valid-anagram` |

#1 also supports hash lookup. These are hash applications; they do not directly exercise probing, collision resolution, or hash-table resizing.

## Recommended implementation and review plan

Ranked approaches:

1. **Rubric-guided model classification plus deterministic validation.** Recommended for SPEC.md's `claude -p` batches. It can distinguish tracing from designing and interpret questions with several topics. Validate enums, question IDs, and every LeetCode triple against this catalog; require reasons and retain original text.
2. **Keyword candidate selection followed by model classification.** Useful if batches become expensive. Keep multiple candidates and let the full question decide. Cues such as “LL rotation” and “circular” make keyword-only decisions unreliable.
3. **Keyword-only classification.** Suitable as a baseline or fallback with explicit review flags. It cannot reliably distinguish task difficulty or match constraints.

Next steps for the builder:

1. Load this rubric into each per-paper tagging request and require the SPEC.md JSON shape.
2. Reject unknown topics, invalid difficulty strings, duplicate/missing question IDs, or LeetCode triples absent from the catalog. Retry malformed outputs without discarding source text.
3. Spot-check the six examples and a small set of actual exam questions, including a pure AVL trace, circular queue implementation, polynomial operation, and incomplete diagram question.
4. Review `Needs review:` outputs and broad or partial LeetCode matches before publishing. Keep the estimated exam difficulty visibly separate from any future official LeetCode difficulty field.

Source note: the catalog links point to LeetCode's original problem pages. During preparation, web search confirmed #430, #641, and #912 against official pages. A full catalog API check was blocked by the local network sandbox, so the remaining entries were not individually live-verified. No official difficulty claims are made here.
