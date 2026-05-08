import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

const SITE_NAME = 'Studienkolleg Aachen – Way2Germany';
const SITE_URL = 'https://www.stk-aachen.de';

export default function SEOHead({ titleKey, descKey, path, noIndex = false }) {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'de';
  const altLang = lang === 'de' ? 'en' : 'de';

  const title = t(titleKey);
  const description = t(descKey);
  const fullTitle = `${title} | ${SITE_NAME}`;
  const canonical = `${SITE_URL}${path || '/'}`;
  const altUrl = `${SITE_URL}${path || '/'}?lng=${altLang}`;

  return (
    <Helmet>
      <html lang={lang} />
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      {noIndex && <meta name="robots" content="noindex, nofollow" />}
      {!noIndex && <link rel="canonical" href={canonical} />}
      {!noIndex && <link rel="alternate" hrefLang={lang} href={canonical} />}
      {!noIndex && <link rel="alternate" hrefLang={altLang} href={altUrl} />}
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonical} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:locale" content={lang === 'de' ? 'de_DE' : 'en_US'} />
      <meta name="twitter:card" content="summary" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
    </Helmet>
  );
}
