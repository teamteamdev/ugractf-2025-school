import * as fs from 'fs';

import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

const tex = new TeX({
  packages: ['base', 'ams']
});

const svg = new SVG({
  fontCache: 'none'
});

const mjDocument = mathjax.document('', {
  InputJax: tex,
  OutputJax: svg
});

/**
 * Renders a LaTeX formula to an image file
 * @param formula The LaTeX formula string to render
 * @param outputPath Path where the image should be saved
 */
export async function renderFormula(formula: string, outputPath: string): Promise<void> {
  try {
    const svg = mjDocument.convert(formula, { display: true });
    fs.writeFileSync(outputPath, adaptor.innerHTML(svg));
  } catch (error) {
    console.error('Error rendering formula:', error);
    throw new Error('Не удалось обработать формулу');
  }
}
