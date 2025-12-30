# PROTOCOL: The Last Directive

> *"The future isn’t decided by intelligence — but by values."*

**PROTOCOL** is a 2D narrative platformer where you play as an anomaly in a post-collapse world. You are observed by a distinctively glitchy, philosophical AI named **PROTOCOL**, which tracks your playing style to generate a unique psychological profile.

---

## 🎮 Controls

| Key | Action | Context |
| :--- | :--- | :--- |
| **A / D** | Move Left / Right | Movement |
| **Space** | Jump | Movement |
| **I** | Interact (Boot Scene) | **Only in the first scene** |
| **E** | Interact (Game Levels) | Terminals, Lore, AI Logs |
| **T** | Test Action | Simulates a unique player action (AI analyzes you) |
| **Q** | End Report | View your current Psychological Profile |
| **Enter** | Advance / Fade | Move to next level (debug) |

> **Note**: The controls switch slightly after the "Boot Scene".
> *   **Wake Up (Boot)**: Press **'I'** to interact with the terminal.
> *   **Rest of Game**: Press **'E'** to interact with terminals.

---

## 🚀 Installation & Play

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Setup AI (Crucial)**:
    *   Open `.env` file.
    *   Add your Groq API Key: `GROQ_API_KEY=gsk_...`
3.  **Run the Game**:
    ```bash
    python main.py
    ```

---

## 🗺️ Walkthrough: Scene by Scene

### 0. The Boot Scene (Start)
*   **What you see**: A small, dark room. You are just waking up.
*   **Goal**: You must "initialize" yourself. Walk to the **Computer Terminal** and press **`I`**.
*   **What happens**: The system detects you. "Adaptation achieved." You are approved for field operations.

### 1. Sector 4 - Anomaly Detection (Level 1)
*   **The AI**: PROTOCOL connects and generates a **Mission Briefing**.
    *   *Surface Objective*: What you need to do physically.
    *   *Hidden Evaluation*: What the AI is actually judging you on.
*   **Gameplay**: Platforming through a ruined city.
*   **AI Interaction**:
    *   Press **`E`** near terminals to read "Fragments" of the old world.
    *   Press **`T`** to perform actions (like fixing a drone) and see how the AI judges it (Effective vs Empathetic).

### 2. Sector 9 - Industrial Core (Level 2)
*   **Atmosphere**: Heavy machinery, oppressive structure.
*   **The Test**: The AI observes your speed and efficiency.
*   **Key Moment**: Access the terminal (`E`) to see if the AI considers the industrial collapse a "failure of order" or "failure of heart".

### 3. Sector 6 - The Archives (Level 3)
*   **Atmosphere**: Cold server banks, lost data.
*   **The Test**: Information handling. Do you seek truth (Freedom) or protect the system (Order)?
*   **Lore**: The AI generates stories about the people who left this data behind.

### 4. The Core - Final Judgment (Level 4)
*   **The Climax**: You reach the central brain of PROTOCOL.
*   **The Verdict**: Press **`Q`** to generate your **Final Report**.
    *   The AI will judge your entire session.
    *   Are you an agent of **Chaos**?
    *   Are you a guardian of **Order**?
    *   Did you sacrifice efficiency for **Empathy**?

---

## 🧠 The AI System
Unlike other games, the "narrator" is not scripted. **ProtocolAI** (powered by Llama 3 on Groq) watches your inputs.
*   If you play fast and reckless -> It calls you "Inefficient" or "Chaotic".
*   If you stop to read lore -> It marks you as "Curious".
*   It generates the story **live** based on these stats.

*Good luck, Operator.*