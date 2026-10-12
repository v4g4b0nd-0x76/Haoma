---
title: "Writing guide"
tagline: "Layouts, sliders, notes and media for pages"
wide: true
grade: guide
reviewed: 2026-10-12
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
