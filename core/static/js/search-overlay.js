function openSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay){ overlay.classList.add("show");
  document.body.style.overflow = "hidden"; // Prevent background scrolling
}
}

function closeSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay){ overlay.classList.remove("show");
  document.body.style.overflow = "auto"; // Restore background scrolling
}
}
