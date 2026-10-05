import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import InsightList from "./insightlist";

describe("InsightList", () => {
  it("renders each word with its count", () => {
    render(
      <InsightList
        title="Top Positives"
        items={[
          { word: "great", count: 3 },
          { word: "nice", count: 1 },
        ]}
      />,
    );

    expect(screen.getByText("Top Positives")).toBeInTheDocument();
    expect(screen.getByText("great (3)")).toBeInTheDocument();
    expect(screen.getByText("nice (1)")).toBeInTheDocument();
  });
});
