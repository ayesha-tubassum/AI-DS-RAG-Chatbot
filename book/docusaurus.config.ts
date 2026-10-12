import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

function normalizeFrontMatterTitles(fileContent: string): string {
  const endMarker = fileContent.match(/^---\r?\n[\s\S]*?\r?\n---/);

  if (!endMarker) {
    return fileContent;
  }

  const frontMatter = endMarker[0].replace(
    /^(title:\s*)(?!['"])(.+:\s+.+)$/m,
    (_match, key: string, title: string) => `${key}${JSON.stringify(title.trim())}`,
  );

  return frontMatter + fileContent.slice(endMarker[0].length);
}

const config: Config = {
  title: 'AI & Data Science',
  tagline: 'A clear, practical introduction to intelligent systems and the data behind them.',
  url: 'https://example.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  future: {v4: true},
  customFields: {
    // Override at build time with: BOOK_API_URL=https://... npm run build
    apiUrl: process.env.BOOK_API_URL ?? 'http://localhost:8000',
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  markdown: {
    parseFrontMatter: async ({filePath, fileContent, defaultParseFrontMatter}) =>
      defaultParseFrontMatter({
        filePath,
        fileContent: normalizeFrontMatterTitles(fileContent),
      }),
  },
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          showLastUpdateTime: false,
          showLastUpdateAuthor: false,
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      } satisfies Preset.Options,
    ],
  ],
  themeConfig: {
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'AI & Data Science',
      items: [
        {
          to: '/module-01-python-foundations/variables-data-types',
          label: 'Start reading',
          position: 'left',
        },
        {
          type: 'docSidebar',
          sidebarId: 'bookSidebar',
          label: 'Contents',
          position: 'left',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'The book',
          items: [
            {
              label: 'Start reading',
              to: '/module-01-python-foundations/variables-data-types',
            },
            {
              label: 'Module 01: Python Foundations',
              to: '/module-01-python-foundations/variables-data-types',
            },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} AI & Data Science.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
