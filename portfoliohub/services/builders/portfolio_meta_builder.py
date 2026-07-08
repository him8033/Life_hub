class PortfolioMetaBuilder:

    @staticmethod
    def build(portfolio):

        return {
            "portfolio_id":
                portfolio.portfolio_id,

            "title":
                portfolio.title,

            "slug":
                portfolio.slug,

            "custom_domain":
                portfolio.custom_domain,

            "seo_title":
                portfolio.seo_title,

            "seo_description":
                portfolio.seo_description,

            "hero_title":
                portfolio.hero_title,

            "hero_subtitle":
                portfolio.hero_subtitle,

            "is_public":
                portfolio.is_public,

            "view_count":
                portfolio.view_count,
        }
