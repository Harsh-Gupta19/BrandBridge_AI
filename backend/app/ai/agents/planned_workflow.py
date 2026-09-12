from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedWorkflowNode:
    name: str
    responsibility: str


PLANNED_CREATOR_MATCHING_WORKFLOW: tuple[PlannedWorkflowNode, ...] = (
    PlannedWorkflowNode("START", "Receive a campaign brief and brand context."),
    PlannedWorkflowNode("Parse Campaign", "Convert natural language into structured requirements."),
    PlannedWorkflowNode(
        "Validate Requirements",
        "Check required fields and ask for missing information.",
    ),
    PlannedWorkflowNode("Search Creators", "Find candidate creators from marketplace data."),
    PlannedWorkflowNode("Retrieve Social Metrics", "Load permitted YouTube and Instagram metrics."),
    PlannedWorkflowNode(
        "Calculate ML Score",
        "Apply structured feature-based recommendation models.",
    ),
    PlannedWorkflowNode("Calculate Semantic Score", "Compare campaign and creator embeddings."),
    PlannedWorkflowNode("Rank Candidates", "Combine signals into an explainable ranked list."),
    PlannedWorkflowNode(
        "Retrieve Brand Knowledge using RAG",
        "Fetch relevant unstructured context.",
    ),
    PlannedWorkflowNode("Generate Explanation", "Explain why top creators were selected."),
    PlannedWorkflowNode("Human Approval", "Require brand approval before important actions."),
    PlannedWorkflowNode("Generate Proposal", "Assist with invitation or proposal text."),
    PlannedWorkflowNode("END", "Return final workflow output."),
)
