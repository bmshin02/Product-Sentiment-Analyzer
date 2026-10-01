import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import SentimentSummary from "./sentimentsummary";

function renderSummary(positive: number, neutral: number, negative: number) {
  render(
    <SentimentSummary
      positive={positive}
      neutral={neutral}
      negative={negative}
    />,
  );
}

function cardFor(label: string) {
  return screen.getByText(label).parentElement;
}

describe("SentimentSummary", () => {
  it("renders each fraction as a whole percentage", () => {
    renderSummary(0.71, 0.18, 0.11);

    expect(cardFor("Positive")).toHaveTextContent("71%");
    expect(cardFor("Neutral")).toHaveTextContent("18%");
    expect(cardFor("Negative")).toHaveTextContent("11%");
  });

  it("rounds to the nearest whole percentage", () => {
    renderSummary(0.714, 0.716, 0);

    expect(cardFor("Positive")).toHaveTextContent("71%");
    expect(cardFor("Neutral")).toHaveTextContent("72%");
  });

  it("handles the extremes 0 and 1", () => {
    renderSummary(1, 0, 0);

    expect(cardFor("Positive")).toHaveTextContent("100%");
    expect(cardFor("Neutral")).toHaveTextContent("0%");
  });
});
