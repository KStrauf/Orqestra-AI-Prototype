"""Every error this system raises. One place, so failures are predictable."""

class OrqError(Exception):
    """Base for every OrqestraAI error.
    
    Why a base class: the CLI can catch OrqError and print a clean message,
    while any OTHER exception (a real bug) crashes loudly with a full traceback.
    That distinction matters - "your YAML is missing a key" should look nothing like 
    "the engine has a bug." """

class ManifestError(OrqError):
     """An agent.yaml is missing, malformed, or points at something that 
  doesn't exist."""

class TemplateError(OrqError):
    """An output template (like social_post.yaml) is missing or malformed."""

class ProviderError(OrqError):
    """A model call failed: bad key, model not found, Ollama not running, networl down. 
    Every provider adapter catches its own SDK's exceptions and re-raises THIS.
    That means the rest of the engine never has to know what an SDK is - a missing.
    Anthropic key and a stopped Ollama daemon produce the same shape of error."""

class GuardrailError(OrqError):
    """A tool tried to act on the outside world wothout human approval.
    
    This is not a bug. This is the safety system working. It should be loud.""" 