"""Gallery of every Web Awesome component wrapped by spaday-webawesome."""

from __future__ import annotations

import io
import keyword
import textwrap
import tokenize

from spaday import SetProp, by_id, element
from spaday.backends.starlette import serve

from . import components as wa, package

DEMO_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360' viewBox='0 0 640 360'%3E"
    "%3Cdefs%3E%3ClinearGradient id='g' x2='1' y2='1'%3E%3Cstop stop-color='%232563eb'/%3E"
    "%3Cstop offset='1' stop-color='%237c3aed'/%3E%3C/linearGradient%3E%3C/defs%3E"
    "%3Crect width='640' height='360' rx='32' fill='url(%23g)'/%3E"
    "%3Ccircle cx='500' cy='80' r='110' fill='%23ffffff' opacity='.14'/%3E"
    "%3Ctext x='48' y='190' fill='white' font-family='system-ui' font-size='46' font-weight='700'%3EWeb Awesome%3C/text%3E"
    "%3Ctext x='50' y='235' fill='white' font-family='system-ui' font-size='22'%3Espaday component gallery%3C/text%3E%3C/svg%3E"
)

COMPONENT_SNIPPETS: list[str] = []


def _snippet(names: str, body: str) -> str:
    source = f"from spaday_webawesome import {names}\n\n{textwrap.dedent(body).strip()}\n"
    COMPONENT_SNIPPETS.append(source)
    return source


def _offsets(source: str) -> list[int]:
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _code(source: str):
    """Render a small, dependency-free highlighted Python code block."""
    offsets = _offsets(source)
    children = []
    cursor = 0
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.ENDMARKER:
            continue
        start = offsets[token.start[0] - 1] + token.start[1]
        end = offsets[token.end[0] - 1] + token.end[1]
        if start > cursor:
            children.append(source[cursor:start])
        token_class = None
        if token.type == tokenize.NAME and keyword.iskeyword(token.string):
            token_class = "keyword"
        elif token.type == tokenize.STRING:
            token_class = "string"
        elif token.type == tokenize.NUMBER:
            token_class = "number"
        elif token.type == tokenize.COMMENT:
            token_class = "comment"
        elif token.type == tokenize.OP:
            token_class = "operator"
        children.append(element("span", class_=f"token-{token_class}").text(token.string) if token_class else token.string)
        cursor = end
    if cursor < len(source):
        children.append(source[cursor:])
    return element("pre", element("code", *children), class_="code-block")


def _demo(title: str, description: str, source: str, preview):
    return wa.WaCard(
        element(
            "header",
            element("div", element("h3").text(title), element("p").text(description)),
            wa.WaCopyButton(value=source, copy_label=f"Copy {title} example", tooltip="copy"),
            class_="demo-heading",
        ),
        element("div", preview, class_="preview"),
        _code(source),
        appearance="outlined",
        class_="gallery-card",
    )


def _section(section_id: str, title: str, description: str, *cards):
    return element(
        "section",
        element("header", element("p", class_="section-label").text(section_id.upper()), element("h2").text(title), element("p").text(description)),
        element("div", *cards, class_="gallery-grid"),
        id=section_id,
        class_="gallery-section",
    )


actions = _section(
    "actions",
    "Actions",
    "Buttons and menus for common user actions.",
    _demo(
        "Buttons",
        "Buttons can be grouped and styled by intent.",
        _snippet(
            "WaButton, WaButtonGroup",
            """
            buttons = WaButtonGroup(
                WaButton(variant="brand").text("Save"),
                WaButton(appearance="outlined").text("Cancel"),
                label="Document actions",
            )
            """,
        ),
        wa.WaButtonGroup(
            wa.WaButton(variant="brand").text("Save"),
            wa.WaButton(appearance="outlined").text("Cancel"),
            label="Document actions",
        ),
    ),
    _demo(
        "Copy button",
        "Copy a known value with built-in feedback.",
        _snippet("WaCopyButton", 'copy = WaCopyButton(value="pip install spaday-webawesome")'),
        wa.WaCopyButton(value="pip install spaday-webawesome"),
    ),
    _demo(
        "Dropdown",
        "Place menu items behind a compact trigger.",
        _snippet(
            "WaButton, WaDropdown, WaDropdownItem",
            """
            menu = WaDropdown(
                WaDropdownItem(value="rename").text("Rename"),
                WaDropdownItem(value="archive").text("Archive"),
            ).child_in("trigger", WaButton(with_caret=True).text("Actions"))
            """,
        ),
        wa.WaDropdown(
            wa.WaDropdownItem(value="rename").text("Rename"),
            wa.WaDropdownItem(value="archive").text("Archive"),
        ).child_in("trigger", wa.WaButton(with_caret=True).text("Actions")),
    ),
)

forms = _section(
    "forms",
    "Forms",
    "Inputs, selectors, and validation-ready controls.",
    _demo(
        "Checkbox group",
        "Group related binary choices under one label.",
        _snippet(
            "WaCheckbox, WaCheckboxGroup",
            """
            choices = WaCheckboxGroup(
                WaCheckbox(value="email", checked=True).text("Email"),
                WaCheckbox(value="push").text("Push"),
                label="Notifications",
                with_label=True,
            )
            """,
        ),
        wa.WaCheckboxGroup(
            wa.WaCheckbox(value="email", checked=True).text("Email"),
            wa.WaCheckbox(value="push").text("Push"),
            label="Notifications",
            with_label=True,
        ),
    ),
    _demo(
        "Color picker",
        "Select colors in common CSS formats.",
        _snippet("WaColorPicker", 'picker = WaColorPicker(label="Accent", value="#2563eb", format="hex", with_label=True)'),
        wa.WaColorPicker(label="Accent", value="#2563eb", format="hex", with_label=True),
    ),
    _demo(
        "Input",
        "Collect a single line of typed data.",
        _snippet("WaInput", 'name = WaInput(label="Project name", value="Apollo", with_clear=True)'),
        wa.WaInput(label="Project name", value="Apollo", with_clear=True),
    ),
    _demo(
        "Known date",
        "Enter a date through locale-aware segments.",
        _snippet("WaKnownDate", 'date = WaKnownDate(label="Launch date", value="2026-09-11", with_label=True)'),
        wa.WaKnownDate(label="Launch date", value="2026-09-11", with_label=True),
    ),
    _demo(
        "Number input",
        "Edit numeric values with stepper controls.",
        _snippet("WaNumberInput", 'quantity = WaNumberInput(label="Quantity", value="12", min=0, max=100)'),
        wa.WaNumberInput(label="Quantity", value="12", min=0, max=100),
    ),
    _demo(
        "OTP input",
        "Collect fixed-length verification codes.",
        _snippet("WaOtpInput", 'code = WaOtpInput(label="Verification code", length=6, type="numeric")'),
        wa.WaOtpInput(label="Verification code", length=6, type="numeric"),
    ),
    _demo(
        "Radio group",
        "Choose one option from a visible set.",
        _snippet(
            "WaRadio, WaRadioGroup",
            """
            plan = WaRadioGroup(
                WaRadio(value="starter").text("Starter"),
                WaRadio(value="pro").text("Pro"),
                label="Plan",
                value="starter",
                with_label=True,
            )
            """,
        ),
        wa.WaRadioGroup(
            wa.WaRadio(value="starter").text("Starter"),
            wa.WaRadio(value="pro").text("Pro"),
            label="Plan",
            value="starter",
            with_label=True,
        ),
    ),
    _demo(
        "Rating",
        "Capture or display a numeric rating.",
        _snippet("WaRating", 'rating = WaRating(label="Quality", value=4, max=5)'),
        wa.WaRating(label="Quality", value=4, max=5),
    ),
    _demo(
        "Select",
        "Choose from a compact option list.",
        _snippet(
            "WaOption, WaSelect",
            """
            region = WaSelect(
                WaOption(value="east").text("US East"),
                WaOption(value="west").text("US West"),
                label="Region",
                value="east",
            )
            """,
        ),
        wa.WaSelect(
            wa.WaOption(value="east").text("US East"),
            wa.WaOption(value="west").text("US West"),
            label="Region",
            value="east",
        ),
    ),
    _demo(
        "Slider",
        "Pick a value from a bounded range.",
        _snippet("WaSlider", 'volume = WaSlider(label="Volume", min=0, max=100, value=60, with_tooltip=True)'),
        wa.WaSlider(label="Volume", min=0, max=100, value=60, with_tooltip=True),
    ),
    _demo(
        "Switch",
        "Toggle a setting that takes effect immediately.",
        _snippet("WaSwitch", 'enabled = WaSwitch(checked=True).text("Automatic updates")'),
        wa.WaSwitch(checked=True).text("Automatic updates"),
    ),
    _demo(
        "Textarea",
        "Collect longer free-form text.",
        _snippet("WaTextarea", 'notes = WaTextarea(label="Notes", rows=3, value="Ready for review.")'),
        wa.WaTextarea(label="Notes", rows=3, value="Ready for review."),
    ),
    _demo(
        "Time input",
        "Enter time through locale-aware segments.",
        _snippet("WaTimeInput", 'start = WaTimeInput(label="Start time", value="09:30", with_label=True)'),
        wa.WaTimeInput(label="Start time", value="09:30", with_label=True),
    ),
)

layout = _section(
    "layout",
    "Layout",
    "Containers that structure and progressively reveal content.",
    _demo(
        "Accordion",
        "Group related disclosure panels.",
        _snippet(
            "WaAccordion, WaAccordionItem",
            """
            faq = WaAccordion(
                WaAccordionItem("Components are typed Python objects.", label="What is Spaday?", expanded=True),
                WaAccordionItem("Yes. This page runs in Pyodide.", label="Does it run in a browser?"),
            )
            """,
        ),
        wa.WaAccordion(
            wa.WaAccordionItem("Components are typed Python objects.", label="What is Spaday?", expanded=True),
            wa.WaAccordionItem("Yes. This page runs in Pyodide.", label="Does it run in a browser?"),
        ),
    ),
    _demo(
        "Card",
        "Group related content and actions.",
        _snippet(
            "WaButton, WaCard",
            """
            card = (
                WaCard("Deployment is healthy.", appearance="outlined")
                .child_in("header", "Production")
                .child_in("footer", WaButton(size="small").text("View details"))
            )
            """,
        ),
        wa.WaCard("Deployment is healthy.", appearance="filled")
        .child_in("header", "Production")
        .child_in("footer", wa.WaButton(size="small").text("View details")),
    ),
    _demo(
        "Details",
        "Reveal optional content inline.",
        _snippet("WaDetails", 'details = WaDetails("Advanced configuration", summary="Show details")'),
        wa.WaDetails("Advanced configuration", summary="Show details"),
    ),
    _demo(
        "Dialog",
        "Present a focused modal task.",
        _snippet(
            "WaButton, WaDialog",
            """
            dialog = WaDialog("Changes have been saved.", id="saved-dialog", label="Saved")
            trigger = WaButton().text("Open dialog").on("click", SetProp(by_id("saved-dialog"), "open", True))
            """,
        ),
        element(
            "div",
            wa.WaButton().text("Open dialog").on("click", SetProp(by_id("saved-dialog"), "open", True)),
            wa.WaDialog("Changes have been saved.", id="saved-dialog", label="Saved", light_dismiss=True),
        ),
    ),
    _demo(
        "Divider",
        "Separate adjacent groups visually.",
        _snippet("WaDivider", "divider = WaDivider()"),
        element("div", element("span").text("Above"), wa.WaDivider(), element("span").text("Below"), class_="stack"),
    ),
    _demo(
        "Drawer",
        "Expose secondary content from an edge.",
        _snippet(
            "WaButton, WaDrawer",
            """
            drawer = WaDrawer("Filters go here.", id="filters", label="Filters", light_dismiss=True)
            trigger = WaButton().text("Open drawer").on("click", SetProp(by_id("filters"), "open", True))
            """,
        ),
        element(
            "div",
            wa.WaButton().text("Open drawer").on("click", SetProp(by_id("gallery-drawer"), "open", True)),
            wa.WaDrawer("Filters go here.", id="gallery-drawer", label="Filters", light_dismiss=True),
        ),
    ),
    _demo(
        "Page",
        "Compose application regions into a responsive shell.",
        _snippet(
            "WaPage",
            """
            page = (
                WaPage(view="desktop")
                .child_in("header", "Header")
                .child_in("navigation", "Navigation")
                .child("Main content")
            )
            """,
        ),
        wa.WaPage(view="desktop", class_="mini-page").child_in("header", "Header").child_in("navigation", "Navigation").child("Main content"),
    ),
    _demo(
        "Scroller",
        "Make horizontal overflow discoverable.",
        _snippet(
            "WaScroller",
            'scroller = WaScroller(*[f"Item {number}" for number in range(1, 9)], orientation="horizontal")',
        ),
        wa.WaScroller(*(element("span", class_="scroll-item").text(f"Item {number}") for number in range(1, 9)), orientation="horizontal"),
    ),
    _demo(
        "Split panel",
        "Resize two neighboring content regions.",
        _snippet(
            "WaSplitPanel",
            """
            split = (
                WaSplitPanel(position=45)
                .child_in("start", "Navigation")
                .child_in("end", "Content")
            )
            """,
        ),
        wa.WaSplitPanel(position=45, class_="split-demo").child_in("start", "Navigation").child_in("end", "Content"),
    ),
)

navigation = _section(
    "navigation",
    "Navigation",
    "Wayfinding for pages, collections, and hierarchies.",
    _demo(
        "Breadcrumb",
        "Show location within a hierarchy.",
        _snippet(
            "WaBreadcrumb, WaBreadcrumbItem",
            """
            trail = WaBreadcrumb(
                WaBreadcrumbItem(href="/").text("Home"),
                WaBreadcrumbItem(href="/components").text("Components"),
                WaBreadcrumbItem().text("Gallery"),
            )
            """,
        ),
        wa.WaBreadcrumb(
            wa.WaBreadcrumbItem(href="#").text("Home"),
            wa.WaBreadcrumbItem(href="#navigation").text("Components"),
            wa.WaBreadcrumbItem().text("Gallery"),
        ),
    ),
    _demo(
        "Pagination",
        "Move through a larger result set.",
        _snippet("WaPagination", 'pages = WaPagination(total=120, page_size=10, page=3, with_summary=True, label="Results")'),
        wa.WaPagination(total=120, page_size=10, page=3, with_summary=True, label="Results"),
    ),
    _demo(
        "Tabs",
        "Switch among related panels.",
        _snippet(
            "WaTab, WaTabGroup, WaTabPanel",
            """
            tabs = (
                WaTabGroup(WaTabPanel("Overview content", name="overview"), active="overview")
                .child_in("nav", WaTab(panel="overview").text("Overview"))
                .child_in("nav", WaTab(panel="activity").text("Activity"))
                .child(WaTabPanel("Activity content", name="activity"))
            )
            """,
        ),
        wa.WaTabGroup(wa.WaTabPanel("Overview content", name="gallery-overview"), active="gallery-overview")
        .child_in("nav", wa.WaTab(panel="gallery-overview").text("Overview"))
        .child_in("nav", wa.WaTab(panel="gallery-activity").text("Activity"))
        .child(wa.WaTabPanel("Activity content", name="gallery-activity")),
    ),
    _demo(
        "Tree",
        "Navigate nested, selectable items.",
        _snippet(
            "WaTree, WaTreeItem",
            """
            tree = WaTree(
                WaTreeItem(
                    "spaday_webawesome",
                    WaTreeItem().text("gallery.py"),
                    WaTreeItem().text("example.py"),
                    expanded=True,
                ),
                selection="single",
            )
            """,
        ),
        wa.WaTree(
            wa.WaTreeItem(
                "spaday_webawesome",
                wa.WaTreeItem().text("gallery.py"),
                wa.WaTreeItem().text("example.py"),
                expanded=True,
            ),
            selection="single",
        ),
    ),
)

feedback = _section(
    "feedback",
    "Feedback",
    "Status, progress, transient messages, and contextual help.",
    _demo(
        "Badge and tag",
        "Compact status and category labels.",
        _snippet(
            "WaBadge, WaTag",
            """
            status = WaBadge(variant="success", pill=True).text("Healthy")
            label = WaTag(variant="brand", with_remove=True).text("Python")
            """,
        ),
        element(
            "div",
            wa.WaBadge(variant="success", pill=True).text("Healthy"),
            wa.WaTag(variant="brand", with_remove=True).text("Python"),
            class_="inline-preview",
        ),
    ),
    _demo(
        "Callout",
        "Keep an important message in the page flow.",
        _snippet("WaCallout", 'notice = WaCallout("All systems operational", variant="success", appearance="outlined")'),
        wa.WaCallout("All systems operational", variant="success", appearance="outlined"),
    ),
    _demo(
        "Progress and loading",
        "Show determinate and indeterminate work or placeholders.",
        _snippet(
            "WaProgressBar, WaProgressRing, WaSkeleton, WaSpinner",
            """
            bar = WaProgressBar(value=65, label="Build progress")
            ring = WaProgressRing("65%", value=65, label="Build progress")
            skeleton = WaSkeleton(effect="sheen")
            spinner = WaSpinner()
            """,
        ),
        element(
            "div",
            wa.WaProgressBar(value=65, label="Build progress"),
            element("div", wa.WaProgressRing("65%", value=65, label="Build progress"), wa.WaSpinner(), class_="inline-preview"),
            wa.WaSkeleton(effect="sheen", class_="skeleton-demo"),
            class_="stack",
        ),
    ),
    _demo(
        "Toast",
        "Display a short, non-blocking notification.",
        _snippet(
            "WaToast, WaToastItem",
            """
            toasts = WaToast(
                WaToastItem("Settings saved", variant="success", duration=0),
                placement="bottom-end",
            )
            """,
        ),
        wa.WaToast(wa.WaToastItem("Settings saved", variant="success", duration=0), placement="bottom-end"),
    ),
    _demo(
        "Tooltip",
        "Explain a control on hover or focus.",
        _snippet(
            "WaButton, WaTooltip",
            'trigger = WaButton(id="help-trigger").text("Hover me")\ntip = WaTooltip("Contextual help", for_="help-trigger", placement="top")',
        ),
        element(
            "div",
            wa.WaButton(id="gallery-tooltip-trigger").text("Hover me"),
            wa.WaTooltip("Contextual help", for_="gallery-tooltip-trigger", placement="top"),
        ),
    ),
)

media = _section(
    "media",
    "Media",
    "Images, icons, comparisons, rich text, and embedded content.",
    _demo(
        "Animated image",
        "Provide accessible play and pause controls for motion.",
        _snippet("WaAnimatedImage", 'image = WaAnimatedImage(src="animation.gif", alt="Animated product preview")'),
        wa.WaAnimatedImage(src=DEMO_IMAGE, alt="Web Awesome gallery preview", class_="media-demo"),
    ),
    _demo(
        "Avatar",
        "Represent a person or object with initials or an image.",
        _snippet("WaAvatar", 'avatar = WaAvatar(initials="WA", label="Web Awesome", shape="rounded")'),
        wa.WaAvatar(initials="WA", label="Web Awesome", shape="rounded"),
    ),
    _demo(
        "Carousel",
        "Browse a sequence of content slides.",
        _snippet(
            "WaCarousel, WaCarouselItem",
            """
            carousel = WaCarousel(
                WaCarouselItem("First slide"),
                WaCarouselItem("Second slide"),
                navigation=True,
                pagination=True,
            )
            """,
        ),
        wa.WaCarousel(
            wa.WaCarouselItem(element("div", class_="slide slide-one").text("First slide")),
            wa.WaCarouselItem(element("div", class_="slide slide-two").text("Second slide")),
            navigation=True,
            pagination=True,
        ),
    ),
    _demo(
        "Comparison",
        "Reveal two versions with a draggable divider.",
        _snippet(
            "WaComparison",
            """
            comparison = (
                WaComparison(position=50)
                .child_in("before", before_image)
                .child_in("after", after_image)
            )
            """,
        ),
        wa.WaComparison(position=50, class_="comparison-demo")
        .child_in("before", element("div", class_="comparison-side before").text("Before"))
        .child_in("after", element("div", class_="comparison-side after").text("After")),
    ),
    _demo(
        "Icon",
        "Render a named Font Awesome or custom icon.",
        _snippet("WaIcon", 'icon = WaIcon(name="star", label="Featured")'),
        wa.WaIcon(name="star", label="Featured", class_="icon-demo"),
    ),
    _demo(
        "Markdown",
        "Render Markdown content in the browser.",
        _snippet("WaMarkdown", 'content = WaMarkdown("## Release notes\\n\\n- Faster\\n- Smaller")'),
        wa.WaMarkdown("## Release notes\n\n- Faster\n- Smaller"),
    ),
    _demo(
        "QR code",
        "Encode a short value into a scannable image.",
        _snippet("WaQrCode", 'qr = WaQrCode(value="https://spaday.dev", label="Open Spaday", size=144)'),
        wa.WaQrCode(value="https://github.com/1kbgz/spaday", label="Open Spaday", size=144),
    ),
    _demo(
        "Zoomable frame",
        "Embed content with zoom and pan controls.",
        _snippet("WaZoomableFrame", 'frame = WaZoomableFrame(srcdoc="<h1>Preview</h1>", zoom=1)'),
        wa.WaZoomableFrame(
            srcdoc="<style>body{font:16px system-ui;margin:0;padding:2rem;background:#dbeafe;color:#172033}h1{margin:0}</style><h1>Embedded preview</h1>",
            zoom=1,
            class_="frame-demo",
        ),
    ),
)

helpers = _section(
    "helpers",
    "Helpers",
    "Declarative wrappers around browser formatting, positioning, and observation APIs.",
    _demo(
        "Animation",
        "Apply a named Web Animation preset.",
        _snippet("WaAnimation", 'animation = WaAnimation(WaBadge().text("New"), name="pulse", play=True, duration=1200)'),
        wa.WaAnimation(wa.WaBadge().text("New"), name="pulse", play=True, duration=1200, iterations=3),
    ),
    _demo(
        "Format values",
        "Use the browser locale to format bytes, dates, and numbers.",
        _snippet(
            "WaFormatBytes, WaFormatDate, WaFormatNumber",
            """
            size = WaFormatBytes(value=1536000)
            date = WaFormatDate(date="2026-09-11", month="long", day="numeric", year="numeric")
            price = WaFormatNumber(value=1299.5, type="currency", currency="USD")
            """,
        ),
        element(
            "dl",
            element("div", element("dt").text("Size"), element("dd", wa.WaFormatBytes(value=1536000))),
            element(
                "div", element("dt").text("Date"), element("dd", wa.WaFormatDate(date="2026-09-11", month="long", day="numeric", year="numeric"))
            ),
            element("div", element("dt").text("Price"), element("dd", wa.WaFormatNumber(value=1299.5, type="currency", currency="USD"))),
            class_="format-list",
        ),
    ),
    _demo(
        "Include",
        "Fetch and insert an HTML fragment.",
        _snippet("WaInclude", 'fragment = WaInclude(src="/partials/status.html", mode="same-origin")'),
        wa.WaInclude(src="data:text/html,%3Cstrong%3EIncluded%20content%3C/strong%3E"),
    ),
    _demo(
        "Intersection observer",
        "Add a class when content enters the viewport.",
        _snippet(
            "WaIntersectionObserver",
            'observed = WaIntersectionObserver("Visible content", intersect_class="is-visible", once=True)',
        ),
        wa.WaIntersectionObserver(element("div", class_="observer-box").text("I am in the viewport"), intersect_class="is-visible", once=True),
    ),
    _demo(
        "Mutation observer",
        "Emit events when wrapped content changes.",
        _snippet("WaMutationObserver", 'observed = WaMutationObserver("Watched content", child_list=True, char_data=True)'),
        wa.WaMutationObserver(element("div", class_="observer-box").text("Watched content"), child_list=True, char_data=True),
    ),
    _demo(
        "Popover",
        "Anchor rich contextual content to a trigger.",
        _snippet(
            "WaButton, WaPopover",
            """
            trigger = WaButton(id="profile-trigger").text("Profile")
            popover = WaPopover("Signed in as Ada", for_="profile-trigger")
            """,
        ),
        element(
            "div",
            wa.WaButton(id="profile-trigger").text("Profile"),
            wa.WaPopover("Signed in as Ada", for_="profile-trigger"),
        ),
    ),
    _demo(
        "Popup",
        "Position one element relative to another.",
        _snippet(
            "WaButton, WaPopup",
            """
            popup = (
                WaPopup("Positioned content", active=True, placement="bottom")
                .child_in("anchor", WaButton().text("Anchor"))
            )
            """,
        ),
        wa.WaPopup(element("span", class_="popup-content").text("Positioned content"), active=True, placement="bottom", distance=8).child_in(
            "anchor", wa.WaButton().text("Anchor")
        ),
    ),
    _demo(
        "Random content",
        "Select child content randomly or sequentially.",
        _snippet(
            "WaRandomContent",
            'message = WaRandomContent("Build", "Create", "Ship", items=1, mode="sequence")',
        ),
        wa.WaRandomContent("Build", "Create", "Ship", items=1, mode="sequence"),
    ),
    _demo(
        "Relative time",
        "Keep human-readable dates synchronized with now.",
        _snippet("WaRelativeTime", 'updated = WaRelativeTime(date="2026-09-11T12:00:00Z", numeric="auto")'),
        wa.WaRelativeTime(date="2026-09-11T12:00:00Z", numeric="auto"),
    ),
    _demo(
        "Resize observer",
        "Emit events when wrapped content changes size.",
        _snippet("WaResizeObserver", 'observed = WaResizeObserver("Resize the browser to update me")'),
        wa.WaResizeObserver(element("div", class_="observer-box").text("Resize the browser to update me")),
    ),
)

page = element(
    "main",
    element(
        "header",
        element("p", class_="eyebrow").text("SPADAY · WEB AWESOME"),
        element("h1").text("Component gallery"),
        element("p", class_="lede").text("Every free Web Awesome component currently wrapped by spaday-webawesome, with runnable Python."),
        element(
            "nav",
            *(
                element("a", href=f"#{name}").text(label)
                for name, label in [
                    ("actions", "Actions"),
                    ("forms", "Forms"),
                    ("layout", "Layout"),
                    ("navigation", "Navigation"),
                    ("feedback", "Feedback"),
                    ("media", "Media"),
                    ("helpers", "Helpers"),
                ]
            ),
            aria_label="Gallery sections",
            class_="section-nav",
        ),
        class_="hero",
    ),
    actions,
    forms,
    layout,
    navigation,
    feedback,
    media,
    helpers,
    element("footer").text(f"Generated components: {len(wa.__all__)} Web Awesome elements · Python runs locally in Pyodide"),
    class_="gallery-page",
)

styles = """
<style>
  :root { color-scheme: light; }
  html { scroll-behavior: smooth; }
  body { margin: 0; background: #f8fafc; color: #172033; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
  .gallery-page { box-sizing: border-box; width: min(100%, 92rem); margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
  .hero { padding: 2rem 0 1rem; }
  .eyebrow, .section-label { margin: 0; color: #2563eb; font-size: .72rem; font-weight: 800; letter-spacing: .16em; }
  h1 { margin: .35rem 0 0; font-size: clamp(2.4rem, 6vw, 4.75rem); letter-spacing: -.055em; line-height: .98; }
  .lede { max-width: 48rem; margin: 1rem 0 1.5rem; color: #64748b; font-size: 1.08rem; line-height: 1.6; }
  .section-nav { display: flex; flex-wrap: wrap; gap: .5rem; }
  .section-nav a { padding: .45rem .75rem; border: 1px solid #cbd5e1; border-radius: 999px; color: #334155; text-decoration: none; background: white; }
  .section-nav a:hover { border-color: #2563eb; color: #1d4ed8; }
  .gallery-section { scroll-margin-top: 4rem; padding: 3rem 0 1rem; }
  .gallery-section > header { max-width: 44rem; margin-bottom: 1.25rem; }
  .gallery-section h2 { margin: .3rem 0 .4rem; font-size: 2rem; letter-spacing: -.03em; }
  .gallery-section > header > p:last-child { margin: 0; color: #64748b; }
  .gallery-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 26rem), 1fr)); gap: 1rem; align-items: start; }
  .gallery-card { display: block; min-width: 0; --wa-border-radius-l: 1rem; background: white; }
  .demo-heading { display: flex; align-items: start; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
  .demo-heading h3 { margin: 0; font-size: 1.05rem; }
  .demo-heading p { margin: .3rem 0 0; color: #64748b; font-size: .88rem; line-height: 1.45; }
  .preview { box-sizing: border-box; min-height: 8.5rem; margin-bottom: 1rem; padding: 1.25rem; border: 1px solid #e2e8f0; border-radius: .75rem; background: #f8fafc; overflow: auto; }
  .preview > * { max-width: 100%; }
  .code-block { box-sizing: border-box; max-height: 18rem; margin: 0; padding: 1rem; overflow: auto; border-radius: .75rem; color: #dbeafe;
    background: #172033; font: .78rem/1.6 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; tab-size: 4; white-space: pre; }
  .token-keyword { color: #c4b5fd; } .token-string { color: #86efac; } .token-number { color: #fcd34d; }
  .token-comment { color: #94a3b8; font-style: italic; } .token-operator { color: #7dd3fc; }
  .inline-preview { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; }
  .stack { display: grid; gap: .75rem; }
  .media-demo { display: block; width: min(100%, 24rem); border-radius: .6rem; overflow: hidden; }
  .slide { display: grid; min-height: 10rem; place-items: center; border-radius: .6rem; color: white; font-size: 1.25rem; font-weight: 700; }
  .slide-one { background: linear-gradient(135deg, #2563eb, #60a5fa); } .slide-two { background: linear-gradient(135deg, #7c3aed, #c084fc); }
  .comparison-demo { display: block; height: 10rem; } .comparison-side { display: grid; width: 100%; height: 10rem; place-items: center; color: white; font-weight: 800; }
  .comparison-side.before { background: #2563eb; } .comparison-side.after { background: #7c3aed; }
  .icon-demo { font-size: 2.5rem; color: #2563eb; }
  .frame-demo { display: block; height: 11rem; }
  .mini-page { display: block; height: 12rem; border: 1px solid #cbd5e1; border-radius: .5rem; overflow: hidden; }
  .mini-page::part(header), .mini-page::part(navigation), .mini-page::part(main) { padding: .75rem; }
  .scroll-item { display: inline-block; min-width: 7rem; margin-right: .5rem; padding: .75rem; border-radius: .5rem; background: #dbeafe; text-align: center; }
  .split-demo { display: block; height: 9rem; } .split-demo::part(start), .split-demo::part(end) { display: grid; place-items: center; padding: 1rem; }
  .skeleton-demo { display: block; width: 100%; height: 2.5rem; }
  .format-list { display: grid; gap: .5rem; margin: 0; } .format-list div { display: grid; grid-template-columns: 5rem 1fr; }
  .format-list dt { color: #64748b; } .format-list dd { margin: 0; font-weight: 700; }
  .helper-placeholder, .observer-box, .popup-content { display: inline-block; padding: .7rem .85rem; border: 1px dashed #94a3b8; border-radius: .5rem; background: white; }
  footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid #cbd5e1; color: #64748b; font-size: .85rem; }
  @media (max-width: 600px) { .gallery-page { padding-inline: .75rem; } .gallery-section { padding-top: 2rem; } .preview { padding: .9rem; } }
</style>
"""

app = serve(page, packages=[package], head=styles, title="spaday-webawesome gallery")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8013)
