# Farmers' Almanac — honest integration notes

**Researched 2026-11-27. No content was copied or redistributed.**

## Two distinct publications

| Name | Publisher | Site |
|---|---|---|
| Farmers' Almanac | Almanac Publishing Co. | https://www.farmersalmanac.com/ |
| The Old Farmer's Almanac | Yankee Publishing Inc. | https://www.almanac.com/ |

They are different publications with different editors and content. Don't conflate them.

## API availability (verified live)

- `/api` on both domains → **404**. No documented public JSON API found.
- `farmersalmanac.com/feed` → live RSS (title "Farmers' Almanac – Plan Your Day. Grow Your Life.", updated Nov 2026).
- `almanac.com/gardening/planting-calendar` → live page: "2026 Planting Calendar by ZIP Code" with frost-date and garden-resource sections.
- Both home pages and the gardening/weather sections return 200.

## Terms (why we don't scrape)

The Farmers' Almanac terms of use state that the site's content is copyrighted and that you may not "copy, download, reproduce, modify, publish, redistribute, retransmit, publicly display, publicly perform or create derivative works from the content" without permission from the publisher. That means: **no copying their tables, forecasts, or text into our repo, data files, or app.**

## What we integrate instead

1. **Citations** — `garden_os.almanac.SOURCES` is a source registry with publisher, URL and licence note. Links only; no republished content.
2. **User-entered seasonal context** — `SeasonalContext` holds a frost-free window the *user* transcribes from a source they consulted, together with the source label/URL. It rejects anything not explicitly user-entered.
3. **Informational status** — `status(date)` says whether a date is inside the user-entered window. It is never a planting instruction.

## On accuracy

Both almanacs publish long-range weather predictions and planting calendars, but no source we checked provides a published, independently verified accuracy metric for those predictions. We therefore describe them as **widely used reference publications**, not as "highly accurate" in a measured sense. Treat their forecasts as reference material; validate planting dates against your local Extension office.

## What would change this

A written licence/API agreement from either publisher would allow a real adapter with attribution. Until then: cite, link, and let users enter dates themselves.

© 2026 PCMedicalist — All Rights Reserved
