// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const site = 'https://zen-mcp.github.io/browser';
const base = '/browser/';

// https://astro.build/config
export default defineConfig({
	site,
	base,
	trailingSlash: 'always',
	integrations: [
		starlight({
			title: 'Zen Browser MCP',
			description: 'Zen Browser MCP is a browser automation server that allows you to automate browser actions using MCP.',
			logo: {
				src: './src/assets/logo.svg',
				alt: 'Zen Browser MCP',
			},
			favicon: '/favicon.svg',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/zen-mcp/browser' },
				{ icon: 'linkedin', label: 'LinkedIn', href: 'https://www.linkedin.com/in/zenkiet/' },
			],
			editLink: {
				baseUrl: 'https://github.com/zen-mcp/browser/edit/main/docs/',
			},
			lastUpdated: true,
			sidebar: [
				{ label: 'Home', link: '/' },
				{ label: 'Features', link: '/features/' },
				{ label: 'Tools', link: '/tools/' },
				{ label: 'Configuration', link: '/configuration/' },
				{ label: 'Use cases', link: '/use-cases/' },
				{ label: 'Release process', link: '/release/' },
			],
			components: {
				Header: './src/components/Header.astro',
			},
		}),
	],
});
