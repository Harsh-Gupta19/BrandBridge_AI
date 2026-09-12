import { useParams } from "react-router-dom";

import { PagePlaceholder } from "../components/PagePlaceholder";

export function CampaignDetailPage() {
  const { id } = useParams();

  return (
    <PagePlaceholder
      title={`Campaign ${id ?? ""}`.trim()}
      description="Campaign details, requirements, recommendations, and proposal actions will be shown here."
    />
  );
}
