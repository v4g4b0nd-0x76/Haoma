---
title: "Writing guide"
tagline: "Layouts, sliders, notes and media for pages"
wide: true
grade: guide
reviewed: 2026-10-12
draft: true
---
This page is both documentation and a live demo of every layout tool. Open it in the editor to see the source.

## Text beside an image (2/3 + 1/3)

{{% grid cols="2fr 1fr" gap="2rem" %}}
{{% col %}}
The main text takes two thirds of the width. It can contain **Markdown**, lists and links. Hover over this {{< note text="Notes appear above the highlighted text on hover, focus or tap." >}}highlighted phrase{{< /note >}} to see a note.

Wikipedia-style pages usually place the figure on the right (or the left in right-to-left languages).
{{% /col %}}
{{% col %}}
{{< fig src="img/iranian.svg" caption="Animated SVG banner" note="Images can carry hover notes too." >}}
{{% /col %}}
{{% /grid %}}

## Infobox that text wraps around

{{% infobox side="end" w="32%" title="Quick facts" %}}
**Type:** guide page

**Tool:** infobox shortcode
{{% /infobox %}}

An infobox floats to one side and the paragraph wraps around it, like the summary box on a Wikipedia article. It collapses to full width on phones. Add more paragraphs and the text keeps flowing next to the box until the next heading.

Keep writing here to see the wrap. The box ends where the next heading begins.

## Slider with images, GIFs and video

{{< slider autoplay="6" ratio="16/9" >}}
img/norse.svg | Norse banner
img/iranian.svg | Iranian banner
img/base.svg | General banner
{{< /slider >}}

## Rows and columns grid

{{% grid cols="1fr 1fr 1fr" gap="1.5rem" %}}
{{% col span="3" %}}
### A header row spanning all three columns
{{% /col %}}
{{% col %}}
First column.
{{% /col %}}
{{% col %}}
Second column.
{{% /col %}}
{{% col %}}
Third column.
{{% /col %}}
{{% /grid %}}

## GIF or video that plays when scrolled into view

Use `{{</* scrollplay src="img/media/clip.gif" caption="..." */>}}`. GIFs start when at least 60% visible and restart on re-entry. MP4 and WebM videos play muted and pause when out of view.

## Map with pins and a travel route

Maps are drawn from real coastlines in this site's own style. Pins carry labels and hover notes; the optional route draws a dashed line joining the pins in order.

{{< map id="map-guide" src="img/maps/persia.svg" height="440px" route="auto" caption="Demo map of the Iranian plateau — pins are placed as percentages of the map box" >}}
region points="9.1,17.9 15.0,13.1 20.8,11.4 26.6,14.3 30.5,21.5 32.2,31.0 31.2,40.5 27.3,48.8 22.1,51.2 16.3,47.6 11.7,40.5 9.1,31.0 8.5,23.8" label="Media" note="The north-western highlands, home of Ecbatana (Hamadan)." color="gold" /
region points="24.0,47.6 29.2,45.2 34.4,44.1 39.6,42.3 44.2,42.9 48.1,50.0 50.0,59.5 49.4,69.0 47.4,77.3 41.6,82.1 35.1,82.7 29.2,77.3 25.3,70.2 23.4,61.9 23.4,53.6" label="Persia" note="The southern heartland of Fars, where Persepolis stands." href="/cultures/iranian/" color="gold" /
region points="39.6,13.1 45.5,9.6 51.9,8.4 59.1,9.6 64.9,15.5 68.8,23.8 69.5,33.4 65.6,40.5 59.7,42.9 53.2,39.3 47.4,34.5 42.2,29.8 39.0,23.8 39.0,17.9" label="Parthia" note="The north-eastern march, later the realm of the Parthians." color="gold" /
region points="59.1,27.4 64.3,23.8 70.1,22.7 76.0,25.0 80.5,31.0 82.4,40.5 81.8,50.0 77.9,57.1 72.7,59.5 66.9,57.1 62.3,51.2 59.1,44.1 58.4,35.7" label="Aria" note="The eastern highlands around Herat." color="gold" /
region points="67.5,6.0 73.4,3.6 79.2,3.6 85.0,6.0 89.6,10.8 90.6,17.9 89.6,22.7 84.4,25.0 78.6,25.0 72.7,22.7 68.8,17.9 67.5,12.0" label="Transoxiana" note="The plain beyond the Oxus (Amu Darya), the eastern edge of the Iranian world." color="gold" /
pin x="36.9%" y="25.3%" label="Damavand" note="First pin — the route starts here" color="fire" /
pin x="21.7%" y="32.5%" label="Ecbatana" note="Second stop" /
pin x="20.8%" y="48.8%" label="Susa" note="Third stop" color="silver" /
pin x="36.3%" y="62.6%" label="Persepolis" note="Route end" color="blood" /
{{< /map >}}
