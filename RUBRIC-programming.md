# First-year C programming tagging rubric

For MIT Manipal CSS 1001 (Programming for Problem Solving, PPS) and CSE 1071 (Problem Solving Using
Computers, PSUC), first year. Classify the question actually asked. Difficulty is an exam-task
estimate in LeetCode-style categories for a first-semester student, not an official LeetCode rating.

## Output contract

Return ONLY a JSON array, one object per question id given, each with: `id`, `topic` (exact name
from the table), `subtopic` (one listed where possible), `difficulty` (`Easy` | `Medium` | `Hard`),
`leetcode` (0 to 2 objects `{ "id", "title", "slug" }`, taken only from the catalog below; `[]` when
nothing fits, which is common here) and `reason` (one or two sentences naming the task and what
decides its difficulty).

1. Identify the deliverable: explanation, flowchart/algorithm, trace/output prediction, or a program.
2. Pick the C construct or concept being assessed, not every construct the program happens to use.
   A program that reads an array and sums it is Arrays; one whose point is a pointer to the array is
   Pointers; a menu-driven program built from functions is Functions.
3. For a question with sub-parts on different topics, choose the one carrying more marks or, if equal,
   the first, and mention the other in `reason`.
4. If the text is too garbled to tell, use `topic: "Unclear"`, `subtopic: "Insufficient text"`,
   `difficulty: "Medium"`, `leetcode: []`, and a reason starting `Needs review:`.

## Topic taxonomy

| Topic | Subtopics | Cues |
|---|---|---|
| Computer fundamentals | Computer organization; Operating system; Number systems; Computer languages; Compilation process; Cyber security and ethics | CPU, memory, input/output, OS role, binary/hex conversion, machine/assembly/high-level language, compiler, linker, cybercrime |
| Algorithms & flowcharts | Algorithm writing; Flowchart design; Pseudocode | "algorithm", "flowchart", step 1/step 2, symbols |
| Operators & expressions | Precedence and associativity; Increment/decrement; Bitwise operators; Type conversion; Output prediction | x++ vs ++x, %, \|, &, ^, <<, casting, "evaluate the expression", "what is the output" |
| Decision making | if / else-if; Nested if; switch | grade, commission, vowel check, menu via switch |
| Loops | while; do-while; for; Nested loops and patterns; break / continue; Number problems | print odd numbers, digit sum, reverse number, palindrome/Armstrong/prime checks with loops, patterns |
| Arrays | 1D array operations; Searching; Sorting; Array functions | read/print array, max/min, sum of even elements, linear/binary search, bubble/selection sort |
| Matrices (2D arrays) | Matrix input/output; Matrix arithmetic; Transpose; Row/column operations | M x N matrix, add/multiply matrices, row-wise sum, diagonal |
| Strings | String library functions; Character classification; String manipulation | strcpy, strcat, strlen, strcmp, count vowels/digits, remove characters, reverse/palindrome string |
| Functions | Defining and calling; Parameter passing; Call by value vs reference; Menu-driven programs; Storage classes | "using functions", prototype, return value, nested function calls, scope |
| Recursion | Recursive functions; Recursive search; Recursion vs iteration | "recursive", factorial, Fibonacci, recursive binary search, sum of n terms recursively |
| Pointers | Pointer basics; Pointer arithmetic; Pointers and arrays; Pointers and strings; Pointers to structures | `*`, `&`, "using pointers only", pointer to an array, swap via pointers |
| Structures | Structure definition; Array of structures; Nested structures; Structures and functions; Unions | struct, records (student, account, census, product), union |
| File handling | Opening modes; Reading and writing; File functions; Copy/merge files | fopen, fclose, fprintf, fscanf, putw, feof, "r", "w", "a" |

Topic precedence when several fit: Recursion over Functions when recursion is required; Pointers over
Arrays/Strings when "using pointers" is the point; Structures over Arrays for arrays of records;
File handling over everything else when files are the deliverable.

## Difficulty rubric (first-year scale)

| Requested work | Default |
|---|---|
| Explain a concept, list types, draw a diagram | Easy |
| Predict the output of an expression or short code; trace a sort or search on given data | Easy |
| Flowchart/algorithm, or a program with one loop or one decision | Easy |
| Program with nested loops, a 2D array, string processing by hand, or several functions | Easy, or Medium if several cases interact |
| Menu-driven program over records, structure arrays with search/sort, file merging with checks, recursion that isn't a textbook formula | Medium |
| Needs a non-obvious algorithm or coupled invariants beyond first-year material | Hard (rare) |

Long programs with many required features add work, not difficulty: rate the hardest single idea.

## LeetCode catalog

Only these real problems may appear in `leetcode`. Build links as `https://leetcode.com/problems/<slug>/`.

| id | title | slug |
|---|---|---|
| 1 | Two Sum | two-sum |
| 7 | Reverse Integer | reverse-integer |
| 9 | Palindrome Number | palindrome-number |
| 13 | Roman to Integer | roman-to-integer |
| 26 | Remove Duplicates from Sorted Array | remove-duplicates-from-sorted-array |
| 27 | Remove Element | remove-element |
| 35 | Search Insert Position | search-insert-position |
| 48 | Rotate Image | rotate-image |
| 50 | Pow(x, n) | powx-n |
| 54 | Spiral Matrix | spiral-matrix |
| 58 | Length of Last Word | length-of-last-word |
| 66 | Plus One | plus-one |
| 67 | Add Binary | add-binary |
| 69 | Sqrt(x) | sqrtx |
| 75 | Sort Colors | sort-colors |
| 88 | Merge Sorted Array | merge-sorted-array |
| 118 | Pascal's Triangle | pascals-triangle |
| 125 | Valid Palindrome | valid-palindrome |
| 136 | Single Number | single-number |
| 169 | Majority Element | majority-element |
| 191 | Number of 1 Bits | number-of-1-bits |
| 202 | Happy Number | happy-number |
| 204 | Count Primes | count-primes |
| 217 | Contains Duplicate | contains-duplicate |
| 231 | Power of Two | power-of-two |
| 242 | Valid Anagram | valid-anagram |
| 258 | Add Digits | add-digits |
| 263 | Ugly Number | ugly-number |
| 268 | Missing Number | missing-number |
| 283 | Move Zeroes | move-zeroes |
| 344 | Reverse String | reverse-string |
| 345 | Reverse Vowels of a String | reverse-vowels-of-a-string |
| 371 | Sum of Two Integers | sum-of-two-integers |
| 387 | First Unique Character in a String | first-unique-character-in-a-string |
| 412 | Fizz Buzz | fizz-buzz |
| 461 | Hamming Distance | hamming-distance |
| 485 | Max Consecutive Ones | max-consecutive-ones |
| 509 | Fibonacci Number | fibonacci-number |
| 704 | Binary Search | binary-search |
| 709 | To Lower Case | to-lower-case |
| 728 | Self Dividing Numbers | self-dividing-numbers |
| 867 | Transpose Matrix | transpose-matrix |
| 912 | Sort an Array | sort-an-array |
| 917 | Reverse Only Letters | reverse-only-letters |
| 1108 | Defanging an IP Address | defanging-an-ip-address |
| 1281 | Subtract the Product and Sum of Digits of an Integer | subtract-the-product-and-sum-of-digits-of-an-integer |
| 1295 | Find Numbers with Even Number of Digits | find-numbers-with-even-number-of-digits |
| 1480 | Running Sum of 1d Array | running-sum-of-1d-array |
| 1572 | Matrix Diagonal Sum | matrix-diagonal-sum |
| 1672 | Richest Customer Wealth | richest-customer-wealth |
| 2011 | Final Value of Variable After Performing Operations | final-value-of-variable-after-performing-operations |

Explanations, flowcharts, file handling, structures and computer fundamentals usually have no match:
use `[]` rather than forcing one.
