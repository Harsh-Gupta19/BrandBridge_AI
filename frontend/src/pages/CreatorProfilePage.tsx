import { useParams } from "react-router-dom";

import { PagePlaceholder } from "../components/PagePlaceholder";

export function CreatorProfilePage() {
  const { id } = useParams();

  return (
    <PagePlaceholder
      title={`Creator ${id ?? ""}`.trim()}
      description="Creator profile, audience metrics, rate cards, and collaboration history will be shown here."
    />
  );
}
