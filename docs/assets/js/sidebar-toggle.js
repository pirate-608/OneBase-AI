(function () {
    function initSidebarToggles() {
        var sections = document.querySelectorAll(
            ".md-sidebar--primary .md-nav__item--section"
        );

        sections.forEach(function (section) {
            var toggleInput = section.querySelector("input.md-toggle");
            var headerLink = section.querySelector(":scope > .md-nav__link");

            if (!toggleInput || !headerLink) {
                return;
            }

            if (section.querySelector(".ob-nav-toggle")) {
                return;
            }

            var toggleButton = document.createElement("button");
            toggleButton.type = "button";
            toggleButton.className = "ob-nav-toggle";
            toggleButton.setAttribute("aria-label", "Toggle section");
            toggleButton.setAttribute(
                "aria-expanded",
                toggleInput.checked ? "true" : "false"
            );

            toggleButton.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                toggleInput.checked = !toggleInput.checked;
                toggleButton.setAttribute(
                    "aria-expanded",
                    toggleInput.checked ? "true" : "false"
                );
            });

            toggleInput.addEventListener("change", function () {
                toggleButton.setAttribute(
                    "aria-expanded",
                    toggleInput.checked ? "true" : "false"
                );
            });

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
