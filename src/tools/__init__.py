from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from browser import BrowserRuntime


def register_tools(mcp: Any, runtime: "BrowserRuntime", llm: Any) -> None:
    from .agent import register_agent_tools
    from .artifacts import register_artifact_tools
    from .interaction import register_interaction_tools
    from .navigation import register_navigation_tools
    from .observation import register_observation_tools

    register_observation_tools(mcp, runtime)
    register_navigation_tools(mcp, runtime)
    register_interaction_tools(mcp, runtime)
    register_artifact_tools(mcp, runtime)
    register_agent_tools(mcp, runtime, llm)
