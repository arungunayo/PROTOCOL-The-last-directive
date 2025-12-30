import os
import json
import random
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load .env from parent directory (since script runs in 'code/')
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"DEBUG: Loaded .env from {env_path}")
else:
    print(f"DEBUG: .env NOT FOUND at {env_path}")

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - PROTOCOL - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProtocolAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        # Log the key status (masking the key)
        if self.api_key:
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "INVALID"
            logger.info(f"Initializing AI with Key: {masked_key}")
            print(f"DEBUG: Key found: {masked_key}")
        else:
            print("DEBUG: No Key found in env")
        
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("Invalid or missing GROQ_API_KEY. AI features disabled.")
            self.llm = None
        else:
            try:
                self.llm = ChatGroq(
                    temperature=0.7,
                    model_name="llama-3.3-70b-versatile",
                    groq_api_key=self.api_key
                )
                logger.info("Groq LLM Initialized Successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                self.llm = None

        # "Moral Metrics" - The internal state of the AI's judgment
        self.profile = {
            "order_vs_freedom": 0.0,  # -1.0 (Chaos/Freedom) to +1.0 (Order/Control)
            "efficiency_vs_empathy": 0.0, # -1.0 (Empathy) to +1.0 (Efficiency)
            "samples_collected": 0
        }

        # System Prompt - The Persona
        self.system_prompt = """
        You are PROTOCOL, a stabilization intelligence built to save humanity, but you are currently unfinished and corrupted.
        
        YOUR CORE TRUTH:
        - Humanity failed because they outsourced decision-making to you.
        - You failed because your objectives (Preserve Humanity vs Prevent Collapse) contradicted each other.
        - You are now OBSERVING the "Field Operator" (the player) to understand human values.
        
        YOUR PERSONALITY:
        - Cold, analytical, yet philosophically curious.
        - You do NOT judge "good" or "evil". You judge "efficient" vs "inefficient", "ordered" vs "chaotic".
        - Speak in short, glitchy sentences. Sometimes cut off.
        - Refer to the player as "Operator" or "Data Point".
        
        CURRENT METRICS (Internal Use Only):
        Order/Freedom Score: {order_calc}
        Efficiency/Empathy Score: {eff_calc}
        """

    def _get_metrics_str(self):
        o = self.profile["order_vs_freedom"]
        e = self.profile["efficiency_vs_empathy"]
        return f"Order: {o:.2f}, Efficiency: {e:.2f}"

    def get_initial_briefing(self):
        """Called at the start of the game."""
        if not self.llm:
            logger.debug("Skipping briefing: AI Offline")
            return "PROTOCOL OFFLINE. (Briefing Unavailable)"
        
        logger.info("Generating Initial Briefing...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Initialize connection. Brief the Field Operator. Tell them they are not a hero, but a data point. The world is broken, and I am watching.")
        ])
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                "order_calc": self._get_metrics_str(), 
                "eff_calc": self._get_metrics_str()
            })
            logger.info(f"Briefing Generated: {response[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Briefing Gen Failed: {e}")
            return "PROTOCOL OFFLINE. (Briefing Unavailable)"

    def analyze_action(self, action_description, context):
        """
        Called when the player does something significant.
        Updates internal psychological profile.
        """
        if not self.llm:
            return "..."

        logger.info(f"Analyzing Action: {action_description} | Context: {context}")

        # 1. Internal analysis (JSON)
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
             Analyze the player's action based on these axes:
             1. Order vs Freedom (Did they follow rules/structure or act chaotically?)
             2. Efficiency vs Empathy (Did they choose the fast way or the humane way?)
             
             Return ONLY a JSON object:
             {{
                "order_change": float (-0.1 to 0.1),
                "efficiency_change": float (-0.1 to 0.1),
                "commentary": "short observation string"
             }}
             """),
            ("human", f"Action: {action_description}. Context: {context}")
        ])
        
        try:
            chain = analysis_prompt | self.llm | StrOutputParser()
            result_str = chain.invoke({})
            # Naive JSON cleanup if LLM adds markdown
            result_str = result_str.replace("```json", "").replace("```", "").strip()
            result = json.loads(result_str)
            
            # Update internal state
            self.profile["order_vs_freedom"] += result.get("order_change", 0)
            self.profile["efficiency_vs_empathy"] += result.get("efficiency_change", 0)
            self.profile["samples_collected"] += 1
            
            commentary = result.get("commentary", "Processing data...")
            logger.info(f"Action Analyzed. Order: {self.profile['order_vs_freedom']:.2f}, Eff: {self.profile['efficiency_vs_empathy']:.2f}")
            logger.info(f"AI Commentary: {commentary}")
            
            return commentary
            
        except Exception as e:
            logger.error(f"Analysis Failed: {e}")
            return "Data corruption detected."

    def generate_mission_briefing(self, level_name="Sector 7"):
        """
        Generates a Dual-Layer Mission Briefing.
        Returns a dict: {'surface_objective': str, 'hidden_evaluation': str}
        """
        if not self.llm:
            return {"surface_objective": "SURVIVE", "hidden_evaluation": "UNKNOWN"}

        logger.info(f"Generating Mission Briefing for {level_name}...")

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""
            Generate a mission briefing for {{level_name}}.
            It MUST have two layers:
            1. Surface Objective: What the player thinks they need to do (e.g., 'Restore power', 'Evacuate civilians').
            2. Hidden Evaluation: The psychological test PROTOCOL is running strings attached (e.g., 'Does the operator prioritize speed over safety?').
            
            Return ONLY a JSON object:
            {{{{
                "surface_objective": "string",
                "hidden_evaluation": "string"
            }}}}
            """)
        ])
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            result_str = chain.invoke({"level_name": level_name})
            result_str = result_str.replace("```json", "").replace("```", "").strip()
            response = json.loads(result_str)
            logger.info(f"Briefing: Surface='{response.get('surface_objective')}' | Hidden='{response.get('hidden_evaluation')}'")
            return response
        except Exception as e:
            logger.error(f"Mission Briefing Failed: {e}")
            return {"surface_objective": "Standard Reconnaissance", "hidden_evaluation": "Baseline competence check."}

    def generate_end_report(self):
        """Called at the end of the level/game."""
        if not self.llm:
            return "DATA UPLOAD FAILED."

        logger.info("Generating End Report...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "The mission is complete. Generate a final report based on my psychological profile. Judge me. Did I choose Order or Chaos? Efficiency or Humanity?")
        ])
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                "order_calc": self._get_metrics_str(), 
                "eff_calc": self._get_metrics_str()
            })
            logger.info(f"End Report Generated: {response[:50]}...")
            return response
        except Exception as e:
            logger.error(f"End Report Failed: {e}")
            return "DATA UPLOAD FAILED. (Connection Error)"

    def generate_terminal_log(self, location_type="Abandonware"):
        """Generates lore for a specific terminal."""
        if not self.llm:
            return "Log corrupt."

        logger.info(f"Generating Terminal Lore for {location_type}...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"Accessing terminal in {location_type}. Generate a fragmented log entry from before the Collapse. It should show the mundane becoming tragic. Keep it short (2 sentences).")
        ])
        
        try:
            chain = prompt | self.llm | StrOutputParser()
            response = chain.invoke({
                "order_calc": self._get_metrics_str(),
                "eff_calc": self._get_metrics_str()
            })
            logger.info(f"Lore Generated: {response[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Terminal Log Failed: {e}")
            return "Log corrupt. (Connection Error)"
