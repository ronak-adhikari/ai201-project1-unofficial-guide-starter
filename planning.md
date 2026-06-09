# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- Student reviews of CSULB professors in the Computer Science and Finance 
departments, sourced from Rate My Professors. This knowledge is valuable 
because it captures firsthand insight — grading style, workload, exam 
format, professor accessibility — that never appears in official course 
catalogs. It is otherwise scattered across hundreds of individual reviews 
with no way to ask cross-cutting questions. -->

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Susan Nachawati — CS | https://www.ratemyprofessors.com/professor/115586 |
| 2 | Rate My Professors | Ali Sharifian — CS | https://www.ratemyprofessors.com/professor/2300819 |
| 3 | Rate My Professors | Alireza Mehrnia — CS | https://www.ratemyprofessors.com/professor/2521315 |
| 4 | Rate My Professors | Jelena Trajkovic — CS | https://www.ratemyprofessors.com/professor/2493982 |
| 5 | Rate My Professors | Shannon Cleary — CS | https://www.ratemyprofessors.com/professor/1287692 |
| 6 | Rate My Professors | Chant Phengpis — Finance | https://www.ratemyprofessors.com/professor/934194 |
| 7 | Rate My Professors | Xiaoying (Cindy) Chen — Finance | https://www.ratemyprofessors.com/professor/917849 |
| 8 | Rate My Professors | Frank McEnulty — Finance | https://www.ratemyprofessors.com/professor/2088803 |
| 9 | Rate My Professors | Wikrom Prombutr — Finance | https://www.ratemyprofessors.com/professor/1781246 |
| 10 | Rate My Professors | Aslihan Salih — Finance | https://www.ratemyprofessors.com/professor/2626180 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300 characters

**Overlap:** 50 characters 

**Reasoning:** Rate My Professor reviews range from 1-2 sentences to a short paragraph, with most falling between 2-4 sentences. A 300-character chunk captures roughly one complete review or one meaningful thought without pulling in unrelated content from adjacent reviews. A 50-character overlap ensures that reviews are split across a chunk boundry still have enough shared context to be retrivable. Chinks that are too small risk being too vagure to ansewer any specific question; chucks that are too large risk burying a simple answer inside irrelevant text. Very short reviews (1-2) words will produce low-quality chunks.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2

**Top-k:** 5

**Production tradeoff reflection:** all-MiniLM-L6-v2 runs locally with no API cost and handles English text pretty well, which makes it a strong chouce for this project. In a real production system I would weigh seveal tradeoffs: context length limits (this model is fine for short reviews but would trucate longer documents), multilingual support, domain-sepcific accuracy, and latency (local models avoid network round trips but are slower on machines without a GPU). An API-hosted model from a different company could offer better accuracy at the cost of per-request pricing and data leaving the local machine.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

## Evaluation Plan

| # | Question | Expected Answer |
|---|----------|-----------------|
| 1 | What do students say about Professor Nachawati's organization? | Mixed reviews — most say her lectures and class format feel disorganized, though students note she herself is not an disorganized person. The disorganization is in the class structure rather than her personality. |
| 2 | How are Professor Xiaoying (Cindy) Chen's exams and what are they based on? | Exams are hard and include conceptual questions pulled from homework and math-based questions pulled from quizzes. Students find the questions difficult to learn despite being drawn from familiar material. |
| 3 | What is Professor Prombutr's overall class structure like? | Class consists of 4 exams with the lowest dropped from the final grade. No graded homework is assigned and exams are multiple choice and considered straightforward. |
| 4 | What do students say about Professor Sharifian's lectures and exams? | Lectures are well structured and easy to follow though some find them outdated. Overall considered pretty straightforward. |
| 5 | Which CS professor is most recommended for students taking a class for the first time? | Professor Jelena Trajkovic is highly recommended for first time students based on very positive reviews, good class structure, and a history of teaching entry level courses. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The embedding model may retrieve chunks that share similar words or topics with the query mbut don't contain the speific information the expected answer is based on.

2. Rate My Proffesor reviews that are 1-2 words in length or a single vague sentence don't contain enough context for the embedding model to produce a meaningful vector. These chunks may never be retrieved for relevant queries, amking those reviews effectivly invisible to the system. This could cause the system to miss signals expecially where every review matters for professors with less reviews overall. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
     
Document Ingestion     Chunking              Embedding + Vector Store
──────────────────     ────────────────      ────────────────────────
RMP review text   →    300 char chunks   →   all-MiniLM-L6-v2
(plain .txt files)     50 char overlap        sentence-transformers
                                              stored in ChromaDB
                                                      │
                                                      ▼
                                              Retrieval (top-k=5)
                                              ──────────────────
                                              semantic similarity
                                              search via ChromaDB
                                                      │
                                                      ▼
                                              Generation
                                              ──────────
                                              Groq LLM
                                              llama-3.3-70b-versatile
                                              grounded response
                                              with source citation  
  

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
Ingestion and chunking:** I will give Claude the Chunking 
Strategy section of this planning.md and ask it to implement a chunk_text() function that splits text using a chunk size of 300 characters and overlap of 50 characters. I will verify the output by printing sample chunks and confirming they match the expected size and overlap.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval 
Approach section of this planning.md and ask it to implement the embedding and ChromaDB storage pipeline using all-MiniLM-L6-v2. I will verify by querying the vector store manually and checking that returned chunks are relevant to the query.

**Milestone 5 — Generation and interface:**
I will give Claude the full planning.md and ask it to implement the Groq LLM generation step with a system prompt that enforces grounding. I will verify by running my 5 evaluation questions and checking responses against my expected answers.