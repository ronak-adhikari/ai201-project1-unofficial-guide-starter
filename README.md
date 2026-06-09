# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers student reviews of professors in the Computer Science and Finance departments at California State University Long Beach (CSULB), sourced from Rate My Professors. This knowledge is valuable because it captures firsthand student insight — grading style, exam format, workload, professor accessibility — that never appears in official course catalogs or department websites. It is otherwise scattered across hundreds of individual reviews with no way to ask cross-cutting questions or get a synthesized answer about a specific professor's teaching style.


---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/115586 |
| 2 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2300819 |
| 3 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2521315 |
| 4 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2493982 |
| 5 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/1287692 |
| 6 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/934194 |
| 7 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/917849 |
| 8 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2088803 |
| 9 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/1781246 |
| 10 | Rate My Professors | Professor reviews | https://www.ratemyprofessors.com/professor/2626180 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 75 characters

**Why these choices fit your documents:** RMP reviews range from one sentence to a short paragraph, with most falling between 2–4 sentences. The pipeline first splits documents at review boundaries so that individual reviews stay intact rather than being cut mid-thought. The 500-character limit handles the rare case where a review is unusually long. A 75-character overlap ensures that content near chunk boundaries is not lost. Before chunking, the header metadata block at the top of each file (professor name, department, school, URL) is stripped so it does not pollute retrieval. Each chunk is also prefixed with the professor's name (e.g. "[Susan Nachawati] Review 3: ...") so the embedding carries professor identity and retrieval stays professor-specific even for generic queries. Very short reviews (under 30 characters) are filtered out entirely.

**Final chunk count:** 223 chunks across 10 documents

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers

**Production tradeoff reflection:** all-MiniLM-L6-v2 was chosen because it runs entirely locally with no API key or rate limits, making it ideal for a student project. It handles general English text well and produces embeddings quickly on a CPU. In a real production deployment, several tradeoffs would matter. First, context length: MiniLM supports up to 256 tokens, which is sufficient for short reviews but would silently truncate longer documents. Second, domain specificity: a model fine-tuned on student feedback or educational text would likely outperform a general-purpose model on this corpus. Third, multilingual support: MiniLM is English-only, which would be a limitation at a university with a large international student population. Fourth, latency and cost: an API-hosted model like OpenAI's text-embedding-3-small would offer higher accuracy but introduces per-request pricing, network latency, and the risk of data leaving the local environment. For this project, the local model was the right tradeoff.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt explicitly instructs the model with five rules: (1) answer only using information in the provided documents, (2) if the documents do not contain enough information respond with a specific refusal phrase, (3) always cite source documents using the format (Source: filename), (4) do not make up or infer information not explicitly stated, and (5) keep answers focused on what students actually said. The exact instruction is: "Answer ONLY using the information provided in the documents below. Do not use any outside knowledge. If the documents do not contain enough information to answer the question, respond with: 'I don't have enough information in the available reviews to answer that question.'"

**How source attribution is surfaced in the response:** Source attribution is enforced at two levels. First, the retrieved chunks are passed to the LLM with their source filename prepended (e.g. "[Source 1: nachawati_susan.txt]") so the model can reference them directly in its answer. Second, the unique source filenames from all retrieved chunks are collected programmatically after generation and displayed in a separate "Retrieved From" panel in the Gradio interface, regardless of what the LLM includes in its response text. This means attribution is guaranteed structurally, not dependent on the model choosing to cite sources.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Nachawati's organization? | Mixed reviews — most say lectures and class format feel disorganized, though students note she herself is not a disorganized person | Found disorganization theme correctly but only surfaced negative reviews; missed the nuance that she as a person is not disorganized, only the class structure is | Relevant | Partially accurate |
| 2 | How are Professor Xiaoying (Cindy) Chen's exams and what are they based on? | Exams are hard, conceptual questions from homework, math-based questions from quizzes, students find them difficult despite familiar material | Correctly identified conceptual and calculation-based exams pulled from homework and quizzes; noted mixed difficulty opinions | Relevant | Accurate |
| 3 | What is Professor Prombutr's overall class structure like? | 4 exams with lowest dropped, no graded homework, multiple choice exams, cheat sheet allowed | Accurately described 4 exams with lowest dropped, ungraded homework, cheat sheet, recorded lectures on Canvas | Relevant | Accurate |
| 4 | What do students say about Professor Sharifian's lectures and exams? | Lectures well structured but some say outdated; exams straightforward with study guides | Balanced mixed review — some call lectures worst, others well-structured; correctly identified study guide similarity to exams and no partial credit | Relevant | Accurate |
| 5 | Which CS professor is most recommended for students taking a class for the first time? | Professor Jelena Trajkovic based on positive reviews, good structure, entry level course history | Returned Shannon Cleary instead of Jelena Trajkovic; cited easy grading and clear teaching as reasons | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** Which CS professor is most recommended for students taking a class for the first time?

**What the system returned:** The system returned Shannon Cleary as the most recommended professor, citing reviews that describe her class as very easy, open-note exams, and minimal effort required for an A. It did not mention Jelena Trajkovic, who was the expected answer based on manual review of the RMP pages.

**Root cause (tied to a specific pipeline stage):** This is a retrieval failure caused by semantic mismatch at the embedding stage. The query phrase "recommended for first time students" does not appear verbatim in either professor's reviews. The embedding model found Shannon Cleary's chunks because her reviews contain words like "easy," "minimal effort," and "getting started with coding" which are semantically close to "beginner-friendly." Trajkovic's reviews use different vocabulary — "flipped classroom," "caring," "accommodating" — which scored lower similarity despite her being more explicitly recommended for entry-level students. The model retrieved surface-level semantic similarity rather than the underlying intent of the query.

**What you would change to fix it:** Two improvements would help. First, adding metadata tags to each chunk indicating the course level (introductory vs upper division) would allow filtering retrieval to only entry-level course reviews. Second, using a larger or domain-specific embedding model that better understands educational context would improve semantic matching between "first time students" and concepts like "flipped classroom" and "accommodating."

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the chunking strategy in planning.md before touching any code forced an early decision about chunk size that directly shaped the pipeline. Because the spec required explaining why the chunk size fits the documents, I had to think carefully about the structure of RMP reviews before writing chunk_text(). This led to the decision to split by review boundaries rather than fixed character counts — a better approach that would not have been obvious without the upfront planning. The spec acted as a forcing function for design decisions that would otherwise have been deferred until debugging.

**One way your implementation diverged from the spec, and why:** The spec specified a chunk size of 300 characters with 50 character overlap. During implementation the chunk size was increased to 500 characters after observing that 300-character chunks were producing mid-word cuts and fragments that carried too little semantic meaning for the embedding model. The distance scores on retrieval improved after increasing the chunk size, which confirmed that larger chunks carry more signal per embedding. The planning.md was updated to reflect this change as required by the spec instructions.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

## AI Usage

**Instance 1**

- *What I gave the AI:* The Chunking Strategy and Retrieval Approach sections from planning.md along with the pipeline architecture diagram, and asked Claude to implement the full ingestion, chunking, embedding, and retrieval pipeline in a single script.
- *What it produced:* A pipeline.py script with load_documents(), clean_text(), chunk_text(), build_vector_store(), and retrieve() functions using the specified chunk size, overlap, all-MiniLM-L6-v2, and ChromaDB.
- *What I changed or overrode:* The initial chunk_text() function used fixed character splitting which produced mid-word fragments. I directed Claude to rewrite it to split at review boundaries first (using "Review N:" markers) and only fall back to character splitting for unusually long reviews. I also increased chunk size from 300 to 500 after observing high retrieval distance scores.

**Instance 2**

- *What I gave the AI:* The grounding requirement from planning.md (answers from retrieved context only, with source attribution), the desired output format (answer + source list), and asked Claude to implement the generation function and Gradio interface.
- *What it produced:* A query.py file with a generate_answer() function using Groq's llama-3.3-70b-versatile, a five-rule system prompt enforcing grounding, and an app.py Gradio interface with separate answer and sources panels.
- *What I changed or overrode:* The initial system prompt used soft language ("try to answer only from the documents"). I directed Claude to make the grounding instruction strict and explicit, adding the specific refusal phrase the model should return for out-of-scope questions. I verified the out-of-scope behavior by testing a weather query before accepting the implementation.
