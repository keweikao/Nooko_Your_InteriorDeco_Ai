import React from 'react';

const StyleGuide = () => {
  return (
    <div className="p-8 bg-nooko-white text-nooko-charcoal min-h-screen">
      <h1 className="text-5xl font-playfair font-bold mb-8 text-nooko-charcoal">Nooko Design Style Guide</h1>

      <section className="mb-12">
        <h2 className="text-4xl font-playfair font-bold mb-6 text-nooko-charcoal">Colors</h2>
        <div className="flex flex-wrap gap-4">
          <div className="w-32 h-32 bg-nooko-white flex items-center justify-center rounded-lg shadow-md">
            <span className="text-sm font-medium">Nooko White</span>
          </div>
          <div className="w-32 h-32 bg-nooko-charcoal flex items-center justify-center rounded-lg shadow-md text-nooko-white">
            <span className="text-sm font-medium">Nooko Charcoal</span>
          </div>
          <div className="w-32 h-32 bg-nooko-terracotta flex items-center justify-center rounded-lg shadow-md text-white">
            <span className="text-sm font-medium">Nooko Terracotta</span>
          </div>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-4xl font-playfair font-bold mb-6 text-nooko-charcoal">Typography</h2>
        <div className="mb-8">
          <h3 className="text-3xl font-playfair font-bold mb-2 text-nooko-charcoal">Playfair Display (Headings)</h3>
          <p className="text-6xl font-playfair font-bold mb-2">Heading 1</p>
          <p className="text-5xl font-playfair font-bold mb-2">Heading 2</p>
          <p className="text-4xl font-playfair font-bold mb-2">Heading 3</p>
          <p className="text-3xl font-playfair font-bold mb-2">Heading 4</p>
        </div>
        <div>
          <h3 className="text-3xl font-sans font-bold mb-2 text-nooko-charcoal">Inter (Body Text)</h3>
          <p className="text-xl font-sans mb-2">The quick brown fox jumps over the lazy dog. (Extra Large)</p>
          <p className="text-lg font-sans mb-2">The quick brown fox jumps over the lazy dog. (Large)</p>
          <p className="text-base font-sans mb-2">The quick brown fox jumps over the lazy dog. (Base)</p>
          <p className="text-sm font-sans mb-2">The quick brown fox jumps over the lazy dog. (Small)</p>
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-4xl font-playfair font-bold mb-6 text-nooko-charcoal">Buttons</h2>
        <div className="flex gap-4">
          <button className="px-6 py-3 bg-nooko-terracotta text-white font-sans font-bold rounded-lg shadow-md hover:opacity-90 transition-opacity">
            Primary Button
          </button>
          <button className="px-6 py-3 border border-nooko-charcoal text-nooko-charcoal font-sans font-bold rounded-lg shadow-md hover:bg-nooko-charcoal hover:text-nooko-white transition-colors">
            Secondary Button
          </button>
        </div>
      </section>
    </div>
  );
};

export default StyleGuide;
