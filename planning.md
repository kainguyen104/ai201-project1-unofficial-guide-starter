# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

My domain is unofficial student knowledge about Furman dining and campus food options. This knowledge is valuable because official Furman dining pages explain meal plans, menus, dining locations, and general services, but they do not fully show what students actually experience day to day, such as convenience, wait times, food quality, vegetarian or gluten-free options, and which places students prefer when they are busy. This guide will help students ask practical questions about eating on campus and receive grounded answers from collected dining-related documents, student-facing sources, and student comments.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Furman Dining official page | Official overview of Furman dining services, meal plan information, and dining resources. | https://www.furman.edu/dining/ |
| 2 | Daniel Dining Hall Virtual Tour | Official Furman page describing Daniel Dining Hall, also called the DH, including made-from-scratch food and vegan, vegetarian, and gluten-free options. | https://www.furman.edu/virtual-campus-tour/daniel-dining-hall/ |
| 3 | Dining at Furman / Enrollment Services | Official page explaining meal plan portal information, meal plan changes, food points, and board swipe details. | https://www.furman.edu/enrollment-services/enrollment-services/dining-at-furman/ |
| 4 | Furman Dining News | Official page for dining events, dining calendar information, and campus dining updates. | https://www.furman.edu/dining/dining-news/ |
| 5 | The Beauty of Dining at Furman | Student-facing admissions blog post describing the dining hall, PDen, Paddock, meal swipes, food points, and student dining experience. | https://www.furman.edu/admissions-aid/admission-blog/the-beauty-of-dining-at-furman/ |
| 6 | Food at Furman During a Pandemic | Article from The Paladin discussing student experiences with Furman dining, including vegetarian and vegan options during the pandemic. | https://thepaladin.news/12892/arts-culture/food-at-furman-during-a-pandemic/ |
| 7 | Furman Dining Instagram | Social media source showing current dining options, dining events, and student-facing food updates from Furman Dining. | https://www.instagram.com/furman_dining/ |
| 8 | Furman Dining Instagram Reel | Social media post mentioning examples of campus dining options such as Indian tandoor, Mediterranean station, salad bars, wok grill, sushi, and noodle options. | https://www.instagram.com/reel/DSAwTE6kc6Y/ |
| 9 | Food allergy and accommodation information | Bon Appetit/Furman-related source with information about food allergy and celiac disease resources and accommodation contacts. | https://furman.cafebonappetit.com/mail-templates/2790/ |
| 10 | Student survey/interview notes | Short notes from 3–5 Furman students about dining convenience, wait times, food quality, healthy options, and first-year advice. | Local file: data/student_survey_notes.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 600–900 characters per chunk

**Overlap:** 100–150 characters of overlap between chunks

**Reasoning:** My sources include official dining pages, student-facing articles, and short student survey notes. I chose 600–900 characters because this size is long enough to keep one complete idea together, such as a student comment about wait times or a description of dining options, but short enough to avoid mixing too many unrelated topics. The overlap helps prevent important information from being lost when an idea continues into the next chunk.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

**Top-k:** 5 chunks per query

**Production tradeoff reflection:** 
I chose this embedding model because it is free, local, and recommended for the project. Retrieving 5 chunks should give the LLM enough context without adding too much unrelated information. For a real system, I would consider accuracy, speed, cost, context length, and how well the model handles informal student language.

If this system were deployed for real users, I would consider several tradeoffs when choosing an embedding model. A stronger embedding model might improve retrieval accuracy, especially for informal student language, slang, or short comments, but it could be slower or more expensive. I would also consider context length, multilingual support, latency, and whether the model works well with campus-specific terms such as “DH,” “PDen,” “food points,” and “meal swipes.”

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about the best place to eat when they are in a hurry? | The system should answer that students often prefer the fastest or closest option when they have limited time, and it should mention that Daniel Dining Hall may not always be ideal during crowded lunch periods. The answer should cite student survey/interview notes or another relevant source. |
| 2 | What dining option seems most associated with wait time or crowding complaints? | The system should identify Daniel Dining Hall or popular meal times as being associated with crowding and longer lines, based on student comments. It should explain that the issue is especially noticeable during lunch or busy periods. |
| 3 | What vegetarian, vegan, or gluten-free options are mentioned in the sources? | The system should mention that Daniel Dining Hall provides vegan, vegetarian, and gluten-free options if the official dining hall source is retrieved. It may also mention that students say vegetarian options exist but could have more variety. |
| 4 | What do students say about the overall food quality at Furman? | The system should summarize that students see Furman dining as generally useful and acceptable for everyday meals, but food quality can vary by day, station, and menu. It should not claim that every meal is excellent. |
| 5 | What should a first-year student know about Furman dining? | The system should say that Daniel Dining Hall is a useful default option because it is predictable and easy to use, but first-year students should learn busy times, check menus, and try different dining options during the first few weeks. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Some sources may be more official than unofficial. Official Furman pages describe dining services in a polished way, but they may not fully reflect student experience. To balance this, I need to include student survey/interview notes, public comments, and student-facing sources so the system can answer practical questions instead of only repeating official descriptions.

2. Retrieval may fail if students use different words from the query. For example, a user might ask about “quick food between classes,” while a source might use words like “convenient,” “fast,” “closest,” or “busy.” Because semantic search is not perfect, the system may retrieve a related but incomplete chunk. I will test retrieval with my evaluation questions and inspect the returned chunks before connecting generation.

3. Some important information may be split across chunk boundaries. For example, one paragraph might describe vegetarian options while the next paragraph explains student opinions about variety. The overlap should reduce this problem, but I will still inspect sample chunks before embedding.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

Document Ingestion (TXT files)
→ Cleaning (remove HTML and extra whitespace)
→ Chunking (600–900 characters with overlap)
→ Embedding (all-MiniLM-L6-v2)
→ Vector Store (ChromaDB with metadata)
→ Retrieval (top 5 chunks)
→ Generation (Groq LLM)
→ Grounded Answer with sources

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
I used Claude to help write the ingestion and chunking script. I will give Claude my Documents section, Chunking Strategy section, and Architecture diagram from this planning.md. I will also tell Claude that my documents are local `.txt` files stored in the `data/` folder. I expect Claude to produce a Python script that loads all documents, preserves the raw text, cleans the text, splits the documents into 600–900 character chunks with 100–150 character overlap, saves the chunks with source metadata, prints one cleaned document, prints 5 representative chunks, and prints the total number of chunks. I will verify the output by checking that all 10 documents load correctly, the cleaned text does not contain navigation or footer text, and the sample chunks are readable and self-contained.

**Milestone 4 — Embedding and retrieval:**
I used Claude to help write the embedding and retrieval script. I gave Claude my Retrieval Approach section, Architecture diagram, and the location of my processed chunks in `output/chunks.json`. Claude helped generate code that loads the chunks, embeds them with `sentence-transformers/all-MiniLM-L6-v2`, stores them in ChromaDB, and retrieves the top 5 chunks for each query. I also asked Claude to add a `--rebuild` option so I could delete the old vector store and re-embed all 35 chunks from scratch. I verified the output by running 3 evaluation questions and checking the source filename, chunk number, metadata, distance score, and full retrieved text.

**Milestone 5 — Generation and interface:**  
I used Claude to help connect my retrieval pipeline to Groq’s `llama-3.3-70b-versatile` model and build the query interface. I gave Claude my Architecture diagram, Retrieval Approach section, grounding requirement, and the fact that my retrieval function already returns the top 5 chunks with source metadata. I expected Claude to produce code that sends retrieved chunks to the LLM, generates answers using only the retrieved context, includes inline source citations, and refuses to answer when the sources do not contain enough information.
Claude first helped create `generate.py`, which supports command-line testing, interactive chat mode, and a grounding check mode. I verified it by testing three in-scope dining questions and one out-of-scope question about fall course registration. The out-of-scope question correctly returned: “I don't have enough information in the provided sources to answer that.”
I also used Claude to add a Gradio interface in `app.py` following the project instruction. I gave Claude the Gradio example from the assignment and asked it to reuse the existing answer function from `generate.py` instead of duplicating retrieval or generation logic. I verified the interface by running `python app.py`, opening `http://localhost:7860`, and checking that the answer box showed grounded answers while the sources box showed retrieved source metadata.
