# Discorso presentazione

Good afternoon, everyone. My name is **Gabriele De Lucia**, and the work I am presenting today is my Master Thesis, entitled
**“Design and Evaluation of a Multimodal Embodied Conversational Agent for Digital Commensality.”**

Before diving into the technical aspects, I’d like to start from the human problem that inspired this project: **the global challenge of loneliness.**
This is more than just a passing sadness; it is now recognized as a **critical public health issue**. Loneliness affects 1 in 6 people worldwide as reported by the World Health Organization.

The best natural antidote to loneliness is often found in shared human rituals.
And one of them is **commensality** — the act of eating and drinking together.
Commensality is not just about nutrition; it’s about **social cohesion, emotional synchronization, and mutual support.**
When we share a meal, we feel better.

Unfortunately, modern life trends — from busy work schedules to smaller households — have led to a dramatic decline in this daily ritual.
More and more people are eating alone, seeking comfort and joy in digital distraction — they turn to their phones, the TV, or their computers. But this passive engagement fails to provide the real social support we need.

This fragmented attention, multiplied across millions of individuals, paints a clear picture of a **global crisis of connection.**
The screen, meant to connect us, has instead become a barrier — leaving us emotionally unfulfilled, and still alone.

And this is where the core problem lies.

So, we are faced with a fundamental question:
**Can technology be used to mediate meaningful social connection?**

If *digital distraction* is the problem, then perhaps *targeted, empathetic digital presence* could be the solution.
And this is the vision that gave birth to the project I will present today —
**Audrey, our Artificial Commensal Companion.**

---

### STATE OF THE ART

When we looked at previous research on digital commensality, we noticed two main approaches.

First, **passive co-eating**, where users watch pre-recorded videos of others eating. This offers a minimal sense of company, but no real interaction — it’s like having a TV on during dinner.

Second, **physical robots**, which can be expressive but are expensive, not very accessibile and not easy to deploy.

No existing system provided what we really wanted: a companion that was *interactive, expressive, real-time,* and *affordable.*

So we decided to build an **Embodied Conversational Agent**, based on the SAIBA framework, which provides a model for transforming psychological intent — “what the agent wants to express” — into synchronized verbal and nonverbal behavior. The overall architecture is divided into three fundamental, sequential blocks: Intent Planning, Behavior Planning, and Behavior Realization.

---

### ARCHITECTURE

To bring Audrey to life, we extended SAIBA with an additional first module: **the Perception Layer**, responsible for interpreting what the user says and does in real time.

Audrey’s architecture operates as a continuous feedback loop, composed of four layers.
To better understand this structure, we can think of Audrey as a real person: 

- she uses her senses to perceive the user.
- her brain understands the input and generates a verbal response.
- her internal system synchronizes that response with appropriate nonverbal behaviors.
- her body delivers the complete, multimodal output back to the user.

The first layer is **Perception**. Here we used **Faster Whisper** for fast speech recognition and **MediaPipe** for real-time gaze tracking. This layer transforms the raw data into valuable information.

The second layer is **Intent Planning**, which decides what to say and when to say it.
This layer includes a core module, called the Decider, responsible for selecting which action Audrey should perform based on the input received from the previous layer. When Audrey detects silence, the Decider activates a mechanism to keep the conversation alive through short “icebreakers” — but only when the user seems ready. Instead, when a message from the user is detected, the Decider forwards it to LLaMa 3.1, a large language model that generates natural and empathetic responses in real time.

The third layer is **Behavior Planning**. Once Audrey’s verbal response is ready, it is analyzed using TextBlob and WordNet to identify the most semantically and emotionally relevant words. The script then associates these keywords with corresponding gestures, postures, and facial expressions. Finally, everything is formatted into **Behavior Markup Language (BML)** — a type of script that defines which nonverbal behaviors Audrey will perform and when exactly they will occur during speech.

The **Behavior Realization Layer** is the fourth and final stage of our architecture.
It transforms the abstract multimodal descriptions written in BML into real 3D animations inside the Unity3D engine.
Using **CereVoice**, we achieve real-time synchronization between audio and lip movements. Facial animations are based on a blendshape implementation of the **Facial Action Coding System** (FACS). The **Final IK** library by RootMotion allows Audrey to move smoothly and naturally.

[DEMO 2 minuti]

---

### METHODOLOGY

To test Audrey’s impact, we conducted a study with 34 participants.

Before the main session, participants completed a baseline questionnaire. This gathered demographics and information about their Frequency of Tech Use and Commensality Habits, as well as psychological data using scales like:

PANAS, for their general emotional state (affect).
UCLA Loneliness Scale, to establish baseline loneliness.
Big Five Inventory (BFI), to capture core personality traits.

Next, each person ate a simple meal while interacting with Audrey for approximately 20 minutes.
We employed a mixed experimental design to assign participants to one of two conditions:

- a **Static Agent**, with a neutral conversational style, and
- a **Personalized Agent**, whose dialogue was adapted to each participant’s personality profile, measured through the Big Five Inventory. 

Immediately following the interaction, participants completed the PANAS scale again to capture their immediate emotional affect, along with an open-ended questionnaire regarding their overall experience.

---

### RESULTS

Let’s now move to the core of this thesis: the results from the preliminary user study to evaluate Audrey's impact.

Our primary finding, is the **Significant Reduction in Negative Affect (NA)**. Audrey significantly reduced negative emotional states across the entire user sample. This strong initial evidence confirms the positive influence of an ACC on emotional well-being.

Moreover, the efficacy was not uniform. The group receiving a **personalized conversational experience** reported a significantly greater reduction in Negative Affect compared to the group of the static version.

An important limitation to note is that the personalized intervention was significantly less effective for users with **high Neuroticism scores**. This highlights a specific design challenge, suggesting that future iterations for highly anxious individuals may require a completely different approach and emotional tone.

On the qualitative front, participants described the experience as "interesting", "fun" and 'neither embarrassing nor stressful. Also a significant majority expressed a strong willingness to dine with Audrey again. They highlighted the ACC's potential as a dependable companion for vulnerable populations, such as older adults, individuals living alone, or those in quarantine. 

Finally, we address a major ethical concern with what we call **The Human Connection Paradox**. Participants worried that an ACC might replace human interaction and, at the same time, expressed a renewed desire to "engage more" with real individuals. This suggests that rather than removing the need of real companionship, **the ACC can serve as a reflective catalyst**, reinforcing the value of human connection.

---

### CONCLUSIONS

However, scientific progress requires recognizing current limits. Our study has three main **Limitations**:

The evaluation was conducted on a **small sample** of 34 participants, which restricts the generalizability of our results to the wider target population.

The **Limited Duration** of just a single session prevents us from assessing crucial long-term effects.

Finally, despite our efforts, Audrey occasionally exhibited **delays** in responses and **difficulties** in fully grasping complex conversational context. 

This brings us to our plan for **Future Work**.

Technically, we are focused on improving **Performance**, meaning a reduction in Audrey's latency.

Secondly, we aim for significantly **Advanced Personalization**. We will move beyond static questionnaire data to develop models that personalize Audrey's dialogue dynamically. This includes integrating RAG (Retrieval-Augmented Generation) technology to equip Audrey with a long-term memory, allowing for truly meaningful conversations across multiple sessions.

Our last priority is to conduct **Longitudinal Studies** focusing on continuous, long-term use across a much larger dataset.

---

### A CLOSING THOUGHT

This project started with a simple question:
*Can a machine make us feel a little less alone?*

After months of research, design, and experimentation, I believe the answer is yes — but not because technology replaces people.
Audrey works because she reminds us of what truly matters: presence, empathy, and the power of being heard.

Thank you.