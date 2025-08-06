import logging
import os

import chainlit as cl

from diagram_service.application.commands.generate_diagram_command import (
    GenerateDiagramCommand,
)
from diagram_service.application.dtos.diagram_dtos import ChatRequest
from diagram_service.infrastructure.config.container import Container

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global container instance
container = None


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    global container

    logger.info("Starting Chainlit chat session...")

    # Initialize container
    container = Container()
    container.config.from_dict(
        {"gemini_api_key": os.getenv("GEMINI_API_KEY", "your-api-key-here")}
    )

    # Wire container
    container.wire(modules=["diagram_service.chainlit_app"])

    # Send welcome message
    await cl.Message(
        content="👋 Welcome to the Diagram Generation Assistant! I can help you create diagrams from natural language descriptions. Try asking me to create a diagram like 'Create a simple AWS architecture with an EC2 instance and an RDS database'."
    ).send()

    logger.info("Chainlit chat session started successfully")


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    global container

    try:
        user_message = message.content

        logger.info(f"Received message: {user_message}")

        # Create chat request
        chat_request = ChatRequest(message=user_message)

        # Get application service from container
        if container is None:
            # Initialize container if not already done
            container = Container()
            container.config.from_dict(
                {"gemini_api_key": os.getenv("GEMINI_API_KEY", "your-api-key-here")}
            )
            container.wire(modules=["diagram_service.chainlit_app"])

        diagram_service = container.diagram_application_service()

        # Process the message
        if _looks_like_diagram_request(user_message):
            # Generate diagram from description
            command = GenerateDiagramCommand(description=user_message)
            response = await diagram_service.generate_diagram_from_description(command)

            if response.success:
                # Send diagram response
                await cl.Message(
                    content=f"✅ {response.message}\n\nGenerated diagram specification:\n```json\n{response.specification}\n```"
                ).send()

                # If there's an image path, display it
                if response.image_path:
                    logger.info(f"Image path: {response.image_path}")
                    if os.path.exists(response.image_path):
                        logger.info(f"Image file exists at: {response.image_path}")
                        await cl.Message(
                            content="Here's your generated diagram:",
                            elements=[
                                cl.Image(path=response.image_path, name="diagram")
                            ],
                        ).send()
                    else:
                        logger.warning(
                            f"Image file does not exist at: {response.image_path}"
                        )
                        await cl.Message(
                            content="📝 Diagram specification generated successfully! The image would be created here."
                        ).send()
                else:
                    logger.warning("No image path returned from diagram service")
                    await cl.Message(
                        content="📝 Diagram specification generated successfully! The image would be created here."
                    ).send()
            else:
                await cl.Message(
                    content=f"❌ Failed to generate diagram: {response.error}"
                ).send()
        else:
            # Regular chat response - use LLM service
            try:
                logger.info("Attempting to get LLM service from container...")
                llm_service = container.llm_service()
                logger.info("LLM service obtained, generating chat response...")
                chat_response = await llm_service.generate_chat_response(user_message)
                logger.info(f"Generated chat response: {chat_response[:50]}...")
                await cl.Message(content=chat_response).send()
            except Exception as e:
                logger.error(f"Error generating chat response: {e}")
                logger.error(f"Error type: {type(e)}")
                # Fallback to simple response
                await cl.Message(
                    content="💬 I'm here to help you create architecture diagrams! Try asking me to 'Create a FastAPI + SQS architecture' or 'Generate an EC2 + RDS diagram' and I'll build one for you."
                ).send()

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await cl.Message(content=f"❌ Sorry, I encountered an error: {str(e)}").send()


def _looks_like_diagram_request(message: str) -> bool:
    """Check if the message looks like a diagram generation request."""
    # More specific keywords that indicate diagram generation intent
    diagram_verbs = ["create", "generate", "make", "build", "draw", "design", "show"]
    diagram_nouns = ["diagram", "architecture", "infrastructure"]

    message_lower = message.lower()

    # Check if message contains diagram-related verbs AND nouns/cloud terms
    has_diagram_verb = any(verb in message_lower for verb in diagram_verbs)
    has_diagram_noun = any(noun in message_lower for noun in diagram_nouns)
    has_cloud_terms = any(
        term in message_lower
        for term in [
            "aws",
            "azure",
            "gcp",
            "cloud",
            "ec2",
            "rds",
            "s3",
            "lambda",
            "vpc",
            "subnet",
        ]
    )

    # Must have a diagram verb AND (diagram noun OR cloud terms)
    return has_diagram_verb and (has_diagram_noun or has_cloud_terms)


@cl.on_chat_end
async def end():
    """Clean up when chat session ends."""
    global container

    logger.info("Ending Chainlit chat session...")

    # Cleanup
    if container:
        # Cleanup rendering service
        rendering_service = container.diagram_rendering_service()
        if hasattr(rendering_service, "cleanup"):
            rendering_service.cleanup()

    logger.info("Chainlit chat session ended")
