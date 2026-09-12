# LLM

Future responsibility:

- Natural-language campaign brief parsing
- AI-assisted proposal draft generation
- Match explanation generation where deterministic templates are insufficient
- Provider adapters for cloud LLM inference

LLM code should not live directly in API route functions. Routes should call services, and services should call this module when natural-language generation is genuinely required.
