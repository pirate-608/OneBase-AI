(function () {
    function isExpanded(toggleInput) {
        return (
            toggleInput.checked ||
            toggleInput.classList.contains("md-toggle--indeterminate")
        );
    }

    function initSidebarToggles() {
        var sections = document.querySelectorAll(
            ".md-sidebar--primary .md-nav__item--nested"
        );

        sections.forEach(function (section) {
            var toggleInput = section.querySelector(
                ":scope > input.md-nav__toggle"
            );
            var headerLink = section.querySelector(
                ":scope > label.md-nav__link"
            );

            if (!toggleInput || !headerLink) {
                return;
            }

            if (section.querySelector(".ob-nav-toggle")) {
                return;
            }

            // Keep only sections on active path expanded by default.
            var hasActiveChild = !!section.querySelector(
                ".md-nav a.md-nav__link--active"
            );
            if (!hasActiveChild) {
                toggleInput.classList.remove("md-toggle--indeterminate");
                toggleInput.checked = false;
            }

            var toggleButton = document.createElement("button");
            toggleButton.type = "button";
            toggleButton.className = "ob-nav-toggle";
            toggleButton.setAttribute("aria-label", "Toggle section");
            toggleButton.setAttribute(
                "aria-expanded",
                isExpanded(toggleInput) ? "true" : "false"
            );

            toggleButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();

                if (!toggleInput) {
                    return;
                }

                // Use explicit state to avoid being forced open by
                // Material's indeterminate nav state.
                var expanded = isExpanded(toggleInput);
                toggleInput.classList.remove("md-toggle--indeterminate");
                toggleInput.checked = !expanded;
                toggleInput.dispatchEvent(
                    new Event("change", { bubbles: true })
                );
                toggleButton.setAttribute(
                    "aria-expanded",
                    isExpanded(toggleInput) ? "true" : "false"
                );
            });

            toggleInput.addEventListener("change", function () {
                toggleButton.setAttribute(
                    "aria-expanded",
                    isExpanded(toggleInput) ? "true" : "false"
                );
            });

            section.classList.add("ob-nav-section");
            headerLink.appendChild(toggleButton);
        });
    }

    if (typeof document$ !== "undefined" && document$.subscribe) {
        document$.subscribe(initSidebarToggles);
    } else if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initSidebarToggles);
    } else {
        initSidebarToggles();
    }
})();
