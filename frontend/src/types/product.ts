export type Product = {
  name: string;
  reviews_analyzed: number;
  sentiment: {
    positive: number;
    neutral: number;
    negative: number;
  };
  top_positives: string[];
  top_complaints: string[];
};
