# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My system covers unofficial and student-facing knowledge about Furman dining and campus food options. This knowledge is valuable because official dining pages explain meal plans, dining locations, menus, and services, but they do not fully capture what students actually experience, such as convenience, wait times, food quality, quick food options, dietary options, and first-year advice. The system helps users ask plain-language questions and receive grounded answers based on collected Furman dining documents and student comments.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Furman Dining official page | Official university page | https://www.furman.edu/dining/ |
| 2 | Daniel Dining Hall Virtual Tour | Official university page / transcript | https://www.furman.edu/virtual-campus-tour/daniel-dining-hall/ |
| 3 | Dining at Furman / Enrollment Services | Official university page | https://www.furman.edu/enrollment-services/enrollment-services/dining-at-furman/ |
| 4 | Furman Dining News | Official university page | https://www.furman.edu/dining/dining-news/ |
| 5 | The Beauty of Dining at Furman | Student-facing admissions blog post | https://www.furman.edu/admissions-aid/admission-blog/the-beauty-of-dining-at-furman/ |
| 6 | Food at Furman During a Pandemic | Student newspaper article | https://thepaladin.news/12892/arts-culture/food-at-furman-during-a-pandemic/ |
| 7 | Furman Dining Instagram | Social media profile | https://www.instagram.com/furman_dining/ |
| 8 | Furman Admissions Instagram Reel | Social media post / reel | https://www.instagram.com/reel/DSAwTE6kc6Y/ |
| 9 | Food allergy and accommodation information | Bon Appétit / Furman dining page | https://furman.cafebonappetit.com/mail-templates/2790/ |
| 10 | Student survey/interview notes | Local student notes | `data/student_survey_notes.txt` |

---


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**  
600–900 characters

**Overlap:**  
100–150 characters

**Why these choices fit your documents:**  
My documents include a mix of official Furman dining pages, student-facing articles, short social media descriptions, and informal student survey notes. I chose 600–900 characters because this size is long enough to preserve one complete idea, such as a student comment about quick food or an official description of dietary accommodations, but short enough to avoid mixing too many unrelated topics. I used overlap so that important information would not be lost if an idea continued across a chunk boundary.

Before chunking, I cleaned the documents by removing navigation text, repeated headers, cookie banners, legal/footer text, and unrelated website boilerplate. I kept substantive content such as dining descriptions, meal plan details, dining location names, student opinions, wait time comments, food quality comments, and dietary accommodation information.

**Final chunk count:**  
35 chunks


---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`


**Production tradeoff reflection:**
I used `all-MiniLM-L6-v2` because it is free, runs locally, and is fast enough for a small RAG project. It also avoids paid API costs and is simple to use with ChromaDB. If I were deploying this system for real users and cost was not a constraint, I would consider a stronger embedding model with better accuracy on informal student language, longer context support, lower latency, and better handling of campus-specific terms such as “DH,” “PDen,” “food points,” and “meal swipes.”

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The system prompt tells the model to answer only from the retrieved chunks. If the retrieved sources do not contain enough information, the model must respond with:

> I don't have enough information in the provided sources to answer that.

This prevents the model from answering based on general knowledge when the documents do not support the answer.

**How source attribution is surfaced in the response:**
The answer includes inline citations such as `[Source 1]` and `[Source 5]`. The system also displays a sources block built from retrieved metadata, including the source filename, chunk number, source title, URL or local file path, and distance score. The source list is generated from metadata rather than invented by the model.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the best place to eat when they are in a hurry? | Students usually prefer the closest or fastest option when they have limited time. The answer should also mention the PDen as useful for quick food or snacks between classes. | The system answered that Student 3 usually chooses whatever is closest and fastest. It also cited the PDen as a good place to grab something quick on the go or get a snack between classes. It added that Student 1 prefers a quicker option instead of sitting down for a full meal, but that source does not name a specific location. | Relevant | Accurate |
| 2 | What dining option seems most associated with wait time or crowding complaints? | Daniel Dining Hall is most associated with crowding, especially during lunch or busy meal times. | The system answered that Daniel Dining Hall seems most associated with wait time or crowding complaints. It cited student comments saying the dining hall can feel crowded during lunch, especially when students come between classes. It also mentioned students avoiding long lines when they only have a short amount of time. | Relevant | Accurate |
| 3 | What vegetarian, vegan, or gluten-free options are mentioned? | The answer should mention Root & Stem, plant-based dishes, gluten-free or allergy-safe meals, The Nook, made-without-gluten-containing-ingredients labels, and student comments about vegetarian options. | The system mentioned Root & Stem, plant-based dishes, meals prepared without top-9 allergens plus gluten, Meat & Potatoes near Root & Stem, a station for products made without gluten-containing ingredients, The Nook, salad or vegetable options, and vegan/vegetarian options mentioned by a student. | Partially relevant | Accurate |
| 4 | What do students say about overall food quality at Furman? | Students generally see Furman dining as useful for everyday meals, but food quality can vary by day, menu, or station. The answer should include mixed student opinions, not only official praise. | The system answered that Student 2 says food quality depends on the day, with some stations being good while some options feel repetitive. | Relevant | Accurate |
| 5 | What should a first-year student know about Furman dining? | First-year students should know that Daniel Dining Hall is a useful default option because it is central and predictable, but they should learn busy times, check menus, and try different dining options such as the PDen or Paddock. | The system answered that Daniel Dining Hall is convenient and central, making it easy to use. It also said lunch can feel crowded, but the dining hall has variety. It mentioned that the dining hall is a central dining space where students eat and build community, and that the menu rotates daily with made-from-scratch global cuisine. | Relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**  
What should a first-year student know about Furman dining?

**What the system returned:**  
The system returned a mostly useful answer. It said Daniel Dining Hall is convenient and central, lunch can feel crowded, and the dining hall has variety. It also mentioned that the DH is a central dining space with a rotating menu and vegan options.

**Root cause (tied to a specific pipeline stage):**  
This was a partial generation and retrieval issue. The system retrieved relevant sources, but the final answer leaned more toward general official information about Daniel Dining Hall instead of fully combining the practical first-year advice from the student survey notes. It did not clearly mention some expected advice, such as checking menus, learning busy times, and trying other dining options like the PDen or Paddock.

**What you would change to fix it:**  
I would add more first-year-specific student comments and possibly adjust the prompt to prioritize practical student advice when the question asks what a first-year student should know. I could also improve retrieval by adding metadata tags such as “first-year advice,” “quick food,” “busy times,” and “dining locations.”
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The planning spec helped me because it forced me to define my domain, source list, chunking strategy, retrieval approach, and evaluation questions before writing code. This made the implementation more organized and helped me prompt Claude with specific requirements instead of asking for a generic RAG system. It also gave me a clear standard for checking whether each milestone was complete.


**One way your implementation diverged from the spec, and why:**
One way my implementation diverged from the original spec was that I added a `--rebuild` option to the retrieval script. I added this after noticing that ChromaDB could reuse an old vector store, which might make retrieval results outdated if I changed the chunks. I also added both a command-line interface and a Gradio interface. The CLI made testing easier, while Gradio made the project easier to demonstrate in the final video.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->
**Instance 1**

- *What I gave the AI:*  
I gave Claude my Documents section, Chunking Strategy section, and Architecture diagram from `planning.md`. I also told it that my documents were local `.txt` files stored in the `data/` folder.

- *What it produced:*  
Claude produced an ingestion and chunking script that loads the documents, preserves raw text, cleans the documents, chunks them into 600–900 character chunks with overlap, saves source metadata, prints one cleaned document, prints sample chunks, and reports the total chunk count.

- *What I changed or overrode:*  
I checked the output manually to make sure all 10 documents loaded correctly and that the chunks were readable and self-contained. I also made sure the script matched my planned chunk size and overlap instead of using a generic fixed split.

**Instance 2**

- *What I gave the AI:*  
I gave Claude my Retrieval Approach section, Architecture diagram, and the location of my processed chunks in `output/chunks.json`.

- *What it produced:*  
Claude produced code that embeds chunks using `sentence-transformers/all-MiniLM-L6-v2`, stores them in ChromaDB, and retrieves the top 5 chunks for a query with source metadata and distance scores.

- *What I changed or overrode:*  
After testing, I asked Claude to add a `--rebuild` option so I could delete the old ChromaDB collection and re-embed all chunks from scratch. I also asked it to print full retrieved chunk text, metadata, source filenames, chunk numbers, and distance scores so I could debug retrieval quality more clearly.
