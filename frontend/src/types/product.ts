export type WordCount = {
  word: string;
  count: number;
};

export type Product = {
  id: string;
  name: string;
  reviews_analyzed: number;
  sentiment: {
    positive: number;
    neutral: number;
    negative: number;
  };
  top_positives: WordCount[];
  top_complaints: WordCount[];
};

export type ProductSearchResult = {
  id: string;
  name: string;
};
