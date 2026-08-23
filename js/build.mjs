import { bundle } from "./tools/bundle.mjs";
import { bundle_css } from "./tools/css.mjs";
import { node_modules_external } from "./tools/externals.mjs";

import fs from "fs";
import cpy from "cpy";

const componentDir = "node_modules/@awesome.me/webawesome/dist/components";
const catalog = fs
  .readdirSync(componentDir)
  .filter((name) => fs.existsSync(`${componentDir}/${name}/${name}.js`))
  .map(
    (name) =>
      `import "@awesome.me/webawesome/dist/components/${name}/${name}.js";`,
  )
  .join("\n");
const layoutFixes =
  '\nif (typeof document !== "undefined" && !document.querySelector("style[data-spaday-webawesome]")) { const s = document.createElement("style"); s.dataset.spadayWebawesome = ""; s.textContent = "wa-input::part(base),wa-select::part(combobox){box-sizing:border-box}wa-button{display:inline-flex}"; document.head.appendChild(s); }\n';

const BUNDLES = [
  {
    entryPoints: ["src/ts/index.ts"],
    plugins: [node_modules_external()],
    outfile: "dist/esm/index.js",
  },
  {
    stdin: { contents: catalog + layoutFixes, resolveDir: ".", loader: "js" },
    outfile: "dist/cdn/index.js",
  },
];

async function build() {
  fs.rmSync("dist", { recursive: true, force: true });
  fs.rmSync("../spaday_webawesome/extension", {
    recursive: true,
    force: true,
  });

<<<<<<< before updating
  await bundle_css("src/css/webawesome.css");
=======
  // Bundle css
  await bundle_css();
>>>>>>> after updating

  // Copy HTML
  await cpy("src/html/*", "dist/");

  // Copy images
<<<<<<< before updating
  fs.mkdirSync("dist/img", { recursive: true });
  await cpy("src/img/*", "dist/img");
=======
  if (fs.existsSync("src/img")) {
    fs.mkdirSync("dist/img", { recursive: true });
    await cpy("src/img/*", "dist/img");
  }
>>>>>>> after updating

  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

  // Copy servable assets to python extension (exclude esm/)
  fs.mkdirSync("../spaday_webawesome/extension", { recursive: true });
  await cpy("dist/**/*", "../spaday_webawesome/extension", {
    filter: (file) =>
      !file.relativePath.startsWith("esm/") &&
      !file.relativePath.startsWith("dist/esm/"),
  });
}

await build();
