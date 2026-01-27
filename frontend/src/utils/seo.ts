interface MetaTagsConfig {
  title?: string;
  description?: string;
  keywords?: string;
  ogTitle?: string;
  ogDescription?: string;
}

/**
 * Updates document meta tags for SEO optimization.
 * Safely handles SSR environments and creates missing meta tags.
 */
export function updateMetaTags(config: MetaTagsConfig): void {
  // SSR check - exit early if document is not available
  if (typeof document === 'undefined') {
    return;
  }

  // Update document title
  if (config.title) {
    document.title = config.title;
  }

  // Helper function to get or create meta tag
  const getOrCreateMetaTag = (name: string, attribute: 'name' | 'property' = 'name'): HTMLMetaElement => {
    let meta = document.querySelector<HTMLMetaElement>(`meta[${attribute}="${name}"]`);
    
    if (!meta) {
      meta = document.createElement('meta');
      meta.setAttribute(attribute, name);
      document.head.appendChild(meta);
    }
    
    return meta;
  };

  // Update description meta tag
  if (config.description) {
    const descMeta = getOrCreateMetaTag('description');
    descMeta.content = config.description;
  }

  // Update keywords meta tag
  if (config.keywords) {
    const keywordsMeta = getOrCreateMetaTag('keywords');
    keywordsMeta.content = config.keywords;
  }

  // Update og:title meta tag
  if (config.ogTitle) {
    const ogTitleMeta = getOrCreateMetaTag('og:title', 'property');
    ogTitleMeta.content = config.ogTitle;
  }

  // Update og:description meta tag
  if (config.ogDescription) {
    const ogDescMeta = getOrCreateMetaTag('og:description', 'property');
    ogDescMeta.content = config.ogDescription;
  }
}
