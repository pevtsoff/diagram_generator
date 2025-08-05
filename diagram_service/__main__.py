#!/usr/bin/env python3
"""
Entry point for running the diagram service as a module.

Usage:
    python -m diagram_service [--mode=api|chainlit]

Examples:
    python -m diagram_service --mode=api
    python -m diagram_service --mode=chainlit
"""

import argparse
import logging
import sys
from pathlib import Path

import uvicorn

# Add the project root to the path so we can import diagram_service
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the diagram service."""
    parser = argparse.ArgumentParser(description="Diagram Generation Service")
    parser.add_argument(
        "--mode",
        choices=["api", "chainlit"],
        default="api",
        help="Service mode to run (default: api)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    if args.mode == "api":
        # Run FastAPI server
        logger.info(f"🚀 Starting Diagram Service API on {args.host}:{args.port}")
        uvicorn.run(
            "diagram_service.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info",
        )
    elif args.mode == "chainlit":
        # Run Chainlit app
        logger.info(f"🚀 Starting Diagram Service Chainlit on {args.host}:{args.port}")

        # Import and run the chainlit app

        # This would typically be handled by chainlit CLI
        # For now, we'll just show instructions
        logger.info("📝 To run Chainlit app, use:")
        logger.info(
            f"   chainlit run diagram_service/chainlit_app.py --port {args.port}"
        )
        logger.info("   or")
        logger.info(
            f"   python -m chainlit run diagram_service/chainlit_app.py --port {args.port}"
        )


if __name__ == "__main__":
    main()
