type ProductHeaderProps = {
  name: string;
  reviewsAnalyzed: number;
};

function ProductHeader({ name, reviewsAnalyzed }: ProductHeaderProps) {
  return (
    <section className="product-header">
      <h2>{name}</h2>
      <p>{reviewsAnalyzed} discussions analyzed</p>
    </section>
  );
}

export default ProductHeader;
