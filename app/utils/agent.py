import logging
import os
from dataclasses import dataclass
from typing import Any, Sequence, cast

from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential

def _configure_logging() -> None:
    # Keep default behavior quiet unless the user opts in.
    level_name = os.getenv("NEBULAE_LOG_LEVEL", "WARNING").upper()
    level = getattr(logging, level_name, logging.WARNING)
    logging.basicConfig(level=level)

    azure_identity_level_name = os.getenv("AZURE_IDENTITY_LOG_LEVEL")
    if azure_identity_level_name:
        azure_identity_level = getattr(logging, azure_identity_level_name.upper(), None)
        if isinstance(azure_identity_level, int):
            logging.getLogger("azure.identity").setLevel(azure_identity_level)


_configure_logging()


LOGGER = logging.getLogger(__name__)
DEFAULT_PROJECT_ENDPOINT = "https://fndry-nebulae-east.services.ai.azure.com/api/projects/project-nebulae"
DEFAULT_AGENT_NAME = "nebulae-agent"
DEFAULT_AGENT_VERSION = "9"


class AzureAuthenticationError(RuntimeError):
    pass


@dataclass(frozen=True)
class NebulaeAgentSettings:
    project_endpoint: str
    agent_name: str
    agent_version: str


def load_settings() -> NebulaeAgentSettings:
    return NebulaeAgentSettings(
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", DEFAULT_PROJECT_ENDPOINT),
        agent_name=os.getenv("NEBULAE_AGENT_NAME", DEFAULT_AGENT_NAME),
        agent_version=os.getenv("NEBULAE_AGENT_VERSION", DEFAULT_AGENT_VERSION),
    )


def create_credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def _format_auth_error(exc: Exception) -> str:
    return (
        "Azure authentication failed. Sign in with `az login`, restart VS Code if Azure CLI was installed or updated recently, "
        "or set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET. "
        "Set AZURE_IDENTITY_LOG_LEVEL=DEBUG for credential-chain details. "
        f"Original error: {exc}"
    )


class NebulaeAgentService:
    def __init__(self, settings: NebulaeAgentSettings | None = None):
        self.settings = settings or load_settings()
        self._project_client: AIProjectClient | None = None
        self._openai_client = None

    def _ensure_client(self):
        if self._openai_client is not None:
            return self._openai_client

        try:
            self._project_client = AIProjectClient(
                endpoint=self.settings.project_endpoint,
                credential=create_credential(),
            )
            self._openai_client = self._project_client.get_openai_client()
            return self._openai_client
        except ClientAuthenticationError as exc:
            LOGGER.exception("Failed to initialize Azure AI Foundry client")
            raise AzureAuthenticationError(_format_auth_error(exc)) from exc

    def build_agent_reference(self) -> dict[str, str]:
        return {
            "name": self.settings.agent_name,
            "version": self.settings.agent_version,
            "type": "agent_reference",
        }

    def ask(self, messages: Sequence[dict[str, str]]) -> str:
        client = self._ensure_client()

        try:
            response = client.responses.create(
                input=cast(Any, list(messages)),
                extra_body={"agent_reference": self.build_agent_reference()},
            )
        except ClientAuthenticationError as exc:
            LOGGER.exception("Azure authentication failed during Nebulae agent request")
            raise AzureAuthenticationError(_format_auth_error(exc)) from exc

        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text.strip()

        return "The Nebulae agent returned an empty response."


def main() -> None:
    service = NebulaeAgentService()
    response_text = service.ask([
        {"role": "user", "content": "Tell me what you can help with."},
    ])
    print(f"Response output: {response_text}")


if __name__ == "__main__":
    main()