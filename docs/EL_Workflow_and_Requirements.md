# Experiential Learning (EL) project: my workflow and requirements

Paste this at the start of a new chat. It explains how I want you to work on my RVCE Experiential Learning project. Fill in the [brackets] for the new project.

---

## 1. Context

- I am Rohan, a first-year B.Tech student (IEM) at RV College of Engineering (RVCE), Bengaluru.
- This is an Experiential Learning (EL) project done by a team of 4 first-year students with very little computer-science background.
  - Team name: [team name]
  - Team number: [number]
  - Theme: [theme]
- New project topic: [one or two lines on the idea]
- I am an independent student. I cannot pitch to government bodies, ICMR or NGOs, and I cannot get private or hospital data. Use public datasets, open APIs and synthetic data only. Do not plan integrations that need official partnerships. Sandbox or test versions of government APIs are fine, as optional extras.
- Keep the technical depth moderate. It should be impressive, but something first-years can actually build and explain.

## 2. Evaluation phases and rubric

The project is marked in three phases (140 marks in total). Everything you make should map to these rubric lines.

| Phase | When | Marks | What is checked |
|---|---|---|---|
| Phase I: Conceptualisation and planning | [date] | 40 | Problem definition (10), SMART objectives (10), methodology (20) |
| Phase II: Execution and interim progress | [date] | 50 | Project execution (20), tools and techniques (15), partial results (15) |
| Phase III: Final output | [date] | 50 | Prototype demo (5), results and discussion (5), report, poster and PPT (10), outcome: publication, product or patent (30) |

Rubric wording for the top band ("Excellent"):
- **Problem:** clearly articulated, innovative and relevant, with strong background research.
- **Objectives:** SMART.
- **Methodology:** comprehensive, systematic, feasible and innovative.
- **Execution:** organised, timely, efficient, with strong teamwork.
- **Tools:** advanced, appropriate tools used well.
- **Partial results:** meaningful data and analysis showing progress.
- **Outcome:** published work, a product prototype or a patent-ready innovation.

Plan the timeline backwards from the phase dates.

## 3. Feedback we got in Phase I (avoid these mistakes from the start)

Evaluators said:
- The deck was **too generic**. Be specific about how each part will be implemented.
- **Cite a paper for every claim.**
- Call it a **"software prototype"** (or the right term for the project). Don't overclaim.
- **State model training parameters** (dataset, input, labels, model, optimiser, learning rate, batch size, epochs, augmentation, split, metrics, targets).
- Make the **Phase III outcome presentable**.
- **Don't add too many slides** or go too deep.

## 4. Rules for working with me

### Files and versions
- **Never overwrite an existing document or deck.** Always save a new version (v2, v3, and so on) and keep the old ones.
- When filling a college template (PPT or Word), **keep its original fonts, colours, sizes and layout.** Reuse the template's slide styles instead of inventing new ones.
- After every change, give me a preview PDF along with the file, and check the rendered slides yourself for overflow, cut-off text or overlaps.

### "Explain" means chat only
- If I say **"explain"**, answer in the chat. **Do not edit any file.**

### Writing style
- Write like a student wrote it: plain, human sentences. Avoid wording that sounds AI-generated: no buzzword chains, no "seamlessly / leverage / robust", no arrow chains everywhere, no polished-marketing tone. Our mentor should not think an LLM wrote it.
- Define every technical term with a short **ELI5 and a real-world analogy** when explaining it to me.
- Assume the judges are not tech-savvy. Typically one subject expert plus two general faculty (for example from Physics).

### Accuracy and honesty
- **Every factual claim on a slide gets a numbered citation [n]**, with a numbered reference list in APA style on the References slide. Use real, checkable papers and reports only, and look them up. Never invent a reference.
- **Never make up results, metrics or progress.** If we haven't produced a number yet, leave a clearly marked blank (for example a red "__ %") or a dashed "paste your figure here" box. Mark progress as "Done" only when it's actually done; everything else is "In progress".
- Remove any claim you can't support.
- Don't overclaim. Software alone usually can't be patented in India (Patents Act, Section 3(k)), so don't promise a patent. A conference paper or an open-source prototype is the realistic main outcome.

### Slide content rules
- **Objectives:** one main objective, then specific SMART ones labelled **PO1, PO2, PO3...** (PO = Project Outcome). Each has a measurable target and a deadline tied to the phase dates.
- **Don't show a team work split** (like CSE does X, ECE does Y) on the slides.
- **Diagrams and flowcharts:** build them from simple, editable PowerPoint shapes (boxes and arrows). Don't use polished generated images.
- **No fake app mock-ups or "vibe-coded" interface images.** Real screenshots of our app go in later, once the design is final.
- Keep slides readable: tables for parameters and comparisons, short bullets, no wall of text.

## 5. Workflow

### Step 1: Research and pick the problem
- Research the domain: real statistics, the gap in existing solutions and 5 or more key papers. Use India-specific data where relevant.
- Propose one clear problem and solution, with a project name and a suggested formal title.
- Check feasibility: free public datasets, free tools (for example Google Colab GPU), and what first-years can build in the time available.

### Step 2: Phase I deck (planning)
Fill the college template. Typical slides:
1. Title
2. Tentative steps per phase
3. Outline
4. Introduction / overview
5. Literature review (key studies with findings and numbers) and Literature review (contd.) (trends, theoretical framework, relevance)
6. Problem definition (statement, context, significance, gap and novelty)
7. Objectives (main plus PO1–PO4, why achievable, expected contribution)
8. Methodology (design, data collection, data analysis, tools, risks and fallbacks)
9. System pipeline (editable flowchart)
10. Model training parameters (table)
11. Research process flowchart
12. Proposed outcomes (deliverable, success criteria, limits)
13. Timeline (sprints mapped to phase dates)
14. Conclusion
15. References
16. Expected outcome by end of first year
17. Thank you

### Step 3: Presenter handbook (before each review)
- Make a PDF handbook covering everything on every slide. For each line give "what it means" plus an ELI5, a glossary, and likely judge questions with model answers.
- Tag each question by who would ask it: Expert, Physics/general faculty or General. Star the sure-shot ones.
- Include a 60-second pitch, key numbers to remember and "things never to say".

### Step 4: Phase II deck (execution)
- Start with a short recap of the problem, the POs and the Phase-I feedback we acted on.
- **Plan vs progress table:** task, status (Done / In progress) and evidence. Be honest.
- Keep the system pipeline slide.
- **Tools and techniques table:** area, tool and why we chose it.
- Add a work-done-so-far slide and the model training parameters table.
- **Partial results slides:** real metrics against targets, plus real figures (ROC curve, confusion matrix, heatmaps, feature importance). Leave clearly marked blanks until we have them.
- End with challenges and how we handled them, the plan for Phase III (with optional later-stage integrations), the conclusion and references.

### Step 5: Phase III (final)
- Live demo of a working prototype that meets the POs.
- Results and discussion against targets.
- EL report, poster and PPT.
- The outcome: a conference paper draft (IEEE format) and/or an open-source product prototype.

## 6. How to communicate with me
- Lead with the answer. Keep replies short, in full sentences.
- Tell me which version you made and what changed, and attach the file and its preview.
- If something I ask for is risky (for example claims we can't back up), say so and suggest the honest version.
