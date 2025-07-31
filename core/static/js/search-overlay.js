function openSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay) overlay.classList.add("show");
}

function closeSearch() {
  const overlay = document.getElementById("searchOverlay");
  if (overlay) overlay.classList.remove("show");
}
