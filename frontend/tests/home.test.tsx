import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { HomePage } from "../src/pages/HomePage";

describe("HomePage", () => {
  it("shows the project name and portal links", () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "BrandBridge AI" })).toBeInTheDocument();
    expect(screen.getByText("Creator Portal")).toBeInTheDocument();
    expect(screen.getByText("Brand Portal")).toBeInTheDocument();
  });
});
