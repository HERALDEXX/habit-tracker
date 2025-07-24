// script.js

document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("theme-toggle");
  const tooltip = document.getElementById("theme-tooltip");

  // Set default theme (dark) or load from localStorage
  const userPref = localStorage.getItem("theme") || "dark";
  document.body.classList.toggle("light-theme", userPref === "light");

  const updateTooltipText = () => {
    tooltip.textContent = document.body.classList.contains("light-theme")
      ? "click to switch to dark mode"
      : "click to switch to light mode";
  };

  updateTooltipText();

  toggleBtn.addEventListener("click", () => {
    const isLight = document.body.classList.toggle("light-theme");
    localStorage.setItem("theme", isLight ? "light" : "dark");
    updateTooltipText();
  });

  toggleBtn.addEventListener("mouseenter", () => {
    updateTooltipText();
    tooltip.style.opacity = "1";
    tooltip.style.visibility = "visible";
  });

  toggleBtn.addEventListener("mouseleave", () => {
    tooltip.style.opacity = "0";
    tooltip.style.visibility = "hidden";
  });

  // Animate features on scroll
  const features = document.querySelectorAll(".feature");
  const featureObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = 1;
          entry.target.style.transform = "translateY(0)";
          featureObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  features.forEach((feature) => {
    feature.style.opacity = 0;
    feature.style.transform = "translateY(40px)";
    feature.style.transition = "all 0.6s ease-out";
    featureObserver.observe(feature);
  });
  const feedMessages = [
    "Mobile version coming soon 📱",
    "Built for everyone. Loved by devs ❤️",
    "Works offline — your habits, your device 🔒",
    "Cross-platform magic in one package ✨",
  ];

  const feedTarget = document.getElementById("announcement-feed");
  let feedIndex = 0;
  let charIndex = 0;
  let isDeleting = false;

  function typeFeed() {
    const currentMessage = feedMessages[feedIndex];
    if (!isDeleting && charIndex <= currentMessage.length) {
      feedTarget.textContent = currentMessage.substring(0, charIndex);
      charIndex++;
      setTimeout(typeFeed, 70);
    } else if (isDeleting && charIndex >= 0) {
      feedTarget.textContent = currentMessage.substring(0, charIndex);
      charIndex--;
      setTimeout(typeFeed, 40);
    } else {
      if (!isDeleting) {
        isDeleting = true;
        setTimeout(typeFeed, 1200); // pause before deleting
      } else {
        isDeleting = false;
        feedIndex = (feedIndex + 1) % feedMessages.length;
        setTimeout(typeFeed, 400); // pause before next message
      }
    }
  }

  typeFeed();
});

// Screenshot modal logic
const modal = document.getElementById("screenshot-modal");
const modalImg = document.getElementById("modal-img");
const captionText = document.getElementById("modal-caption");
const closeBtn = document.querySelector(".close-btn");

document.querySelectorAll(".screenshot-wrapper img").forEach((img) => {
  img.addEventListener("click", () => {
    modal.style.display = "block";
    modalImg.src = img.src;
    captionText.textContent = img.dataset.caption || "";
  });
});

closeBtn.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
  }
});

// Auto-update copyright year
document.getElementById("year").textContent = new Date().getFullYear();

// Repeating scroll-based section animation
const scrollObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      } else {
        entry.target.classList.remove("visible");
      }
    });
  },
  { threshold: 0.1 }
);

document.querySelectorAll(".scroll-animate").forEach((el) => {
  scrollObserver.observe(el);
});

document
  .getElementById("download-trigger")
  .addEventListener("click", async () => {
    const drawer = document.getElementById("download-drawer"); // If it's already open, close it

    if (drawer.style.display === "block") {
      drawer.style.display = "none";
      return;
    } // Fetch and populate content if not already loaded

    if (!drawer.dataset.loaded) {
      try {
        const res = await fetch(
          "https://api.github.com/repos/HERALDEXX/habit-tracker/releases/latest"
        );
        const data = await res.json();
        const assets = data.assets;
        const tag = data.tag_name || "";
        const version = tag.replace(/^v/, "");
        const zipURL = `https://github.com/HERALDEXX/habit-tracker/archive/refs/tags/${tag}.zip`;
        const tarURL = `https://github.com/HERALDEXX/habit-tracker/archive/refs/tags/${tag}.tar.gz`;

        const findAsset = (keyword) =>
          assets.find((a) => a.name.toLowerCase().includes(keyword))
            ?.browser_download_url || null;

        const links = {
          windows: findAsset("windows"),
          macos: findAsset("macos"),
          linux: findAsset("linux"),
        };

        const instructionURLs = {
          windows:
            "https://heraldexx.github.io/habit-tracker/setup/windows.txt",
          macos: "https://heraldexx.github.io/habit-tracker/setup/macos.txt",
          linux: "https://heraldexx.github.io/habit-tracker/setup/linux.txt",
        };

        for (const key in links) {
          const binaryBtn = document.getElementById(`download-${key}`);
          const instructionsBtn = document.getElementById(
            `instructions-${key}`
          );

          if (links[key]) {
            if (binaryBtn) {
              binaryBtn.onclick = () => window.open(links[key], "_blank");
            }

            if (instructionsBtn && instructionURLs[key]) {
              instructionsBtn.onclick = () =>
                window.open(instructionURLs[key], "_blank");
            }
          } else {
            if (binaryBtn) {
              binaryBtn.disabled = true;
              binaryBtn.textContent = `${
                key.charAt(0).toUpperCase() + key.slice(1)
              } (Not Available)`;
              binaryBtn.style.opacity = 0.5;
              binaryBtn.style.cursor = "not-allowed";
            }

            if (instructionsBtn) {
              instructionsBtn.style.display = "none";
            }
          }
        } // Set source links

        document.getElementById("source-zip").href = zipURL;
        document.getElementById("source-tar").href = tarURL; // macOS instructions with copy buttons

        drawer.dataset.loaded = true;
      } catch (err) {
        console.error("Failed to fetch release data:", err);
        return;
      }
    } // Finally show drawer (after content is ready)

    drawer.style.display = "block";
  });

document.addEventListener("click", (e) => {
  if (e.target.classList.contains("copy-btn")) {
    const targetId = e.target.dataset.target;
    const codeElement = document.getElementById(targetId);
    if (codeElement) {
      const text = codeElement.textContent.trim();
      navigator.clipboard
        .writeText(text)
        .then(() => {
          e.target.textContent = "✅ Copied!";
          setTimeout(() => (e.target.textContent = "📋"), 1500);
        })
        .catch(() => {
          e.target.textContent = "❌ Error";
          setTimeout(() => (e.target.textContent = "📋"), 1500);
        });
    }
  }
});

// Updated dropdown toggle logic
document.addEventListener("click", function (e) {
  const isToggle = e.target.closest(".dropdown-toggle");
  const openDropdown = document.querySelector(".dropdown.show"); // Check if the click is inside the dropdown menu

  const insideDropdownMenu = e.target.closest(".dropdown-menu");

  if (openDropdown && !isToggle && !insideDropdownMenu) {
    openDropdown.classList.remove("show");
  }

  if (isToggle) {
    const dropdown = isToggle.closest(".dropdown");
    dropdown.classList.toggle("show");
  }
});

// UX: Close dropdown when a link inside it is clicked
document.querySelectorAll(".dropdown-menu a").forEach((link) => {
  link.addEventListener("click", () => {
    const dropdown = link.closest(".dropdown");
    if (dropdown) {
      dropdown.classList.remove("show");
    }
  });
});
