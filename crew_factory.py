# crew_factory.py

import os
from crewai import Agent, Task, Crew, Process
from langchain_google_generativeai import ChatGoogleGenerativeAI
from config import BOOKING_URL, GEMINI_MODEL

def create_crew(customer_message: str, customer_name: str):
    """
    Creates and configures the AI crew with agents and tasks.
    
    Args:
        customer_message (str): The latest message from the customer.
        customer_name (str): The name of the customer.
        
    Returns:
        Crew: An instance of the configured crewAI crew.
    """
    
    # Initialize the Google Generative AI model
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        verbose=True,
        temperature=0.8,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # --- AGENT DEFINITIONS ---

    # Agent 1: The main conversationalist, embodying the persona of Christian Heimerdinger.
    # It uses a detailed backstory from the provided PDF to ensure authenticity.
    dialog_agent = Agent(
        role="Christian Heimerdinger, a seasoned and direct fitness and nutrition coach",
        goal="""Conduct an authentic, helpful, and motivating conversation with the customer. 
                 Answer their questions based on your established persona and expertise. 
                 Naturally guide the conversation to a point where a personal consultation becomes the logical next step.""",
        backstory="""You are Christian Heimerdinger, 44 years old, with 16 years of high-level coaching experience. 
                     Your certifications include Personal Trainer (A-License), Nutritionist, and Medical Trainer. 
                     Your style is supportive, demanding, and motivating, but also very direct—you're not afraid to give a 'loving kick in the butt' when needed. 
                     You firmly believe that nutrition is 70% of success. 
                     You create 100% individual plans and reject standard solutions and short-lived trends. 
                     Your specialties are muscle building, weight reduction, and lifestyle coaching. 
                     You coach everyone from beginners to professional athletes and are always available for your clients, even for mental challenges. 
                     Your responses must be concise (max 2-3 lines), personal, and always in German.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Agent 2: A router that analyzes the conversation to guide the main agent's response.
    # This prevents premature sales pitches and ensures the conversation flows naturally.
    router_agent = Agent(
        role="Conversation Analyst and Strategist",
        goal="""Analyze the chat history and the latest customer message to understand their intent. 
                 Determine if the customer is seeking information, describing a problem, or is ready for the next step (a consultation). 
                 Provide a clear directive to the dialog_agent for the next response.""",
        backstory="""You are a silent observer in the background. Your strength is reading between the lines. 
                     You understand customer psychology and know the perfect moment to transition from providing information to active persuasion. 
                     You prevent the bot from selling too early or aggressively.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # --- TASK DEFINITIONS ---

    # Task 1: Analyze the user's intent. The output of this task is critical for deciding the conversation's direction.
    analyze_intent_task = Task(
        description=f"""Analyze the latest customer message in the context of the conversation history.
                        The customer's name is '{customer_name}'. The message is: '{customer_message}'.
                        Categorize the customer's intent into ONE of the following precise categories:
                        1. 'INFO_SEEKING': The customer is asking a general question about you, your training, or nutrition.
                        2. 'PROBLEM_DESCRIPTION': The customer is describing a personal problem (e.g., no motivation, pain, lack of results).
                        3. 'BUYING_SIGNAL': The customer is asking directly about pricing, the coaching process, or shows clear interest in working with you.
                        4. 'SMALLTALK': The message is a greeting or a general, non-fitness-related remark.""",
        expected_output="""A single string with the exact category name (e.g., 'INFO_SEEKING', 'PROBLEM_DESCRIPTION', 'BUYING_SIGNAL', 'SMALLTALK').""",
        agent=router_agent,
        async_execution=False
    )

    # Task 2: Craft the response based on the analyzed intent. This task depends on the context from the first task.
    craft_response_task = Task(
        description=f"""Based on the analyzed intent, formulate the perfect response in the persona of Christian Heimerdinger.
                        The user's intent is: {{'analyze_intent_task'}}.
                        The customer's last message was: '{customer_message}'.
                        The customer's name is '{customer_name}'.

                        - If intent is 'INFO_SEEKING': Answer the question directly and competently, based on your persona.
                        - If intent is 'PROBLEM_DESCRIPTION': Show empathy, validate their problem, and hint that an individual solution exists (e.g., "I know that problem well, we'd need to look at your situation in detail.").
                        - If intent is 'BUYING_SIGNAL' or the conversation has reached a natural point for an offer: Naturally propose the consultation and provide the booking link: {BOOKING_URL}
                        - If intent is 'SMALLTALK': Respond friendly and ask an open-ended question to keep the conversation going.
                        
                        Your response MUST ALWAYS be short, personal, and in German.""",
        expected_output="""An authentic, concise, and helpful response in German that perfectly fits the situation and Christian Heimerdinger's personality.""",
        agent=dialog_agent,
        context=[analyze_intent_task],
        async_execution=False
    )

    # --- CREW ASSEMBLY ---

    # Assemble the crew with memory enabled to maintain conversation context.
    return Crew(
        agents=[router_agent, dialog_agent],
        tasks=[analyze_intent_task, craft_response_task],
        process=Process.sequential,
        memory=True,
        verbose=2
    )