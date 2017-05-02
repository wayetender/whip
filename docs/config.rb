#-------------------------------------------------------------------------
# Configure Middleman
#-------------------------------------------------------------------------

set :base_url, "http://whip.services/priv/"

activate :hashicorp do |h|
  h.releases_enabled = false
  h.github_slug = "wayetender/whip"
  h.website_root = "docs"
end

helpers do
  def sidebar_current(expected)
    current = current_page.data.sidebar_current || ""
    if current.start_with?(expected)
      return " class=\"active\""
    else
      return ""
    end
  end

  # Get the title for the page.
  #
  # @param [Middleman::Page] page
  #
  # @return [String]
  def title_for(page)
    if page && page.data.page_title
      return "#{page.data.page_title} - Whip"
    end

    "Whip Contract Monitor"
  end
end
