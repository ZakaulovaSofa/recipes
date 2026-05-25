// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'Be cooking',
    tagline: 'Документация онлайн-кулинарной книги',
    favicon: 'img/favicon.ico',

    future: {
        v4: true,
    },

    url: 'https://ZakaulovaSofa.github.io',
    baseUrl: '/recipes/',

    organizationName: 'ZakaulovaSofa',
    projectName: 'recipes',

    onBrokenLinks: 'throw',
    onBrokenMarkdownLinks: 'warn',

    i18n: {
        defaultLocale: 'ru',
        locales: ['ru'],
    },

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: './sidebars.js',
                    routeBasePath: '/',
                    docItemComponent: '@theme/ApiItem',
                    editUrl:
                        'https://github.com/ZakaulovaSofa/recipes/tree/main/docs-site/',
                },

                blog: false,

                theme: {
                    customCss: './src/css/custom.css',
                },
            }),
        ],
    ],

    plugins: [
        [
            'docusaurus-plugin-openapi-docs',
            {
                id: 'openapi',
                docsPluginId: 'classic',
                config: {
                    recipes: {
                        specPath: 'openapi/openapi.yaml',
                        outputDir: 'docs/api/reference',
                        sidebarOptions: {
                            groupPathsBy: 'tag',
                        },
                    },
                },
            },
        ],
    ],

    themes: ['docusaurus-theme-openapi-docs'],

    themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            image: 'img/docusaurus-social-card.jpg',

            navbar: {
                title: 'Be cooking',
                items: [
                    {
                        type: 'docSidebar',
                        sidebarId: 'docs',
                        position: 'left',
                        label: 'Документация',
                    },
                    {
                        href: 'https://github.com/ZakaulovaSofa/recipes',
                        label: 'GitHub',
                        position: 'right',
                    },
                ],
            },

            footer: {
                style: 'dark',
                links: [
                    {
                        title: 'Документация',
                        items: [
                            {
                                label: 'Обзор проекта',
                                to: '/',
                            },
                            {
                                label: 'REST API',
                                to: '/api/overview',
                            },
                            {
                                label: 'База данных',
                                to: '/database/erd',
                            },
                        ],
                    },
                    {
                        title: 'Проект',
                        items: [
                            {
                                label: 'GitHub',
                                href: 'https://github.com/ZakaulovaSofa/recipes',
                            },
                        ],
                    },
                ],
                copyright: `Copyright © ${new Date().getFullYear()} Be cooking.`,
            },

            prism: {
                theme: prismThemes.github,
                darkTheme: prismThemes.dracula,
            },
        }),
};

export default config;