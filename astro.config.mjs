import { cpSync, existsSync, mkdirSync, rmSync, statSync } from 'node:fs';
import { dirname, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const root = fileURLToPath(new URL('.', import.meta.url));

// GitHub Pages serves this repo from a sub-path (/Haoma). CI sets BASE_PATH
// from actions/configure-pages; local dev and root deploys use '/'.
const base = process.env.BASE_PATH || '/';
const site = process.env.PUBLIC_SITE_URL || 'https://v4g4b0nd-0x76.github.io';

/**
 * Content and assets live outside src/ because the Hugo editor owns them.
 * In dev, a change there must invalidate the module-level content index and
 * refresh copies in public/. Without this, editing an article or uploading an
 * image through the editor does nothing until the dev server is restarted.
 */
function watchSources() {
  return {
    name: 'haoma-watch-sources',
    configureServer(server) {
      const contentRoots = ['content', 'data', 'i18n'].map((dir) => join(root, dir));
      const staticRoot = join(root, 'static');
      let restartTimer;

      server.watcher.add([...contentRoots, staticRoot]);

      server.watcher.on('all', (event, rawFile) => {
        const file = resolve(root, rawFile);

        if (contentRoots.some((dir) => file === dir || file.startsWith(dir + sep))) {
          clearTimeout(restartTimer);
          restartTimer = setTimeout(() => server.restart(), 300);
          return;
        }

        if (file !== staticRoot && !file.startsWith(staticRoot + sep)) return;

        const destination = join(root, 'public', relative(staticRoot, file));
        if (event === 'unlink' || event === 'unlinkDir') {
          rmSync(destination, { recursive: true, force: true });
        } else if (existsSync(file) && statSync(file).isFile()) {
          mkdirSync(dirname(destination), { recursive: true });
          cpSync(file, destination);
        }
      });
    },
  };
}

export default defineConfig({
  site,
  base,
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [sitemap()],
  vite: {
    plugins: [watchSources()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  },
});
