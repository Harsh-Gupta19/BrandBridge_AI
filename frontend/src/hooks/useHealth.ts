import { useQuery } from "@tanstack/react-query";

import { apiGet } from "../services/apiClient";
import type { HealthResponse } from "../types/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: ({ signal }) => apiGet<HealthResponse>("/health", { signal }),
  });
}
