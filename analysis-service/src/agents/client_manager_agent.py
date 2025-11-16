from src.agents.base_agent import BaseAgent
from src.models.project import Interaction, AgentRole, ProjectBrief
from src.services.llm_service import mock_llm_service
from src.services.image_generation_service import mock_image_generation_service
from src.services.task_dispatcher import task_dispatcher
from src.services.database_service import db_service
from src.agents.contractor_agent import ContractorAgent
from src.agents.designer_agent import DesignerAgent
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class ClientManagerAgent(BaseAgent):
    """
    The Client Manager Agent is the primary interface with the user.
    It handles the initial interaction, quote analysis, and final presentation.
    """

    async def run(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Main run logic for the Client Manager Agent. It now also handles
        image generation based on style keywords.
        
        :param input_data: A dictionary containing context, 
                           e.g., {'project_id': '...', 'user_message': '...'}.
        :return: A dictionary containing the agent's response.
        """
        project_id = input_data.get("project_id")
        user_message = input_data.get("user_message", "")
        
        logger.info(f"ClientManagerAgent activated for project {project_id}.")

        # 1. Check for style keywords to trigger image generation
        style_keywords = ["北歐風", "工業風", "無印風", "侘寂風"]
        found_style = next((style for style in style_keywords if style in user_message), None)

        metadata = {}
        if found_style:
            image_prompt = f"A high-quality, photorealistic interior design concept of a living room in {found_style} style."
            image_response = await mock_image_generation_service.generate_image(prompt=image_prompt)
            metadata["image_url"] = image_response.get("image_url")

        # 2. Construct a prompt for the LLM for a conversational response
        prompt = (
            "You are an empathetic and professional interior design client manager. "
            f"The user's latest message is: '{user_message}'. "
            "Based on this, formulate a warm and insightful question to continue the conversation. "
            "If a style was mentioned, ask for feedback on the generated image."
        )

        # 3. Call the (mock) LLM service
        llm_response = await mock_llm_service.generate_response(
            prompt=prompt,
            context={"project_id": project_id, "user_message": user_message}
        )
        
        # 4. Format the response
        response_interaction = Interaction(
            agent=AgentRole.CLIENT_MANAGER,
            message=llm_response,
            metadata=metadata if metadata else None
        )
        
        return response_interaction.dict()

    async def finalize_brief(self, project_id: str, conversation_history: List[Interaction]) -> ProjectBrief:
        """
        Summarizes the conversation, generates the final ProjectBrief,
        and dispatches tasks to other agents.
        
        :param project_id: The ID of the current project.
        :param conversation_history: The full list of interactions.
        :return: A structured ProjectBrief object.
        """
        logger.info(f"Finalizing project brief for project {project_id}.")

        # 1. Construct a prompt to summarize the conversation
        history_str = "\n".join([f"{i.agent.value}: {i.message}" for i in conversation_history])
        prompt = (
            "You are a summarization expert. Based on the following conversation history, "
            "extract the key information and structure it into a Project Brief. "
            "Identify user profile, style preferences, key requirements, and analyze the original quote."
            f"\n\n--- CONVERSATION HISTORY ---\n{history_str}\n--- END HISTORY ---\n\n"
            "Please summarize this into a structured ProjectBrief."
        )

        # 2. Call the (mock) LLM service to get structured data
        structured_brief_data = await mock_llm_service.generate_response(
            prompt=prompt,
            context={"project_id": project_id, "task": "summarize"}
        )

        # 3. Create the Pydantic model
        project_brief = ProjectBrief(**structured_brief_data)
        
        logger.info(f"Successfully generated project brief for project {project_id}.")

        # 4. Dispatch tasks to other agents
        await task_dispatcher.dispatch_task(
            target_agent=AgentRole.CONTRACTOR,
            brief=project_brief
        )
        await task_dispatcher.dispatch_task(
            target_agent=AgentRole.DESIGNER,
            brief=project_brief
        )
        
        return project_brief

    async def present_final_results(self, brief: ProjectBrief) -> Dict[str, Any]:
        """
        Simulates waiting for other agents, gets their results, and presents them.
        
        :param brief: The project brief.
        :return: A final interaction object for the user.
        """
        logger.info(f"Presenting final results for project {brief.project_id}.")

        # 1. Simulate getting results from other agents
        contractor_agent = ContractorAgent()
        designer_agent = DesignerAgent()

        generated_quote = await contractor_agent.run(brief)
        final_rendering = await designer_agent.run(brief)

        # 2. Persist results for downstream consumption
        await db_service.update_project_with_quote(brief.project_id, generated_quote)
        await db_service.update_project_with_rendering(brief.project_id, final_rendering["image_url"])

        # 3. Prepare the final presentation message
        presentation_prompt = (
            "You are the client manager. The contractor and designer have finished their work. "
            "Present the final quote and rendering to the user in a warm and professional manner. "
            "Briefly explain what they are looking at."
        )
        presentation_message = await mock_llm_service.generate_response(
            prompt=presentation_prompt,
            context={"project_id": brief.project_id}
        )

        # 4. Format the final interaction
        final_interaction = Interaction(
            agent=AgentRole.CLIENT_MANAGER,
            message=presentation_message,
            metadata={
                "quote": generated_quote.model_dump(),
                "rendering_url": final_rendering["image_url"]
            }
        )

        return final_interaction.dict()
