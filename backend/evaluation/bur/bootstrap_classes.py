
import re

BOOTSTRAP_CLASSES = {
    # Layout
    "container",
    "container-sm",
    "container-md",
    "container-lg",
    "container-xl",
    "container-xxl",
    "container-fluid",
    "row",
    "col",

    # Buttons
    "btn",
    "btn-primary",
    "btn-secondary",
    "btn-success",
    "btn-danger",
    "btn-warning",
    "btn-info",
    "btn-light",
    "btn-dark",
    "btn-link",
    "btn-outline-primary",
    "btn-outline-secondary",
    "btn-outline-success",
    "btn-outline-danger",
    "btn-outline-warning",
    "btn-outline-info",
    "btn-outline-light",
    "btn-outline-dark",
    "btn-sm",
    "btn-lg",
    "btn-check",
    "btn-group",
    "btn-group-vertical",
    "btn-toolbar",
    "active",
    "disabled",

    # Cards
    "card",
    "card-body",
    "card-title",
    "card-subtitle",
    "card-text",
    "card-link",
    "card-header",
    "card-footer",
    "card-img",
    "card-img-top",
    "card-img-bottom",
    "card-img-overlay",
    "card-group",

    # Forms
    "form-label",
    "form-control",
    "form-control-plaintext",
    "form-control-sm",
    "form-control-lg",
    "form-range",
    "form-select",
    "form-select-sm",
    "form-select-lg",
    "form-text",
    "form-check",
    "form-check-input",
    "form-check-label",
    "form-check-inline",
    "form-switch",
    "form-floating",
    "input-group",
    "input-group-text",
    "input-group-sm",
    "input-group-lg",
    "col-form-label",
    "col-form-label-sm",
    "col-form-label-lg",
    "valid-feedback",
    "invalid-feedback",
    "valid-tooltip",
    "invalid-tooltip",
    "is-valid",
    "is-invalid",

    # Navigation
    "nav",
    "nav-item",
    "nav-link",
    "nav-tabs",
    "nav-pills",
    "nav-fill",
    "nav-justified",

    # Navbar
    "navbar",
    "navbar-brand",
    "navbar-nav",
    "navbar-text",
    "navbar-toggler",
    "navbar-toggler-icon",
    "navbar-collapse",
    "navbar-expand",
    "navbar-expand-sm",
    "navbar-expand-md",
    "navbar-expand-lg",
    "navbar-expand-xl",
    "navbar-expand-xxl",
    "navbar-light",
    "navbar-dark",

    # Dropdown
    "dropdown",
    "dropdown-center",
    "dropup",
    "dropup-center",
    "dropend",
    "dropstart",
    "dropdown-toggle",
    "dropdown-menu",
    "dropdown-menu-start",
    "dropdown-menu-end",
    "dropdown-item",
    "dropdown-divider",
    "dropdown-header",
    "dropdown-item-text",

    # Alerts
    "alert",
    "alert-primary",
    "alert-secondary",
    "alert-success",
    "alert-danger",
    "alert-warning",
    "alert-info",
    "alert-light",
    "alert-dark",
    "alert-link",
    "alert-dismissible",

    # Badges
    "badge",

    # Accordion
    "accordion",
    "accordion-item",
    "accordion-header",
    "accordion-button",
    "accordion-collapse",
    "accordion-body",
    "accordion-flush",

    # Breadcrumb
    "breadcrumb",
    "breadcrumb-item",

    # List group
    "list-group",
    "list-group-item",
    "list-group-item-action",
    "list-group-flush",
    "list-group-numbered",
    "list-group-horizontal",

    # Modal
    "modal",
    "modal-dialog",
    "modal-dialog-centered",
    "modal-dialog-scrollable",
    "modal-content",
    "modal-header",
    "modal-title",
    "modal-body",
    "modal-footer",
    "modal-backdrop",
    "modal-sm",
    "modal-lg",
    "modal-xl",
    "modal-fullscreen",
    "fade",
    "show",

    # Offcanvas
    "offcanvas",
    "offcanvas-start",
    "offcanvas-end",
    "offcanvas-top",
    "offcanvas-bottom",
    "offcanvas-header",
    "offcanvas-title",
    "offcanvas-body",

    # Pagination
    "pagination",
    "pagination-sm",
    "pagination-lg",
    "page-item",
    "page-link",

    # Progress
    "progress",
    "progress-bar",
    "progress-bar-striped",
    "progress-bar-animated",

    # Spinner
    "spinner-border",
    "spinner-border-sm",
    "spinner-grow",
    "spinner-grow-sm",

    # Toast
    "toast",
    "toast-container",
    "toast-header",
    "toast-body",

    # Tooltip / Popover
    "tooltip",
    "tooltip-inner",
    "popover",
    "popover-header",
    "popover-body",

    # Carousel
    "carousel",
    "slide",
    "carousel-inner",
    "carousel-item",
    "carousel-control-prev",
    "carousel-control-next",
    "carousel-control-prev-icon",
    "carousel-control-next-icon",
    "carousel-indicators",
    "carousel-caption",

    # Close button
    "btn-close",

    # Tables
    "table",
    "table-primary",
    "table-secondary",
    "table-success",
    "table-danger",
    "table-warning",
    "table-info",
    "table-light",
    "table-dark",
    "table-striped",
    "table-striped-columns",
    "table-hover",
    "table-active",
    "table-bordered",
    "table-borderless",
    "table-sm",
    "table-responsive",

    # Images / Figures
    "img-fluid",
    "img-thumbnail",
    "figure",
    "figure-img",
    "figure-caption",

    # Typography
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "lead",

    # Helpers
    "clearfix",
    "visually-hidden",
    "visually-hidden-focusable",
    "stretched-link",
    "text-truncate",
    "vr",
    "ratio",
    "ratio-1x1",
    "ratio-4x3",
    "ratio-16x9",
    "ratio-21x9",
    "fixed-top",
    "fixed-bottom",
    "sticky-top",
    "sticky-bottom",

    # Common utility values
    "visible",
    "invisible",
    "overflow-auto",
    "overflow-hidden",
    "overflow-visible",
    "overflow-scroll",
    "user-select-all",
    "user-select-auto",
    "user-select-none",
    "pe-none",
    "pe-auto",
}


# ---------------------------------------------------------------------------
# Bootstrap-generated utility patterns
# ---------------------------------------------------------------------------

BOOTSTRAP_PATTERNS = [
    # Grid columns:
    # col-6, col-md-6, col-lg-auto
    r"^col(?:-(?:sm|md|lg|xl|xxl))?-(?:1[0-2]|[1-9]|auto)$",

    # Row columns:
    # row-cols-2, row-cols-md-4, row-cols-auto
    r"^row-cols(?:-(?:sm|md|lg|xl|xxl))?-(?:[1-6]|auto)$",

    # Offset:
    # offset-2, offset-md-3
    r"^offset(?:-(?:sm|md|lg|xl|xxl))?-(?:0|1[0-1]|[1-9])$",

    # Gutters:
    # g-3, gx-2, gy-md-4
    r"^g[xy]?(?:-(?:sm|md|lg|xl|xxl))?-[0-5]$",

    # Margin / padding (including Bootstrap's logical start/end sides):
    # mt-3, px-2, mb-lg-5, ms-auto
    r"^[mp][trblxyse]?(?:-(?:sm|md|lg|xl|xxl))?-(?:0|1|2|3|4|5|auto)$",

    # Display:
    # d-flex, d-none, d-md-grid
    r"^d(?:-(?:sm|md|lg|xl|xxl))?-(?:none|inline|inline-block|block|grid|inline-grid|table|table-cell|table-row|flex|inline-flex)$",

    # Flex direction:
    r"^flex(?:-(?:sm|md|lg|xl|xxl))?-(?:row|row-reverse|column|column-reverse)$",

    # Flex grow/shrink:
    r"^flex-(?:grow|shrink)-(?:0|1)$",

    # Flex fill:
    r"^flex(?:-(?:sm|md|lg|xl|xxl))?-fill$",

    # Flex wrapping:
    r"^flex(?:-(?:sm|md|lg|xl|xxl))?-(?:wrap|nowrap|wrap-reverse)$",

    # Justify content:
    r"^justify-content(?:-(?:sm|md|lg|xl|xxl))?-(?:start|end|center|between|around|evenly)$",

    # Align items:
    r"^align-items(?:-(?:sm|md|lg|xl|xxl))?-(?:start|end|center|baseline|stretch)$",

    # Align content:
    r"^align-content(?:-(?:sm|md|lg|xl|xxl))?-(?:start|end|center|between|around|stretch)$",

    # Align self:
    r"^align-self(?:-(?:sm|md|lg|xl|xxl))?-(?:auto|start|end|center|baseline|stretch)$",

    # Order:
    r"^order(?:-(?:sm|md|lg|xl|xxl))?-(?:first|last|0|1|2|3|4|5)$",

    # Gap:
    r"^gap(?:-(?:sm|md|lg|xl|xxl))?-[0-5]$",

    # Width / height:
    r"^[wh]-(?:25|50|75|100|auto)$",
    r"^m[wh]-100$",
    r"^min-v[wh]-100$",
    r"^v[wh]-100$",

    # Position:
    r"^position-(?:static|relative|absolute|fixed|sticky)$",

    # Position offsets:
    # top-0, start-50, end-100
    r"^(?:top|bottom|start|end)-(?:0|50|100)$",

    # Translate helpers
    r"^translate-middle(?:-x|-y)?$",

    # Border:
    r"^border(?:-(?:top|end|bottom|start))?$",
    r"^border(?:-(?:top|end|bottom|start))?-0$",
    r"^border-(?:0|1|2|3|4|5)$",

    # Border colors
    r"^border-(?:primary|secondary|success|danger|warning|info|light|dark|white|black)$",
    r"^border-(?:primary|secondary|success|danger|warning|info|light|dark)-subtle$",

    # Rounded
    r"^rounded(?:-(?:top|end|bottom|start|circle|pill))?$",
    r"^rounded-(?:0|1|2|3|4|5)$",

    # Shadows
    r"^shadow(?:-sm|-lg|-none)?$",

    # Opacity
    r"^opacity-(?:0|25|50|75|100)$",

    # Background colors
    r"^bg-(?:primary|secondary|success|danger|warning|info|light|dark|black|white|body|transparent)$",

    # Background subtle colors
    r"^bg-(?:primary|secondary|success|danger|warning|info|light|dark)-subtle$",

    # Background opacity
    r"^bg-opacity-(?:10|25|50|75|100)$",

    # Text alignment
    r"^text(?:-(?:sm|md|lg|xl|xxl))?-(?:start|end|center)$",

    # Text colors
    r"^text-(?:primary|secondary|success|danger|warning|info|light|dark|black|white|body|body-secondary|body-tertiary|muted|black-50|white-50)$",

    # Text emphasis colors
    r"^text-(?:primary|secondary|success|danger|warning|info|light|dark)-emphasis$",

    # Text opacity
    r"^text-opacity-(?:25|50|75|100)$",

    # Font sizes
    r"^fs-[1-6]$",

    # Display headings
    r"^display-[1-6]$",

    # Font weights
    r"^fw-(?:lighter|light|normal|medium|semibold|bold|bolder)$",

    # Font style
    r"^fst-(?:italic|normal)$",

    # Line height
    r"^lh-(?:1|sm|base|lg)$",

    # Text decoration
    r"^text-decoration-(?:none|underline|line-through)$",

    # Text transform
    r"^text-(?:lowercase|uppercase|capitalize)$",

    # Text wrapping / breaking
    r"^text-(?:wrap|nowrap|break)$",

    # Vertical alignment
    r"^align-(?:baseline|top|middle|bottom|text-bottom|text-top)$",

    # Float
    r"^float(?:-(?:sm|md|lg|xl|xxl))?-(?:start|end|none)$",

    # Overflow
    r"^overflow-(?:auto|hidden|visible|scroll)$",

    # Object fit (Bootstrap 5.3)
    r"^object-fit(?:-(?:sm|md|lg|xl|xxl))?-(?:contain|cover|fill|scale|none)$",

    # Z-index utilities (Bootstrap 5.3)
    r"^z-(?:n1|0|1|2|3)$",

    # Link utilities
    r"^link-(?:primary|secondary|success|danger|warning|info|light|dark|body-emphasis)$",
    r"^link-opacity-(?:10|25|50|75|100)$",
    r"^link-underline(?:-opacity)?-(?:0|10|25|50|75|100)$",
    r"^link-offset-[1-3]$",

    # Focus ring (Bootstrap 5.3)
    r"^focus-ring$",
]

# Bootstrap Icons is loaded alongside Bootstrap in the project base template.
# For the BUR, it counts as Bootstrap usage as requested.
BOOTSTRAP_ICON_PATTERN = re.compile(r"^bi(?:-[a-z0-9-]+)?$")


def is_bootstrap_class(class_name: str) -> bool:
    """
    Returns True when a class is recognised as Bootstrap 5.3 or Bootstrap Icons.
    """
    if class_name in BOOTSTRAP_CLASSES:
        return True

    return bool(BOOTSTRAP_ICON_PATTERN.fullmatch(class_name)) or any(
        re.fullmatch(pattern, class_name)
        for pattern in BOOTSTRAP_PATTERNS
    )


if __name__ == "__main__":
    examples = [
        "container",
        "row",
        "col-md-6",
        "mt-3",
        "d-lg-flex",
        "justify-content-between",
        "btn-primary",
        "card-body",
        "rounded-3",
        "object-fit-cover",
        "custom-level-wrapper",
    ]

    for example in examples:
        print(
            f"{example:30} "
            f"{'Bootstrap' if is_bootstrap_class(example) else 'Custom'}"
        )
