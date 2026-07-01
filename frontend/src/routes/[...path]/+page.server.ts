// === FEATURE: cms ===
import { error } from '@sveltejs/kit';
import { PUBLIC_API_URL } from '$env/static/public';
import type { PageServerLoad } from './$types';

interface CmsBlock {
	type: 'richtext' | 'image' | 'html';
	html?: string;
	url?: string;
	caption?: string;
	alt?: string;
}

export interface CmsPage {
	id: number;
	title: string;
	slug: string;
	path: string;
	metaDescription: string;
	regions: {
		main: CmsBlock[];
	};
}

export const load: PageServerLoad = async ({ url }) => {
	const path = url.pathname;

	const res = await fetch(`${PUBLIC_API_URL}/cms/page/?path=${encodeURIComponent(path)}`);

	if (res.status === 404) {
		throw error(404, 'Page not found');
	}

	if (!res.ok) {
		throw error(500, 'Failed to load page');
	}

	const page: CmsPage = await res.json();
	return { page };
};
// === END FEATURE: cms ===
