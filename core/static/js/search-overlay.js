function openSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay) overlay.classList.add("show"); // Prevent background scrolling
}


function closeSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay) overlay.classList.remove("show"); // Restore background scrolling
}


